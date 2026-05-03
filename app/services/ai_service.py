from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.ai_request import AIRequest
from app.models.ai_result import AIResult
from app.schemas.ai_request import AIRequestCreate
from app.schemas.ai_result import AIResultCreate
from app.repositories.ai_repo import ai_request_repo, ai_result_repo

class AIService:
    async def create_request(self, db: AsyncSession, *, obj_in: AIRequestCreate, user_id: UUID) -> AIRequest:
        db_req = AIRequest(
            user_id=user_id,
            document_id=obj_in.document_id,
            type=obj_in.type,
            status="pending"
        )
        db.add(db_req)
        await db.commit()
        await db.refresh(db_req)
        # Tại đây có thể trigger Celery/Background task
        return db_req

    async def get_document_requests(self, db: AsyncSession, *, document_id: UUID) -> List[AIRequest]:
        return await ai_request_repo.get_by_document(db, document_id=document_id)

    async def save_result(self, db: AsyncSession, *, obj_in: AIResultCreate) -> AIResult:
        return await ai_result_repo.create(db, obj_in=obj_in)

    async def get_result(self, db: AsyncSession, *, request_id: UUID) -> Optional[AIResult]:
        return await ai_result_repo.get_by_request(db, request_id=request_id)

ai_service = AIService()
