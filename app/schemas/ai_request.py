from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime

class AIRequestBase(BaseModel):
    type: str
    status: str = "pending"

class AIRequestCreate(BaseModel):
    document_id: UUID
    user_id: UUID
    type: str
    prompt: Optional[str] = None

class AIRequestUpdate(BaseModel):
    status: str

class AIRequestResponse(AIRequestBase):
    id: UUID
    user_id: UUID
    document_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
