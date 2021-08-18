##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Scalp Mechanic Client Class   ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio

from .session import Session
from utils import urls


## Classes
class Client:
    """Scalp-Mechanic Client Class"""

    # -Constructor
    def __init__(self) -> Client:
        self.id: int = 0
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._session: Session = Session(loop=self._loop)

    # -Instance Methods
    async def authorize(self, dict_: dict[str, str]) -> None:
        '''Authorize client session'''
        await self._session.request_access_token(dict_)
        await self.me()

    async def me(self) -> None:
        '''GET request: Tradovate basic client data'''
        client_data = await self._session.get(urls.auth_me)
        self.id = client_data['userId']

    def run(self, dict_: dict[str, str]) -> None:
        '''Run client main loop'''
        self._loop.run_until_complete(self.authorize(dict_))
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            self._loop.run_until_complete(self._session.close())
