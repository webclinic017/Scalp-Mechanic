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
from profile.session import Session
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
    def _auth_renewal(self) -> None:
        '''Send authorization auto-renewal request'''
        task = self._loop.create_task(self._session.renew_access_token())
        task.add_done_callback(self._auth_renewal_timer)

    def _auth_renewal_timer(self, result: asyncio.Task | None = None) -> None:
        '''Timer handler for authorization auto-renewal'''
        if result:
            result.result()
        time = self._session.token_duration - timedelta(minutes=10)
        self._handle_auto_renewal = self._loop.call_later(
            time.total_seconds(), self._auth_renewal
        )

    # -Instance Methods: Public
    async def authorize(
        self, auth: CredentialAuthDict, auto_renew: bool = True
    ) -> None:
        '''Initialize Client authorization and auto-renewal'''
        self.id = await self._session.request_access_token(auth)
        if auto_renew:
            self._auth_renewal_timer()
        return self.authenticated

    async def close(self) -> None:
        await self._session.close()

    def run(
        self, auth: CredentialAuthDict,
        *, auto_renew: bool = True
    ) -> None:
        '''Run client loop'''
        self._loop.run_until_complete(self.authorize(auth, auto_renew))
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            self._loop.run_until_complete(self.close())
            self._loop.close()

    # -Property
