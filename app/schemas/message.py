from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class MessageBase(BaseModel):
    content: str = Field(..., min_length=1)
    type: str = "text"

class MessageCreate(MessageBase):
    document_id: UUID

class MessageResponse(MessageBase):
    id: UUID
    document_id: UUID
    user_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
