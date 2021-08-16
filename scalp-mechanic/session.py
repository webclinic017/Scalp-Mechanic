##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Session Class                 ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
from asyncio import AbstractEventLoop
from datetime import datetime
from typing import Optional

import aiohttp
from aiohttp import ClientSession, ClientResponse, ClientWebSocketResponse

from . import urls


## Functions
def timestamp_to_datetime(
    timestamp: str, timestring: str = "%Y-%m-%dT%H:%M:%S.%f%z"
) -> datetime:
    """"""
    return datetime.strptime(timestamp, timestring)


## Classes
class SessionException(Exception):
    """Base exception class for Session"""
    pass


class WebsocketError(SessionException):
    """Unable to establish websocket"""
    pass


class InvalidLoginException(SessionException):
    """Invalid session login exception"""

    def __init__(self, message: str) -> InvalidLoginException:
        super().__init__(message)


class Session:
    """Tradovate Session Class"""

    # -Constructor
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None) -> Session:
        self.authenticated: bool = False
        self.expiration: Optional[datetime] = None
        self.__session: Optional[ClientSession] = None
        self.__socket: Optional[ClientWebSocketResponse] = None
        self.loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()
        self.loop.run_until_complete(self.__async_init__())

    # -Dunder Methods
    def __del__(self) -> None:
        self.loop.run_until_complete(self.__async_del__())

    async def __async_init__(self) -> None:
        self.__session = aiohttp.ClientSession(loop=self.loop, raise_for_status=True)
        self.__socket = await self.__session.ws_connect(urls.base_market_live)
        if await self.__socket.receive_str() != 'o':
            raise WebsocketError()

    async def __async_del__(self) -> None:
        if self.__session:
            await self.__session.close()
            await self.__socket.close()

    # -Instance Methods: Private
    async def _update_authorization(self, resp: ClientResponse) -> None:
        ''''''
        resp = await resp.json()
        if 'errorText' in resp:
            raise InvalidLoginException(resp['errorText'])
        elif 'p-ticket' in resp:
            raise InvalidLoginException(
                f"Unable to authorize - ticket: {resp['p-ticket']}:{resp['p-time']}"
            )
        self.authenticated = True
        self.expiration = timestamp_to_datetime(resp['expirationTime'])
        self.__session.headers.update({
            'AUTHORIZATION': "Bearer " + resp['accessToken']
        })

    # -Instance Methods
    async def request_access_token(self, _dict: dict[str, str]) -> None:
        ''''''
        res = await self.__session.post(urls.auth_request, json=_dict)
        await self._update_authorization(res)

    async def renew_access_token(self) -> None:
        ''''''
        pass
