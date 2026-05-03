from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.db.session import get_db
from app.core.permissions import require_admin
from app.models.user import User
from app.models.document import Document
from app.schemas.user import UserResponse
from app.schemas.document import DocumentResponse
from app.services.user_service import user_service
from app.services.document_service import document_service

router = APIRouter()

@router.get("/users", response_model=List[UserResponse])
async def get_all_users(
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    result = await db.execute(select(User))
    return list(result.scalars().all())

@router.put("/users/{user_id}/ban")
async def ban_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    # This assumes a 'is_banned' or 'is_active' field exists in User model, which doesn't natively,
    # so we might simulate it or raise 501 Not Implemented
    raise HTTPException(status_code=501, detail="Ban user not fully implemented yet")

@router.get("/documents", response_model=List[DocumentResponse])
async def get_all_documents(
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    result = await db.execute(select(Document))
    return list(result.scalars().all())

@router.delete("/documents/{document_id}")
async def delete_any_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db), 
    admin: User = Depends(require_admin)
):
    doc = await document_service.delete_document(db, id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return {"status": "success"}
