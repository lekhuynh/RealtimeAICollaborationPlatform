from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.models.document import Document
from app.models.document_member import DocumentMember
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.repositories.base import BaseRepository

class DocumentRepository(BaseRepository[Document, DocumentCreate, DocumentUpdate]):
    async def get_by_owner(self, db: AsyncSession, *, owner_id: UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        result = await db.execute(
            select(Document)
            .filter(Document.owner_id == owner_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_with_members(self, db: AsyncSession, *, id: UUID) -> Optional[Document]:
        result = await db.execute(
            select(Document)
            .options(selectinload(Document.members))
            .filter(Document.id == id)
        )
        return result.scalars().first()
        
    async def get_accessible_documents(self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        # Tự join với DocumentMember để lấy các document mà user được phép truy cập
        result = await db.execute(
            select(Document)
            .join(DocumentMember, Document.id == DocumentMember.document_id)
            .filter(DocumentMember.user_id == user_id)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_shared_documents(self, db: AsyncSession, *, user_id: UUID, skip: int = 0, limit: int = 100) -> List[Document]:
        from app.models.enums import DocumentRole
        result = await db.execute(
            select(Document)
            .join(DocumentMember, Document.id == DocumentMember.document_id)
            .filter(DocumentMember.user_id == user_id, DocumentMember.role != DocumentRole.OWNER)
            .order_by(Document.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        return list(result.scalars().all())

document_repo = DocumentRepository(Document)
