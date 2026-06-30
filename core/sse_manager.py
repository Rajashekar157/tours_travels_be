# core/sse_manager.py
import asyncio
from typing import Dict

class SSEManager:
    """
    Tracks one active SSE connection queue per jti (session id).
    When a session is evicted, we push a message into its queue;
    the SSE generator picks it up and the client disconconnects.
    """
    def __init__(self):
        self._connections: Dict[str, asyncio.Queue] = {}

    def register(self, jti: str) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._connections[jti] = queue
        return queue

    def unregister(self, jti: str):
        self._connections.pop(jti, None)

    async def notify_evicted(self, jti: str):
        queue = self._connections.get(jti)
        if queue:
            await queue.put("evicted")

sse_manager = SSEManager()