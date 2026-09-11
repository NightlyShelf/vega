import logging
from logging import Logger
from typing import AsyncGenerator

from pydantic import WebsocketUrl

from aiohttp import ClientSession, ClientWebSocketResponse

from contextlib import asynccontextmanager

class ConnectionHelper:
    _session: ClientSession | None
    _websocket: ClientWebSocketResponse | None
    _ws_url: WebsocketUrl
    _logger: Logger
    _retries_count: int

    def __init__(self,  ws_url: WebsocketUrl, logger: Logger):
        self._ws_url = ws_url
        self._logger = logger
        self._session = None
        self._websocket = None
        self._retries_count = -1 #because we count first connection as 0 retries

    def get_retries_count(self) -> int:
        return self._retries_count

    @asynccontextmanager
    async def get_websocket(self) -> AsyncGenerator[ClientWebSocketResponse, None]:
        self._retries_count += 1
        try:
            if self._session is None:
                self._session = ClientSession()
                self._logger.log(logging.INFO, f"Opening new session for websocket...")
            if self._websocket is None:
                self._logger.log(logging.INFO, f"Opening new websocket to {self._ws_url}...")
                assert self._session is not None
                self._websocket = await self._session.ws_connect(str(self._ws_url))
            self._logger.log(logging.INFO, f"Websocket to {self._ws_url} opened successfully")
            websocket = self._websocket
            #  noinspection PyTypeChecker
            yield websocket

        finally:
            await self.close_connection()

    async def close_connection(self):
        if self._websocket is not None and not self._websocket.closed:
            self._logger.log(logging.INFO, f"Closing websocket to {self._ws_url}...")
            await self._websocket.close()
        if self._session is not None and not self._session.closed:
            self._logger.log(logging.INFO, "Closing session...")
            await self._session.close()
        self._websocket = None
        self._session = None
        self._logger.log(logging.INFO, f"Session and websocket to {self._ws_url} closed")

