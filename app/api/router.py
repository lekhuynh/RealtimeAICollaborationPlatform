from fastapi import APIRouter
from app.api.v1.router import router as v1_router

# Tạo router chính
router = APIRouter()

# Include v1 router
router.include_router(v1_router, prefix="/v1")