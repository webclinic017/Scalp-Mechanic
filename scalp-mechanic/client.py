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
from datetime import timedelta

from profile import Profile
from profile.session import Session, WebSocket
from utils import urls
from utils.typing import CredentialAuthDict

## Constants
log = logging.getLogger(__name__)


## Classes
class Client(Profile):
    """Tradovate Client"""

    # -Constructor
    def __init__(self) -> Client:
        self.id: int = 0
        self._loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self._session: Session = Session(loop=self._loop)
        self._handle_auto_renewal: asyncio.TimerHandle | None = None
        self._live: WebSocket | None = None
        self._demo: WebSocket | None = None
        self._mdlive: WebSocket | None = None
        self._mddemo: WebSocket | None = None
        self._mdreplay: WebSocket | None = None

    # -Instance Methods: Private
    async def _authorize(self) -> None:
        '''Coroutine for waiting for all authentication setup'''
        await self._session.authenticated.wait()
        for websocket in self._websockets:
            await websocket.authenticated.wait()

    def _dispatch(self, event: str, *args, **kwargs) -> None:
        '''Dispatch task for event name'''
        log.debug(f"Client event '{event}'")
        method = "on_" + event
        try:
            coro = getattr(self, method)
        except AttributeError:
            pass
        else:
            self._loop.create_task(coro(*args, **kwargs))

    async def _renewal(self) -> None:
        '''Send authorization auto-renewal request'''
        while self._session.authenticated.is_set():
            time = self._session.token_duration - timedelta(minutes=10)
            await asyncio.sleep(time.total_seconds())
            await self._session.renew_access_token()

    # -Instance Methods: Public
    async def authorize(
        self, auth: CredentialAuthDict, auto_renew: bool = True
    ) -> None:
        '''Initialize Client authorization and auto-renewal'''
        self.id = await self._session.request_access_token(
            auth, account_websockets=self._websockets_account,
            market_websockets=self._websockets_market
        )
        if auto_renew:
            self._loop.create_task(self._renewal(), name="client-renewal")
        await self._authorize()
        self._dispatch('connect')

    async def close(self) -> None:
        for websocket in self._websockets:
            await websocket.close()
        await self._session.close()

    async def init_websockets(
        self, live: bool, demo: bool, mdlive: bool
    ) -> None:
        '''Initialize Client WebSockets'''
        self._live = (
            await WebSocket.from_session(urls.wss_base_live, self._session)
            if live else None
        )
        self._demo = (
            await WebSocket.from_session(urls.wss_base_demo, self._session)
            if demo else None
        )
        self._mdlive = (
            await WebSocket.from_session(urls.wss_base_market, self._session)
            if mdlive else None
        )

    def run(
        self, auth: CredentialAuthDict, *, auto_renew: bool = True,
        live_websocket: bool = True, demo_websocket: bool = True,
        mdlive_websocket: bool = True
    ) -> None:
        '''Run client loop'''
        self._loop.run_until_complete(self.init_websockets(
            live_websocket, demo_websocket, mdlive_websocket
        ))
        self._loop.run_until_complete(self.authorize(auth, auto_renew))
        try:
            self._loop.run_forever()
        except KeyboardInterrupt:
            for task in asyncio.all_tasks(loop=self._loop):
                task.cancel()
            self._loop.run_until_complete(self.close())
            self._loop.close()

    # -Properties: Private
    @property
    def _websockets(self) -> tuple[WebSocket]:
        websockets = []
        if self._live:
            websockets.append(self._live)
        if self._demo:
            websockets.append(self._demo)
        if self._mdlive:
            websockets.append(self._mdlive)
        if self._mddemo:
            websockets.append(self._mddemo)
        if self._mdreplay:
            websockets.append(self._mdreplay)
        if websockets:
            return tuple(websockets)
        return None

    @property
    def _websockets_account(self) -> tuple[WebSocket]:
        websockets = []
        if self._live:
            websockets.append(self._live)
        if self._demo:
            websockets.append(self._demo)
        if websockets:
            return tuple(websockets)
        return None

    @property
    def _websockets_market(self) -> tuple[WebSocket]:
        websockets = []
        if self._mdlive:
            websockets.append(self._mdlive)
        if self._mddemo:
            websockets.append(self._mddemo)
        if self._mdreplay:
            websockets.append(self._mdreplay)
        if websockets:
            return tuple(websockets)
        return None

    # -Properties: Authenticated
    @property
    def authenticated(self) -> bool:
        if not self._session.authenticated.is_set():
            return False
        for websocket in self._websockets:
            if not websocket.authenticated.is_set():
                return False
        return True
