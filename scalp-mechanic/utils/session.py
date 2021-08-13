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
from aiohttp import ClientSession, ClientWebSocketResponse

from utils import urls


## Classes
class Session:
    """Tradovate Session Class"""

    # -Constructor
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None) -> Session:
        # -Connection
        self.ready: bool = False
        self.closed: bool = False
        self.__session: Optional[ClientSession] = None
        self.__socket: Optional[ClientWebSocketResponse] = None
        # -Authentication
        self.authenticated: bool = False
        self.expiration: Optional[datetime] = None
        # -Async
        self.loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()

    # -Instance Methods: Public - Authorization
    async def request_access_token(self, _dict: dict[str, str]) -> None:
        ''''''
        res = await self.__session.post(urls.auth_request, json=_dict)
        res = await res.json()
        pass

    async def renew_access_token(self):
        ''''''
        pass

    # -Instance Methods: Private
    async def _init(self) -> None:
        '''Async Module Initializion'''
        self.__session = aiohttp.ClientSession()
        self.__socket = await self.__session.ws_connect(urls.base_market_live)

    async def _del(self) -> None:
        '''Async Module Deletion'''
        if self.closed:
            return None
        self.closed = True
