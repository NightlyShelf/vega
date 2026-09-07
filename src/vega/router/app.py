import logging
from http import HTTPStatus
from logging import getLogger
from os import getenv

from aiohttp import ClientSession
from fastapi import (
    FastAPI,
    HTTPException,
    WebSocket,
    WebSocketDisconnect,
    WebSocketException,
)

from vega.router.context_manager import ContextManager
from vega.router.format_helper import FormatHelper
from vega.router.model.context import Context
from vega.router.model.wakeword_config import AgentModel
from vega.router.wakeword_detector import WakeWordDetector
from vega.shared.model.request import Request

STT_URL = getenv("STT_URL")
assert STT_URL is not None
app = FastAPI()
detector = WakeWordDetector()
logger = getLogger("uvicorn")
logger.setLevel(10)
formatter = logging.Formatter(
    "[{asctime}:{msecs}] {levelname}: {message}", style="{", datefmt="%Y-%m-%d %H:%M:%S"
)
logger.handlers[0].setFormatter(formatter)
context_manager = ContextManager()
input_devices_connected: list[Request] = []


@app.post("/api/query_agent")
async def query_agent(request: Request) -> None:
    logger.log(10, msg=f"Request: {request}")
    # NOTE: potential problems with synchronous code below
    agent: AgentModel | None = detector.search_wakewords(request.content)
    context: Context | None = context_manager.context_exists(
        request.room, request.device
    )

    if context is not None:
        context_manager.update_context(context, request.content)
        logger.log(20, f"Updated context from {request.device} in {request.room}")
        return

    if agent:
        context: Context = Context(request.room, request.device, request.content)
        await context_manager.start_collecting_context(context)
        logger.log(10, f"Proxying request {request.request_id} to {agent.endpoint}")

        try:
            async with ClientSession(read_timeout=30) as session:
                async with session.post(
                    agent.endpoint,
                    data=request.model_dump_json(),
                    headers={
                        "X-Api-Key": agent.auth_header,
                        "Accept": "text/event-stream",
                    },
                ) as response:
                    response.raise_for_status()
                    async for line in response.content:
                        result = FormatHelper.parse_sse_chunk(line.decode())
                        if result is not None:
                            print(result, end="", flush=True)

        except TimeoutError:
            raise HTTPException(
                status_code=HTTPStatus.BAD_GATEWAY,
                detail=f"Timeout error. Is {agent.endpoint} endpoint alive?",
            )

        context_manager.context_buffer.remove(context)
        print("\nEnd of stream")
    else:
        logger.log(10, f"Noise captured. Skipping from {request.device} {request.room}")


@app.websocket("/api/audio_in")
async def audio_in(websocket: WebSocket):
    await websocket.accept()
    request: Request = Request.model_validate_json(await websocket.receive_json())
    input_devices_connected.append(request)
    try:
        async with ClientSession() as session:
            async with session.ws_connect(STT_URL) as ws:
                ws.send_json(request)
                while True:
                    chunk: bytes = await websocket.receive_bytes()
                    await ws.send_bytes(chunk)
    except WebSocketDisconnect:
        input_devices_connected.remove(request)
    except WebSocketException as ex:
        logger.error(f"WebSocketException: {ex.reason}")
