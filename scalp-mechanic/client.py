##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Client Class        ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
import logging
from asyncio import (
    AbstractEventLoop, Task, TimerHandle
)
from datetime import timedelta
from typing import Optional

from profile import Profile
from utils import urls
from utils.session import Session, TradovateWebSocket

## Constants
log = logging.getLogger(__name__)


## Classes
class Client(Profile):
    """Tradovate Client Class"""

    # -Constructor
    def __init__(self) -> Client:
        self._loop: AbstractEventLoop = asyncio.new_event_loop()
        super().__init__(Session(loop=self._loop))
        self._authorization_handle: Optional[TimerHandle] = None

    # -Instance Methods: Private
    def _renew_authorization(self) -> None:
        '''Send authorization renewal request'''
        log.debug("Auto-renewing client authorization")
        task = self._loop.create_task(self._session.renew_access_token())
        task.add_done_callback(self._timer_authorization)

    def _timer_authorization(self, result: Optional[Task] = None) -> None:
        '''Timer handler for authorization renewal'''
        if result:
            result.result()
        time = self._session.token_duration - timedelta(minutes=10)
        self._authorization_handle = self._loop.call_later(
            time.total_seconds(), self._renew_authorization
        )

    # -Instance Methods: Public
    async def authorize(self, dict_: dict[str, str], renew_authorization: bool) -> None:
        '''Initialize and setup auto-renewal for client authorization'''
        self._socket = await TradovateWebSocket.from_client(self, urls.base_market_live)
        self.id = await self._session.request_access_token(dict_, self._socket)
        if renew_authorization:
            self._timer_authorization()

    async def close(self) -> None:
        await self._socket.close()
        await self._session.close()

    def run(self, dict_: dict[str, str], *, renew: bool = True) -> None:
        '''Run client main loop'''
        self._loop.run_until_complete(self.authorize(dict_, renew))
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            self._loop.run_until_complete(self.close())
            self._loop.stop()

    # -Properties
    @property
    def authenticated(self):
        return self._session.authenticated and self._socket.authenticated

    @property
    def loop(self) -> AbstractEventLoop:
        return self._loop

    @property
    def session(self) -> Session:
        return self._session
