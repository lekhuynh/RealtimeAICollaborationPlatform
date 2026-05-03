from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class AIResultBase(BaseModel):
    result: str
    scope: str

class AIResultCreate(AIResultBase):
    request_id: UUID

class AIResultResponse(AIResultBase):
    id: UUID
    request_id: UUID
    created_at: datetime

    class Config:
        from_attributes = True
