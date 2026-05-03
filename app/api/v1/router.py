from fastapi import APIRouter
from .endpoints import auth, users, documents, ai, messages, admin, members

router = APIRouter()

router.include_router(auth.router, prefix="/auth", tags=["auth"])
router.include_router(users.router, prefix="/users", tags=["users"])
router.include_router(documents.router, prefix="/documents", tags=["documents"])
router.include_router(ai.router, prefix="/ai", tags=["ai"])
router.include_router(messages.router, prefix="/messages", tags=["messages"])
router.include_router(members.router, prefix="/members", tags=["members"])
router.include_router(admin.router, prefix="/admin", tags=["admin"])
