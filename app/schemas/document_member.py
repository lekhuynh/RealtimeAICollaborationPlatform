from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from datetime import datetime
from app.models.enums import DocumentRole

class DocumentMemberBase(BaseModel):
    role: DocumentRole = DocumentRole.VIEWER

class DocumentMemberCreate(DocumentMemberBase):
    user_id: UUID
    document_id: UUID

class DocumentMemberUpdate(BaseModel):
    role: DocumentRole

class DocumentMemberResponse(DocumentMemberBase):
    id: UUID
    document_id: UUID
    user_id: UUID
    joined_at: datetime

    class Config:
        from_attributes = True

class MemberInvite(BaseModel):
    document_id: UUID
    email: str
    role: DocumentRole
