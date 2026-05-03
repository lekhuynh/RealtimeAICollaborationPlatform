from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_version import DocumentVersion
from app.schemas.document_version import DocumentVersionCreate
from app.repositories.document_version_repo import document_version_repo

class DocumentVersionService:
    async def create_version(self, db: AsyncSession, *, document_id: UUID, content: str, created_by: UUID) -> DocumentVersion:
        latest = await document_version_repo.get_latest_version(db, document_id=document_id)
        new_version_num = (latest.version + 1) if latest else 1
        
        db_version = DocumentVersion(
            document_id=document_id,
            content=content,
            version=new_version_num,
            created_by=created_by
        )
        db.add(db_version)
        await db.commit()
        await db.refresh(db_version)
        return db_version

    async def get_versions(self, db: AsyncSession, *, document_id: UUID) -> List[DocumentVersion]:
        return await document_version_repo.get_versions_by_document(db, document_id=document_id)

    async def get_version(self, db: AsyncSession, *, id: UUID) -> Optional[DocumentVersion]:
        return await document_version_repo.get(db, id=id)

document_version_service = DocumentVersionService()
