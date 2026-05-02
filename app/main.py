from fastapi import FastAPI

from sqlalchemy import create_engine
from app.db.base import Base 
from app.core.config import settings

# Khởi tạo engine kết nối Supabase
engine = create_engine(settings.DATABASE_URL, pool_pre_ping=True)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="AI Platform API",
    version="1.0.0",
    description="AI Platform system API"
)



@app.get("/")
def read_root():
    return {"message": "Hệ thống đã chạy, DB đã tự động tạo!"}