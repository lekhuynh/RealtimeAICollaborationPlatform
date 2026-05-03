import asyncio
import socket
import os
from sqlalchemy import create_engine, select
from sqlalchemy.ext.asyncio import create_async_engine
from app.core.config import settings
import google.generativeai as genai

async def check_db():
    print("--- 1. Kiểm tra Database ---")
    try:
        engine = create_async_engine(settings.DATABASE_URL)
        async with engine.connect() as conn:
            await conn.execute(select(1))
        print("✅ Kết nối Database THÀNH CÔNG!")
    except Exception as e:
        print(f"❌ Lỗi kết nối Database: {e}")
        print("Gợi ý: Kiểm tra mạng Internet hoặc DATABASE_URL trong .env")

def check_network():
    print("\n--- 2. Kiểm tra DNS & Mạng ---")
    host = "google.com"
    try:
        addr = socket.getaddrinfo(host, 443)
        print(f"✅ Phân giải DNS {host} THÀNH CÔNG: {addr[0][4][0]}")
    except Exception as e:
        print(f"❌ Lỗi DNS: {e}")
        print("Gợi ý: Mạng máy tính của bạn đang không có Internet hoặc bị chặn DNS.")

def check_gemini():
    print("\n--- 3. Kiểm tra Gemini API ---")
    if not settings.API_GEMINI_KEY:
        print("❌ Lỗi: Chưa có API_GEMINI_KEY trong .env")
        return
    try:
        genai.configure(api_key=settings.API_GEMINI_KEY)
        print("Danh sách model khả dụng:")
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                print(f" - {m.name}")
        
        # Thử với gemini-2.5-flash (model ổn định nhất)
        model = genai.GenerativeModel('gemini-2.5-flash')
        response = model.generate_content("Hi")
        print(f"\n✅ Kết nối Gemini API ({model.model_name}) THÀNH CÔNG!")
    except Exception as e:
        print(f"❌ Lỗi Gemini API: {e}")

if __name__ == "__main__":
    check_network()
    asyncio.run(check_db())
    check_gemini()
