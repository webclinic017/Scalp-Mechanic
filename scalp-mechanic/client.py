##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Client Class        ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
from datetime import timedelta

from profile import Profile
from profile.session import Session, WebSocket
from utils import urls
from utils.typing import CredentialAuthDict


## Classes
class Client(Profile):
    """Tradovate Client"""

    # -Constructor
    def __init__(self) -> Client:
        self.id: int = 0
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._session: Session = Session(loop=self._loop)
        self._handle_auto_renewal: asyncio.TimerHandle | None = None

    # -Instance Methods: Private
    async def _auth_renewal(self) -> None:
        '''Send authorization auto-renewal request'''
        while self.authenticated:
            time = self._session.token_duration - timedelta(minutes=10)
            await asyncio.sleep(time.total_seconds())
            await self._session.renew_access_token()

    # -Instance Methods: Public
    async def authorize(
        self, auth: CredentialAuthDict, auto_renew: bool = True
    ) -> None:
        '''Initialize Client authorization and auto-renewal'''
        self.id = await self._session.request_access_token(auth)
        if auto_renew:
            self._loop.create_task(self._auth_renewal(), name="client-renewal")

    async def close(self) -> None:
        await self._session.close()

    def run(self, auth: CredentialAuthDict, *, auto_renew: bool = True) -> None:
        '''Run client loop'''
        self._loop.run_until_complete(self.authorize(auth, auto_renew))
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            for task in asyncio.all_tasks(loop=self._loop):
                task.cancel()
            self._loop.run_until_complete(self.close())
            self._loop.close()
