from asyncio import sleep
from time import time

from vega.router.model.context import Context

UPDATE_TICK: float | int = 0.5
FLUSH_TIME: float | int = 1


class ContextManager:
    context_buffer: list[Context]

    def __init__(self):
        self.context_buffer = []

    def context_exists(self, room_id: str, device_id: str) -> Context | None:
        for context in self.context_buffer:
            if context.room_id == room_id and context.device_id == device_id:
                return context
        return None

    @staticmethod
    def update_context(context: Context, content: str) -> None:
        context.content += " " + content
        context.last_push = time()

    async def start_collecting_context(self, context: Context) -> None:
        self.context_buffer.append(context)
        while True:
            await sleep(UPDATE_TICK)
            # Should be only 1 context from 1 device in 1 room
            current_time: float | int = time()
            if current_time - context.last_push >= FLUSH_TIME:
                return
