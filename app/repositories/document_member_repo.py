from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_member import DocumentMember
from app.schemas.document_member import DocumentMemberCreate, DocumentMemberUpdate
from app.repositories.base import BaseRepository

class DocumentMemberRepository(BaseRepository[DocumentMember, DocumentMemberCreate, DocumentMemberUpdate]):
    async def get_members_by_document(self, db: AsyncSession, *, document_id: UUID) -> List[DocumentMember]:
        result = await db.execute(
            select(DocumentMember)
            .filter(DocumentMember.document_id == document_id)
        )
        return list(result.scalars().all())

    async def get_by_doc_and_user(self, db: AsyncSession, *, document_id: UUID, user_id: UUID) -> Optional[DocumentMember]:
        result = await db.execute(
            select(DocumentMember)
            .filter(
                DocumentMember.document_id == document_id,
                DocumentMember.user_id == user_id
            )
        )
        return result.scalars().first()

document_member_repo = DocumentMemberRepository(DocumentMember)
