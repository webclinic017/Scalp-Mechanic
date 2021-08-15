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

from . import urls


## Classes
class Session:
    """Tradovate Session Class"""

    # -Constructor
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None) -> Session:
        # -Connection
        self.__session: Optional[ClientSession] = None
        self.__socket: Optional[ClientWebSocketResponse] = None
        # -Authentication
        self.authenticated: bool = False
        self.expiration: Optional[datetime] = None
        # -Async
        self.loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()

    # -Dunder Methods
    def __del__(self) -> None:
        self.loop.run_until_complete(self.__async_del__())

    async def __async_init__(self) -> None:
        self.__socket = aiohttp.ClientSession(loop=self.loop, raise_for_status=True)

    async def __async_del__(self) -> None:
        if self.__socket:
            await self.__socket.close()
