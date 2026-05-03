from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.document_version import DocumentVersion
from app.schemas.document_version import DocumentVersionCreate
from app.repositories.base import BaseRepository
from pydantic import BaseModel

class DocumentVersionUpdate(BaseModel):
    pass # Versions are usually immutable, we might not update them

class DocumentVersionRepository(BaseRepository[DocumentVersion, DocumentVersionCreate, DocumentVersionUpdate]):
    async def get_versions_by_document(self, db: AsyncSession, *, document_id: UUID) -> List[DocumentVersion]:
        result = await db.execute(
            select(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
        )
        return list(result.scalars().all())
        
    async def get_latest_version(self, db: AsyncSession, *, document_id: UUID) -> Optional[DocumentVersion]:
        result = await db.execute(
            select(DocumentVersion)
            .filter(DocumentVersion.document_id == document_id)
            .order_by(DocumentVersion.version.desc())
            .limit(1)
        )
        return result.scalars().first()

document_version_repo = DocumentVersionRepository(DocumentVersion)
