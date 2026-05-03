import time
import json
import redis
import os
import logging
from worker.celery_app import celery_app

logger = logging.getLogger(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
# Using synchronous Redis client for Celery
redis_sync = redis.from_url(REDIS_URL, decode_responses=True)

@celery_app.task(name="process_ai_document", bind=True)
def process_ai_document(self, document_id: str, request_id: str, task_type: str, prompt: str = None):
    logger.info(f"Starting AI task {request_id} for document {document_id}")
    
    # 1. Fake LLM processing delay
    time.sleep(3) 
    
    # 2. Fake Result Generation
    action = f"Prompt: {prompt}" if prompt else f"Task: {task_type}"
    result_text = f"[AI Result] Đã hoàn thành xử lý cho {action} trên tài liệu {document_id}. (Worker processed request_id: {request_id})"
    
    # 3. Publish result to Redis Pub/Sub so WebSocket can broadcast to users
    broadcast_data = {
        "type": "ai_result",
        "request_id": request_id,
        "document_id": document_id,
        "content": result_text,
        "status": "completed"
    }
    
    try:
        redis_sync.publish(f"chat:{document_id}", json.dumps(broadcast_data))
        logger.info(f"Broadcasted result for {request_id} successfully")
    except Exception as e:
        logger.error(f"Failed to publish to redis: {e}")
    
    # Note: A real app would also connect to PostgreSQL here to update ai_requests.status = 'completed'
    # For now, we return it to Celery Backend.
    return {"status": "completed", "result": result_text}
