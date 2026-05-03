from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime

class DocumentBase(BaseModel):
    title: str = Field(..., min_length=1)
    content: Optional[str] = None

class DocumentCreate(DocumentBase):
    pass

class DocumentUpdate(BaseModel):
    title: Optional[str] = None
    content: Optional[str] = None

class DocumentResponse(DocumentBase):
    id: UUID
    owner_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
