from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine
from app.db.base import Base 
from app.core.config import settings
from app.api.v1.router import router as api_router
from app.websocket.router import router as ws_router

app = FastAPI(
    title="AI Platform API",
    version="1.0.0",
    description="AI Platform system API"
)

# Cấu hình CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://192.168.1.11:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Gắn router
app.include_router(api_router, prefix="/api")
app.include_router(ws_router, prefix="/ws", tags=["websocket"])

@app.get("/")
def read_root():
    return {"message": "Hệ thống đã chạy, DB đã tự động tạo!"}