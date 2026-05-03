from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_member import DocumentMember
from app.schemas.document_member import DocumentMemberCreate, DocumentMemberUpdate
from app.repositories.document_member_repo import document_member_repo

class DocumentMemberService:
    async def add_member(self, db: AsyncSession, *, obj_in: DocumentMemberCreate) -> DocumentMember:
        return await document_member_repo.create(db, obj_in=obj_in)

    async def update_member_role(self, db: AsyncSession, *, document_id: UUID, user_id: UUID, obj_in: DocumentMemberUpdate) -> Optional[DocumentMember]:
        member = await document_member_repo.get_by_doc_and_user(db, document_id=document_id, user_id=user_id)
        if member:
            return await document_member_repo.update(db, db_obj=member, obj_in=obj_in)
        return None

    async def remove_member(self, db: AsyncSession, *, document_id: UUID, user_id: UUID) -> bool:
        member = await document_member_repo.get_by_doc_and_user(db, document_id=document_id, user_id=user_id)
        if member:
            await document_member_repo.remove(db, id=member.id)
            return True
        return False
        
    async def get_members(self, db: AsyncSession, *, document_id: UUID) -> List[DocumentMember]:
        return await document_member_repo.get_members_by_document(db, document_id=document_id)
        
    async def check_user_role(self, db: AsyncSession, *, document_id: UUID, user_id: UUID) -> Optional[str]:
        member = await document_member_repo.get_by_doc_and_user(db, document_id=document_id, user_id=user_id)
        if member:
            return member.role
        return None

document_member_service = DocumentMemberService()
