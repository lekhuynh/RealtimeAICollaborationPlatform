from typing import List
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.repositories.base import BaseRepository
from pydantic import BaseModel

class MessageUpdate(BaseModel):
    pass

class MessageRepository(BaseRepository[Message, MessageCreate, MessageUpdate]):
    async def get_messages_by_document(self, db: AsyncSession, *, document_id: UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        result = await db.execute(
            select(Message)
            .filter(Message.document_id == document_id)
            .order_by(Message.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        # return ascending for chat view
        messages = list(result.scalars().all())
        messages.reverse()
        return messages

message_repo = MessageRepository(Message)
