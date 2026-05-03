from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document import Document
from app.models.document_member import DocumentMember
from app.models.enums import DocumentRole
from app.schemas.document import DocumentCreate, DocumentUpdate
from app.repositories.document_repo import document_repo
from app.repositories.document_member_repo import document_member_repo

class DocumentService:
    async def create_document(self, db: AsyncSession, *, obj_in: DocumentCreate, owner_id: UUID) -> Document:
        # 1. Tạo document
        doc_data = obj_in.model_dump()
        db_doc = Document(**doc_data, owner_id=owner_id)
        db.add(db_doc)
        await db.commit()
        await db.refresh(db_doc)

        # 2. Tạo member (Owner)
        owner_member = DocumentMember(
            document_id=db_doc.id,
            user_id=owner_id,
            role=DocumentRole.OWNER
        )
        db.add(owner_member)
        await db.commit()
        
        return db_doc

    async def get_document(self, db: AsyncSession, id: UUID) -> Optional[Document]:
        return await document_repo.get(db, id=id)

    async def get_user_documents(self, db: AsyncSession, user_id: UUID) -> List[Document]:
        return await document_repo.get_accessible_documents(db, user_id=user_id)

    async def update_document(self, db: AsyncSession, *, db_obj: Document, obj_in: DocumentUpdate) -> Document:
        return await document_repo.update(db, db_obj=db_obj, obj_in=obj_in)

    async def delete_document(self, db: AsyncSession, *, id: UUID) -> Optional[Document]:
        return await document_repo.remove(db, id=id)

    async def get_shared_documents(self, db: AsyncSession, user_id: UUID) -> List[Document]:
        return await document_repo.get_shared_documents(db, user_id=user_id)

document_service = DocumentService()
