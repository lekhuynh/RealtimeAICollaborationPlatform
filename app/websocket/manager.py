import asyncio
import logging
from typing import Dict, List
from fastapi import WebSocket
from app.cache.redis import redis_client

logger = logging.getLogger(__name__)

class ConnectionManager:
    def __init__(self):
        # document_id -> list of local websockets
        self.active_connections: Dict[str, List[WebSocket]] = {}
        self.pubsub = redis_client.pubsub()
        self.task: asyncio.Task = None

    async def connect(self, websocket: WebSocket, document_id: str):
        await websocket.accept()
        if document_id not in self.active_connections:
            self.active_connections[document_id] = []
            
            # Subscribe to Redis Pub/Sub channel for this document
            await self.pubsub.subscribe(f"chat:{document_id}")
            
            # Start background listener task if not started
            if self.task is None or self.task.done():
                self.task = asyncio.create_task(self.listen_to_redis())
                
        self.active_connections[document_id].append(websocket)

    def disconnect(self, websocket: WebSocket, document_id: str):
        if document_id in self.active_connections:
            if websocket in self.active_connections[document_id]:
                self.active_connections[document_id].remove(websocket)
            
            # If no more local clients for this document, unsubscribe
            if not self.active_connections[document_id]:
                del self.active_connections[document_id]
                asyncio.create_task(self.pubsub.unsubscribe(f"chat:{document_id}"))

    async def broadcast(self, message: str, document_id: str):
        # Publish message to Redis so ALL instances receive it
        await redis_client.publish(f"chat:{document_id}", message)

    async def listen_to_redis(self):
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    channel = message["channel"]
                    doc_id = channel.split(":")[1]
                    data = message["data"]
                    
                    # Push to all local sockets connected to this doc
                    if doc_id in self.active_connections:
                        dead_sockets = []
                        for connection in self.active_connections[doc_id]:
                            try:
                                await connection.send_text(data)
                            except Exception as e:
                                logger.error(f"Error sending message to websocket: {e}")
                                dead_sockets.append(connection)
                        
                        # Cleanup dead connections
                        for dead in dead_sockets:
                            self.disconnect(dead, doc_id)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            logger.error(f"Redis pubsub error: {e}")

manager = ConnectionManager()
