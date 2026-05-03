from pydantic import BaseModel
from uuid import UUID
from datetime import datetime

class DocumentVersionBase(BaseModel):
    content: str
    version: int

class DocumentVersionCreate(DocumentVersionBase):
    document_id: UUID

class DocumentVersionResponse(DocumentVersionBase):
    id: UUID
    document_id: UUID
    created_by: UUID
    created_at: datetime

    class Config:
        from_attributes = True
