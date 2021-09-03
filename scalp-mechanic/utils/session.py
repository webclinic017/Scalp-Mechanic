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
from typing import Optional, TYPE_CHECKING
from asyncio import (
    AbstractEventLoop, TimerHandle
)
from datetime import (
    datetime, timedelta, timezone
)

from aiohttp import (
    ClientSession, ClientResponse,
    ClientWebSocketResponse as ClientWebSocket
)

from utils import (
    timestamp_to_datetime, urls
)
from utils.errors import (
    LoginInvalidException, LoginCaptchaException
)
if TYPE_CHECKING:
    from client import Client

## Constants
log = logging.getLogger(__name__)


## Classes
class TradovateWebSocket:
    """Tradovate WebSocket"""
    # Library Rewrite: 4 websocket types:
    # -Live Account Control
    # -Demo Account Control
    # -Live Market Data
    # -Market Replay Data

    # -Constructor
    def __init__(
        self, socket: ClientWebSocket,
        *, loop: Optional[AbstractEventLoop] = None
    ) -> TradovateWebSocket:
        self.connected: bool = False
        self.authenticated: bool = False
        self._request: int = 0
        self._heartbeat_handle: Optional[TimerHandle] = None
        self._loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()
        self._socket: Optional[ClientWebSocket] = socket
        self._loop.create_task(self.__async_init__())

    # -Dunder Methods
    async def __async_init__(self) -> None:
        if await self._socket.receive_str() != 'o':
            raise Exception()  # TODO: Better exception
        self.connected = True
        self._timer_heartbeat()

    # -Instance Methods: Private
    def _send_heartbeat(self) -> None:
        '''Send heartbeat packet to websocket'''
        log.debug("Sending heartbeat")
        self._loop.create_task(self._socket.send_str("[]"))
        self._timer_heartbeat()

    async def _socket_recieve(self) -> dict[str, str]:
        '''Recieve dictionary object from websocket'''
        ws_res = await self._socket.receive()
        ws_res_dict = json.loads(ws_res.data[1:])
        return ws_res_dict

    async def _socket_send(self, url: str, query: str = "", body: str = "") -> None:
        '''Send formatted request string to websocket'''
        req = f"{url}\n{self._request}\n{query}\n{body}"
        self._request += 1
        await self._socket.send_str(req)

    def _timer_heartbeat(self) -> None:
        '''Timer handle for websocket heartbeat'''
        self._heartbeat_handle = self._loop.call_later(
            2.5, self._send_heartbeat
        )

    # -Instance Methods: Public
    async def authorize(self, token: str) -> None:
        '''Authorize websocket connection'''
        await self._socket_send(urls.auth_websocket, body=token)
        ws_res = (await self._socket_recieve())[0]
        if ws_res['s'] != 200:
            raise Exception()  # TODO: Better exception
        self.authenticated = True

    async def close(self) -> None:
        if self._socket:
            await self._socket.close()

    async def request(
        self, url: str, *, body: Optional[dict[str, str]] = None, **kwargs
    ) -> None:
        query_ = ""
        body_ = ""
        if kwargs:
            fields = []
            for k, v in kwargs.items():
                fields.append(f"{k}={v}")
            query_ = '&'.join(fields)
        if body:
            body_ = json.dumps(body)
        await self._socket_send(url, query_, body_)

    # -Class Methods
    @classmethod
    async def from_client(
        cls, client: Client, url: str, *, loop: Optional[AbstractEventLoop] = None
    ) -> TradovateWebSocket:
        '''Create a WebSocket from a Client object'''
        loop = loop if loop else client.loop
        ws = await client.session.create_websocket(url)
        return cls(ws, loop=loop)

    @classmethod
    async def from_session(
        cls, session: Session, url: str, *, loop: Optional[AbstractEventLoop] = None
    ) -> TradovateWebSocket:
        '''Create a WebSocket from a Session object'''
        # For Tradovate Library Purposes
        loop = loop if loop else session.loop
        ws = await session.create_websocket(url)
        return cls(ws, loop=loop)


class Session:
    """Tradovate HTTP Session"""

    # -Constructor
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None) -> Session:
        self.authenticated: bool = False
        self.token_expiration: Optional[datetime] = None
        self._loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()
        self._session: Optional[ClientSession] = None
        self._loop.create_task(self.__async_init__())

    # -Dunder Methods
    async def __async_init__(self) -> None:
        self._session = ClientSession(loop=self._loop, raise_for_status=True)

    # -Instance Methods: Private
    async def _update_authorization(self, res: ClientResponse) -> dict[str, str]:
        '''Set authorization for active session'''
        res_dict = await res.json()
        # -Invalid Credentials
        if 'errorText' in res_dict:
            self.authenticated = False
            raise LoginInvalidException(res_dict['errorText'])
        # -Invalid Captcha
        elif 'p-ticket' in res_dict:
            self.authenticated = False
            raise LoginCaptchaException(
                res_dict['p-ticket'], int(res_dict['p-time']),
                bool(res_dict['p-captcha'])
            )
        # -Access Token
        self.authenticated = True
        self.token_expiration = timestamp_to_datetime(res_dict['expirationTime'])
        self._session.headers.update({
            'AUTHORIZATION': "Bearer " + res_dict['accessToken']
        })
        return res_dict

    # -Instance Methods: Public
    async def close(self) -> None:
        if self._session:
            await self._session.close()

    async def get(self, url: str, *args, **kwargs) -> dict[str, str]:
        res = await self._session.request('GET', url, *args, **kwargs)
        return await res.json()

    async def post(self, url: str, *args, **kwargs) -> dict[str, str]:
        res = await self._session.request('POST', url, *args, **kwargs)
        return await res.json()

    async def renew_access_token(self) -> None:
        '''Renew session authorization'''
        res = await self._session.post(urls.auth_renew)
        await self._update_authorization(res)

    async def request_access_token(
        self, dict_: dict[str, str], websocket: Optional[TradovateWebSocket] = None
    ) -> int:
        '''Request session authorization'''
        res = await self._session.post(urls.auth_request, json=dict_)
        res_dict = await self._update_authorization(res)
        if websocket:
            await websocket.authorize(res_dict['mdAccessToken'])
        return res_dict['userId']

    async def create_websocket(self, url: str, *args, **kwargs) -> ClientWebSocket:
        '''Create an aiohttp websocket response'''
        return await self._session.ws_connect(url, *args, **kwargs)

    # -Properties
    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def token_duration(self) -> timedelta:
        return self.token_expiration - datetime.now(timezone.utc)

    @property
    def token_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.token_expiration
