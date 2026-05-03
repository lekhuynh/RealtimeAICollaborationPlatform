from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_request import AIRequest
from app.models.ai_result import AIResult
from app.schemas.ai_request import AIRequestCreate, AIRequestUpdate
from app.schemas.ai_result import AIResultCreate
from app.repositories.base import BaseRepository
from pydantic import BaseModel

class AIResultUpdate(BaseModel):
    pass

class AIRequestRepository(BaseRepository[AIRequest, AIRequestCreate, AIRequestUpdate]):
    async def get_by_document(self, db: AsyncSession, *, document_id: UUID) -> List[AIRequest]:
        result = await db.execute(
            select(AIRequest)
            .filter(AIRequest.document_id == document_id)
            .order_by(AIRequest.created_at.desc())
        )
        return list(result.scalars().all())

class AIResultRepository(BaseRepository[AIResult, AIResultCreate, AIResultUpdate]):
    async def get_by_request(self, db: AsyncSession, *, request_id: UUID) -> Optional[AIResult]:
        result = await db.execute(
            select(AIResult)
            .filter(AIResult.request_id == request_id)
        )
        return result.scalars().first()

ai_request_repo = AIRequestRepository(AIRequest)
ai_result_repo = AIResultRepository(AIResult)
