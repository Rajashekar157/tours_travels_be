# core/chat_sse_manager.py
import asyncio
from collections import defaultdict
from typing import Dict, Set

class ChatSSEManager:
    """
    Unlike SSEManager (single connection per session jti),
    a user might have this app open in multiple tabs, so we keep
    a SET of queues per user_id.
    """
    def __init__(self):
        self._connections: Dict[int, Set[asyncio.Queue]] = defaultdict(set)

    def register(self, user_id: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue()
        self._connections[user_id].add(queue)
        return queue

    def unregister(self, user_id: int, queue: asyncio.Queue):
        self._connections[user_id].discard(queue)
        if not self._connections[user_id]:
            del self._connections[user_id]

    async def push_to_user(self, user_id: int, payload: dict):
        for queue in self._connections.get(user_id, []):
            await queue.put(payload)

chat_sse_manager = ChatSSEManager()