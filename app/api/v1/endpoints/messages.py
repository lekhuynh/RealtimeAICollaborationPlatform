from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.utils.security import get_current_user
from app.models.user import User
from app.services.message_service import message_service
from app.services.document_member_service import document_member_service
from app.models.enums import DocumentRole

router = APIRouter()

@router.get("/")
async def get_messages(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Check if user is a member of the document
    role = await document_member_service.check_user_role(db, document_id=document_id, user_id=current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="Not a member of this document")
        
    return await message_service.get_document_messages(db, document_id=document_id)

@router.delete("/{message_id}")
async def delete_message(
    message_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    msg = await message_service.get_message(db, message_id=message_id)
    if not msg:
        raise HTTPException(status_code=404, detail="Message not found")
        
    role = await document_member_service.check_user_role(db, document_id=msg.document_id, user_id=current_user.id)
    
    if msg.user_id != current_user.id and role != DocumentRole.OWNER:
        raise HTTPException(status_code=403, detail="You can only delete your own messages")
        
    await message_service.delete_message(db, message_id=message_id)
    return {"status": "success"}
