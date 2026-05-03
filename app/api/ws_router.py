from uuid import UUID
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.core.security import decode_token
from app.services.user_service import user_service
from app.services.document_member_service import document_member_service
from app.websocket.manager import manager
from app.services.message_service import message_service
from app.schemas.message import MessageCreate
import json

router = APIRouter()

async def get_ws_user(token: str, db: AsyncSession):
    try:
        payload = decode_token(token)
        user_id = payload.get("sub")
        if not user_id:
            return None
        return await user_service.get_user(db, user_id=user_id)
    except:
        return None

@router.websocket("/chat/{document_id}")
async def websocket_endpoint(
    websocket: WebSocket, 
    document_id: UUID,
    token: str = Query(...),
    db: AsyncSession = Depends(get_db)
):
    user = await get_ws_user(token, db)
    if not user:
        print(f"WS Reject: User not found for token {token}")
        await websocket.close(code=1008)
        return
        
    role = await document_member_service.check_user_role(db, document_id=document_id, user_id=user.id)
    if not role:
        print(f"WS Reject: Role not found for doc {document_id} and user {user.id}")
        await websocket.close(code=1008)
        return
        
    await manager.connect(websocket, str(document_id))
    try:
        while True:
            data = await websocket.receive_text()
            try:
                event = json.loads(data)
                event_type = event.get("type")
                
                if event_type == "send_message":
                    content = event.get("content")
                    if content:
                        msg_in = MessageCreate(document_id=document_id, content=content, type="text")
                        db_msg = await message_service.create_message(db, obj_in=msg_in, user_id=user.id)
                        
                        broadcast_data = {
                            "type": "new_message",
                            "message_id": str(db_msg.id),
                            "content": db_msg.content,
                            "user_id": str(user.id),
                            "user_name": user.full_name
                        }
                        await manager.broadcast(json.dumps(broadcast_data), str(document_id))
                        
                elif event_type == "ai_request":
                    from app.worker.tasks.ai_tasks import process_ai_document
                    from app.repositories.ai_repo import ai_request_repo
                    from app.schemas.ai_request import AIRequestCreate
                    
                    prompt = event.get("prompt")
                    task_type = event.get("task_type", "chat")
                    
                    # 1. Lưu yêu cầu vào DB để lấy request_id
                    req_in = AIRequestCreate(
                        document_id=document_id,
                        user_id=user.id,
                        task_type=task_type,
                        prompt=prompt
                    )
                    db_req = await ai_request_repo.create(db, obj_in=req_in)
                    await db.commit()
                    
                    # 2. Gửi xác nhận về cho client kèm request_id
                    ack_data = {
                        "type": "ai_processing",
                        "request_id": str(db_req.id),
                        "prompt": prompt,
                        "status": "queued"
                    }
                    await manager.broadcast(json.dumps(ack_data), str(document_id))
                    
                    # 3. KÍCH HOẠT CELERY WORKER!
                    process_ai_document.delay(
                        document_id=str(document_id),
                        request_id=str(db_req.id),
                        task_type=task_type,
                        prompt=prompt
                    )
                    
            except json.JSONDecodeError:
                pass
                
    except WebSocketDisconnect:
        manager.disconnect(websocket, str(document_id))
