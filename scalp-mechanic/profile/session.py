##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Session Classes     ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
import json
import logging
from asyncio import AbstractEventLoop
from datetime import datetime, timedelta, timezone

import aiohttp
from aiohttp import ClientWebSocketResponse as ClientWebSocket

from utils import timestamp_to_datetime, urls
from utils.errors import (
    LoginInvalidException, LoginCaptchaException,
    WebSocketOpenException, WebSocketAuthorizationException
)
from utils.typing import CredentialAuthDict

## Constants
log = logging.getLogger(__name__)


## Classes
class Session:
    """Tradovate Session"""

    # -Constructor
    def __init__(self, *, loop: AbstractEventLoop | None = None) -> Session:
        self.authenticated: asyncio.Event = asyncio.Event()
        self.token_expiration: datetime | None = None
        self._aiosession: aiohttp.ClientSession | None = None
        self._loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()
        self._loop.create_task(self.__ainit__(), name="session-init")

    # -Dunder Methods
    async def __ainit__(self) -> None:
        self._aiosession = aiohttp.ClientSession(loop=self._loop, raise_for_status=True)

    # -Instance Methods: Private
    async def _update_authorization(
        self, res: aiohttp.ClientResponse
    ) -> dict[str, str]:
        '''Updates Session authorization fields'''
        res_dict = await res.json()
        # -Invalid Credentials
        if 'errorText' in res_dict:
            self.authenticated.clear()
            raise LoginInvalidException(res_dict['errorText'])
        # -Captcha Limiting
        if 'p-ticket' in res_dict:
            self.authenticated.clear()
            raise LoginCaptchaException(
                res_dict['p-ticket'], int(res_dict['p-time']),
                bool(res_dict['p-captcha'])
            )
        # -Access Token
        log.debug("Authenticated session successfully")
        self.authenticated.set()
        self.token_expiration = timestamp_to_datetime(res_dict['expirationTime'])
        self._aiosession.headers.update({
            'AUTHORIZATION': "Bearer " + res_dict['accessToken']
        })
        return res_dict

    # -Instance Methods: Public
    async def close(self) -> None:
        self.authenticated = False
        await self._aiosession.close()

    async def create_websocket(self, url: str, *args, **kwargs) -> ClientWebSocket:
        '''Return an aiohttp WebSocket'''
        return await self._aiosession.ws_connect(url, *args, **kwargs)

    async def get(self, url, *args, **kwargs) -> dict[str, str]:
        res = await self._aiosession.request('GET', url, *args, **kwargs)
        return await res.json()

    async def renew_access_token(self) -> None:
        '''Renew Session authorization'''
        log.debug("Renewing session token")
        res = await self._aiosession.post(urls.http_auth_renew)
        await self._update_authorization(res)

    async def request_access_token(self, auth: CredentialAuthDict, test) -> int:
        '''Request Session authorization'''
        log.debug("Requesting session token")
        res = await self._aiosession.post(urls.http_auth_request, json=auth)
        res_dict = await self._update_authorization(res)
        # -WebSockets
        await test.authorize(res_dict['mdAccessToken'])
        return res_dict['userId']

    # -Property
    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def token_duration(self) -> timedelta:
        return self.token_expiration - datetime.now(timezone.utc)

    @property
    def token_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.token_expiration


class WebSocket:
    """Tradovate WebSocket"""

    # -Constructor
    def __init__(
        self, url: str, websocket: ClientWebSocket, *,
        loop: AbstractEventLoop | None = None
    ) -> WebSocket:
        self.url: str = url
        self.connected: asyncio.Event = asyncio.Event()
        self.authenticated: asyncio.Event = asyncio.Event()
        self._request: int = 0
        self._aiowebsocket: ClientWebSocket = websocket
        self._loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()
        self._loop.create_task(self.__ainit__(), name=f"websocket-init{self.id}")
        WebSocket.id += 1

    # -Dunder Methods
    async def __ainit__(self) -> None:
        if await self._aiowebsocket.receive_str() != 'o':
            raise WebSocketOpenException(self.url)
        self.connected.set()

    # -Instance Methods: Private
    async def _socket_recieve(self) -> dict[str, str]:
        '''Recieve dictionary object from aiowebsocket'''
        ws_res = await self._aiowebsocket.receive()
        ws_res_dict = json.loads(ws_res.data[1:])
        return ws_res_dict

    async def _socket_send(self, url: str, query: str = "", body: str = "") -> None:
        '''Send formatted request string to aiowebsocket'''
        req = f"{url}\n{self._request}\n{query}\n{body}"
        self._request += 1
        await self._aiowebsocket.send_str(req)

    # -Instance Methods: Public
    async def authorize(self, token: str) -> None:
        '''Request WebSocket authorization'''
        await self._socket_send(urls.wss_auth, body=token)
        ws_res = (await self._socket_recieve())[0]
        if ws_res['s'] != 200:
            raise WebSocketAuthorizationException(self.url, token)
        self.authenticated.set()

    async def close(self) -> None:
        if self._aiowebsocket:
            await self._aiowebsocket.close()

    # -Class Methods
    @classmethod
    async def from_session(
        cls, url: str, session: Session, *,
        loop: AbstractEventLoop | None = None
    ) -> WebSocket:
        '''Create WebSocket from Session'''
        loop = loop if loop else session.loop
        websocket = await session.create_websocket(url)
        return cls(
            url, websocket, loop=loop
        )

    # -Class Properties
    id: int = 0
