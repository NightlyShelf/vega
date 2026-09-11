import asyncio
import logging

from aiohttp import WebSocketError, ClientError

from fastapi import WebSocket
from asyncio import Queue
from logging import Logger

from vega.router.helpers.connection_helper import ConnectionHelper
from vega.router.settings import Settings
from vega.shared.model.node_meta import NodeMeta


async def read_audio_chunks(node_meta: NodeMeta, node_ws: WebSocket, stt_queue: Queue, logger: Logger) -> None:
    while True:
        chunk: bytes = await node_ws.receive_bytes()
        if not chunk:
            continue
        if stt_queue.full():
            logger.log(logging.WARNING, f"WARNING: STT Queue for {node_meta} is full."
                                        f" Is STT service overloaded?")
            stt_queue.get_nowait()
        stt_queue.put_nowait(chunk)

async def send_audio_chunks_to_stt(node_meta: NodeMeta, stt_queue: Queue, logger: Logger, settings: Settings) -> None:
    connection_helper: ConnectionHelper = ConnectionHelper(settings.stt_url, logger)
    try:
        while True:
            try:
                logger.log(logging.INFO, f"Starting new connection to STT service for node {node_meta.id} via {settings.stt_url}")
                async with connection_helper.get_websocket() as ws:
                    await ws.send_json(node_meta.model_dump_json())
                    while True:
                        await ws.send_bytes(await stt_queue.get())
            except (WebSocketError, ClientError, ConnectionError) as error:
                logger.log(logging.ERROR, f"WebSocket disconnected for STT service for "
                                          f"node {node_meta.id} via {settings.stt_url}: {error}")
                retries: int = connection_helper.get_retries_count()
                if  retries > 5:
                    logger.log(logging.CRITICAL, "Maximum retries reached. Exiting...")
                    break
                retries_cooldown: float | int = (retries + 0.5 )*2
                logger.log(logging.INFO, f"Retrying connection after {retries_cooldown}s ...")
                await asyncio.sleep(retries_cooldown)
    finally:
        await connection_helper.close_connection()





