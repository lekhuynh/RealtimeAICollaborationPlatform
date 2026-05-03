from uuid import UUID
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.message import Message
from app.schemas.message import MessageCreate
from app.repositories.message_repo import message_repo

class MessageService:
    async def create_message(self, db: AsyncSession, *, obj_in: MessageCreate, user_id: UUID) -> Message:
        db_message = Message(
            document_id=obj_in.document_id,
            user_id=user_id,
            content=obj_in.content,
            type=obj_in.type
        )
        db.add(db_message)
        await db.commit()
        await db.refresh(db_message)
        return db_message

    async def get_document_messages(self, db: AsyncSession, *, document_id: UUID, skip: int = 0, limit: int = 100) -> List[Message]:
        return await message_repo.get_messages_by_document(db, document_id=document_id, skip=skip, limit=limit)

    async def get_message(self, db: AsyncSession, *, message_id: UUID) -> Optional[Message]:
        return await message_repo.get(db, id=message_id)

    async def delete_message(self, db: AsyncSession, *, message_id: UUID) -> bool:
        message = await message_repo.get(db, id=message_id)
        if message:
            await message_repo.remove(db, id=message_id)
            return True
        return False

message_service = MessageService()
