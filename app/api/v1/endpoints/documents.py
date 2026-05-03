from typing import List
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.utils.security import get_current_user
from app.core.permissions import RequireDocPermission
from app.models.enums import DocumentPermission
from app.models.user import User
from app.models.document_member import DocumentMember
from app.schemas.document import DocumentCreate, DocumentResponse, DocumentUpdate
from app.schemas.message import MessageCreate, MessageResponse
from app.schemas.document_member import DocumentMemberCreate, DocumentMemberResponse, DocumentMemberUpdate
from app.schemas.document_version import DocumentVersionResponse
from app.services.document_service import document_service
from app.services.message_service import message_service
from app.services.document_member_service import document_member_service
from app.services.document_version_service import document_version_service
from app.schemas.ai_result import AIResultResponse
from app.services.ai_service import ai_service

router = APIRouter()

@router.post("/", response_model=DocumentResponse)
async def create_document(doc_in: DocumentCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await document_service.create_document(db, obj_in=doc_in, owner_id=current_user.id)

@router.get("/", response_model=List[DocumentResponse])
async def get_my_documents(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await document_service.get_user_documents(db, user_id=current_user.id)

@router.get("/shared", response_model=List[DocumentResponse])
async def get_shared_documents(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await document_service.get_shared_documents(db, user_id=current_user.id)

@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.READ_DOCUMENT))
):
    doc = await document_service.get_document(db, id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.put("/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    doc_in: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.EDIT_DOCUMENT))
):
    doc = await document_service.get_document(db, id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    # KIỂM TRA QUYỀN ĐỔI TÊN: Chỉ Owner mới được đổi title
    if doc_in.title is not None and doc_in.title != doc.title:
        if doc.owner_id != current_user.id:
            raise HTTPException(
                status_code=403, 
                detail="Only the document owner can rename the document"
            )
            
    return await document_service.update_document(db, db_obj=doc, obj_in=doc_in)

@router.delete("/{document_id}", response_model=DocumentResponse)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.DELETE_DOCUMENT))
):
    doc = await document_service.delete_document(db, id=document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

# --- Messages in Document ---
@router.post("/{document_id}/messages", response_model=MessageResponse)
async def add_message(
    document_id: UUID, 
    msg_in: MessageCreate, 
    db: AsyncSession = Depends(get_db), 
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.SEND_MESSAGE))
):
    msg_in.document_id = document_id
    return await message_service.create_message(db, obj_in=msg_in, user_id=member.user_id)

@router.get("/{document_id}/messages", response_model=List[MessageResponse])
async def get_messages(
    document_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.READ_DOCUMENT))
):
    return await message_service.get_document_messages(db, document_id=document_id)

# --- Members in Document ---
@router.post("/{document_id}/members", response_model=DocumentMemberResponse)
async def add_member(
    document_id: UUID, 
    member_in: DocumentMemberCreate, 
    db: AsyncSession = Depends(get_db), 
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.INVITE_MEMBER))
):
    member_in.document_id = document_id
    return await document_member_service.add_member(db, obj_in=member_in)

@router.get("/{document_id}/members", response_model=List[DocumentMemberResponse])
async def get_members(
    document_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.READ_DOCUMENT))
):
    return await document_member_service.get_members(db, document_id=document_id)

@router.put("/{document_id}/members/{user_id}", response_model=DocumentMemberResponse)
async def update_member_role(
    document_id: UUID,
    user_id: UUID,
    member_in: DocumentMemberUpdate,
    db: AsyncSession = Depends(get_db),
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.MANAGE_MEMBERS))
):
    updated = await document_member_service.update_member_role(db, document_id=document_id, user_id=user_id, obj_in=member_in)
    if not updated:
        raise HTTPException(status_code=404, detail="Member not found in document")
    return updated

@router.delete("/{document_id}/members/{user_id}")
async def remove_member(
    document_id: UUID,
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.REMOVE_MEMBER))
):
    success = await document_member_service.remove_member(db, document_id=document_id, user_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="Member not found in document")
    return {"status": "success"}

# --- Versions in Document ---
@router.get("/{document_id}/versions", response_model=List[DocumentVersionResponse])
async def get_versions(
    document_id: UUID, 
    db: AsyncSession = Depends(get_db), 
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.READ_DOCUMENT))
):
    return await document_version_service.get_versions(db, document_id=document_id)

@router.post("/{document_id}/restore-version/{version_id}", response_model=DocumentResponse)
async def restore_version(
    document_id: UUID,
    version_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.EDIT_DOCUMENT))
):
    version = await document_version_service.get_version(db, id=version_id)
    if not version or version.document_id != document_id:
        raise HTTPException(status_code=404, detail="Version not found")
        
    doc = await document_service.get_document(db, id=document_id)
    doc_in = DocumentUpdate(content=version.content)
    updated_doc = await document_service.update_document(db, db_obj=doc, obj_in=doc_in)
    
    await document_version_service.create_version(db, document_id=document_id, content=version.content, created_by=current_user.id)
    return updated_doc

# --- AI Results in Document ---
@router.get("/{document_id}/ai-results", response_model=List[AIResultResponse])
async def get_document_ai_results(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    member: DocumentMember = Depends(RequireDocPermission(DocumentPermission.READ_DOCUMENT))
):
    # Note: Requires a method get_results_by_document in ai_service
    # For now falling back to returning requests
    return await ai_service.get_document_requests(db, document_id=document_id)
