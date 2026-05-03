import os
import json
import logging
import redis
import google.generativeai as genai
from celery import shared_task
from app.worker.celery_app import celery_app
from app.core.config import settings
import asyncio
import sys
from uuid import UUID
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.pool import NullPool
from app.repositories.ai_repo import ai_request_repo, ai_result_repo
from app.schemas.ai_result import AIResultCreate

logger = logging.getLogger(__name__)

# Ép Windows sử dụng SelectorEventLoop để tránh lỗi 'Event loop is closed' khi dùng asyncpg
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

def get_task_engine():
    return create_async_engine(
        settings.DATABASE_URL,
        poolclass=NullPool,
        connect_args={
            "prepared_statement_cache_size": 0,
            "statement_cache_size": 0,
        }
    )

async def update_request_status(session, request_id: str, status: str):
    request = await ai_request_repo.get(session, id=request_id)
    if request:
        request.status = status
        session.add(request)
        await session.commit()

async def save_final_result(session, request_id: str, result_text: str):
    result_in = AIResultCreate(
        request_id=UUID(request_id),
        result=result_text,
        scope="document"
    )
    await ai_result_repo.create(session, obj_in=result_in)
    await session.commit()

async def run_ai_logic(document_id: str, request_id: str, task_type: str, prompt: str):
    engine = get_task_engine()
    TaskSession = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
    
    REDIS_URL = settings.REDIS_URL
    redis_sync = redis.from_url(REDIS_URL, decode_responses=True)
    genai.configure(api_key=settings.API_GEMINI_KEY)
    ai_model = genai.GenerativeModel('gemini-2.5-flash')
    
    full_content = ""
    try:
        async with TaskSession() as db:
            await update_request_status(db, request_id, "processing")

            system_prompt = "You are a helpful AI writing assistant."
            full_prompt = f"{system_prompt}\n\nTask: {task_type}\nPrompt: {prompt}"
            
            logger.info(f"Calling Gemini for {request_id}...")
            response = await ai_model.generate_content_async(full_prompt, stream=True)
            
            async for chunk in response:
                # Kiểm tra xem chunk có chứa văn bản không trước khi truy cập .text
                if chunk.candidates and chunk.candidates[0].content.parts:
                    chunk_text = chunk.text
                    full_content += chunk_text
                    
                    broadcast_data = {
                        "type": "ai_chunk",
                        "request_id": request_id,
                        "document_id": document_id,
                        "content": chunk_text,
                        "is_final": False
                    }
                    redis_sync.publish(f"chat:{document_id}", json.dumps(broadcast_data))

            await save_final_result(db, request_id, full_content)
            await update_request_status(db, request_id, "completed")
            
            final_broadcast = {
                "type": "ai_result",
                "request_id": request_id,
                "document_id": document_id,
                "content": full_content,
                "status": "completed"
            }
            redis_sync.publish(f"chat:{document_id}", json.dumps(final_broadcast))
            logger.info(f"✅ Task {request_id} finished successfully!")

    except Exception as e:
        logger.error(f"AI Logic Error: {e}")
        error_data = {"type": "ai_error", "request_id": request_id, "content": str(e)}
        redis_sync.publish(f"chat:{document_id}", json.dumps(error_data))
        try:
            async with TaskSession() as fail_db:
                await update_request_status(fail_db, request_id, "failed")
        except: pass
        raise e
    finally:
        await engine.dispose()

@celery_app.task(name="process_ai_document", bind=True, max_retries=1)
def process_ai_document(self, document_id: str, request_id: str, task_type: str, prompt: str = None):
    logger.info(f"--- Task {request_id} Starting ---")
    # Đảm bảo mỗi lần chạy là một loop mới sạch sẽ
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(run_ai_logic(document_id, request_id, task_type, prompt))
    finally:
        loop.close()
