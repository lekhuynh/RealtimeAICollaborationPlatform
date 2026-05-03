from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.utils.security import get_current_user
from app.core.permissions import RequireDocPermission
from app.models.enums import DocumentPermission
from app.models.user import User
from app.schemas.ai_request import AIRequestCreate, AIRequestResponse
from app.schemas.ai_result import AIResultResponse
from app.services.ai_service import ai_service
from app.services.document_member_service import document_member_service

router = APIRouter()

from app.worker.celery_app import celery_app

@router.post("/request", response_model=AIRequestResponse)
async def create_ai_request(
    req_in: AIRequestCreate, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Manual permission check since document_id is in body
    role = await document_member_service.check_user_role(db, document_id=req_in.document_id, user_id=current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="Not enough permissions to access this document")
        
    # Save the pending request to DB
    db_request = await ai_service.create_request(db, obj_in=req_in, user_id=current_user.id)
    
    # Push to Celery Worker Queue
    celery_app.send_task(
        "process_ai_document",
        kwargs={
            "document_id": str(req_in.document_id),
            "request_id": str(db_request.id),
            "task_type": req_in.type,
            "prompt": req_in.prompt
        }
    )
    
    return db_request

@router.get("/{request_id}", response_model=AIRequestResponse)
async def get_ai_request(
    request_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    # Retrieve request to find document_id
    # Note: Requires get_request method in ai_service, falling back to result check
    result = await ai_service.get_result(db, request_id=request_id)
    if not result:
        raise HTTPException(status_code=404, detail="Request/Result not found")
        
    role = await document_member_service.check_user_role(db, document_id=result.document_id, user_id=current_user.id)
    if not role:
        raise HTTPException(status_code=403, detail="Not enough permissions")
        
    return result # Or request if service supports it
