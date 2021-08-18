##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Session Class                 ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
import json
from asyncio import (
    AbstractEventLoop, Task, TimerHandle
)
from datetime import (
    datetime, timedelta, timezone
)
from typing import Optional

import aiohttp
from aiohttp import (
    ClientSession, ClientResponse,
    ClientWebSocketResponse
)

from utils import (
    timestamp_to_datetime, urls
)
from utils.errors import (
    LoginInvalidException, LoginCaptchaException, WebsocketException
)


## Classes
class Session:
    """Tradovate Session Class"""

    # -Constructor
    def __init__(
        self, *, loop: Optional[AbstractEventLoop] = None,
        authorization_renewal: bool = True
    ) -> Session:
        self.authenticated: bool = False
        self._session: Optional[ClientSession] = None
        self._socket: Optional[ClientWebSocketResponse] = None
        self._token_expiration: Optional[datetime] = None
        self._authorization_renewal: bool = authorization_renewal
        self._authorization_handle: Optional[TimerHandle] = None
        self._request_number: int = 0
        self._heartbeat_handle: Optional[TimerHandle] = None
        self._loop: AbstractEventLoop = loop if loop else asyncio.get_event_loop()
        self._loop.run_until_complete(self.__async_init__())

    # -Dunder Methods
    async def __async_init__(self) -> None:
        self._session = aiohttp.ClientSession(loop=self._loop, raise_for_status=True)
        self._socket = await self._session.ws_connect(urls.base_market_live)
        if await self._socket.receive_str() != 'o':
            raise WebsocketException()  # TODO: Better exception
        self._timer_heartbeat()

    # -Instance Methods: Private
    def _send_authorization(self) -> None:
        '''Send authorization renewal request through session'''
        print(f"Current token: {self._session.headers['AUTHORIZATION']}")
        task = self._loop.create_task(self.renew_access_token())
        task.add_done_callback(self._timer_authorization)

    def _send_heartbeat(self) -> None:
        '''Send heartbeat packet through websocket'''
        self._loop.create_task(self._socket.send_str("[]"))
        self._timer_heartbeat()

    async def _send_socket_request(
        self, url: str, query: str = "", body: str = ""
    ) -> None:
        '''Send formatted request string through websocket'''
        req = f"{url}\n{self._request_number}\n{query}\n{body}"
        self._request_number += 1
        await self._socket.send_str(req)

    def _timer_authorization(self, task: Optional[Task] = None) -> None:
        '''Timer handler for authorization renewal'''
        self._authorization_handle = self._loop.call_later(
            self.get_token_duration(timedelta(minutes=5)).total_seconds(),
            self._send_authorization
        )

    def _timer_heartbeat(self) -> None:
        '''Timer handler for heartbeat'''
        self._heartbeat_handle = self._loop.call_later(
            2.5, self._send_heartbeat
        )

    async def _update_authorization(self, res: ClientResponse) -> dict[str, str]:
        '''Set authorization for active session'''
        res_dict = await res.json()
        if 'errorText' in res_dict:
            raise LoginInvalidException(res_dict['errorText'])
        elif 'p-ticket' in res_dict:
            raise LoginCaptchaException(
                res_dict['p-ticket'],
                int(res_dict['p-time']),
                bool(res_dict['p-captcha'])
            )
        # -Access Token
        self._token_expiration = timestamp_to_datetime(res_dict['expirationTime'])
        self._session.headers.update({
            'AUTHORIZATION': "Bearer " + res_dict['accessToken']
        })
        return res_dict

    # -Instance Methods
    async def close(self) -> None:
        if not self._session:
            return None

        await self._socket.close()
        await self._session.close()

    async def get(self, url: str, *args, **kwargs) -> dict[str, str]:
        res = await self._session.request('GET', url, *args, **kwargs)
        return await res.json()

    def get_token_duration(self, offset: Optional[timedelta] = None) -> timedelta:
        '''Get timedelta of remaining time until token is expired'''
        time_remaining = self._token_expiration - datetime.now(timezone.utc)
        if offset:
            return time_remaining - offset
        return time_remaining

    def is_token_expired(self, offset: Optional[timedelta] = None) -> bool:
        '''Returns true if current time in UTC is past the token expiration datetime'''
        time = datetime.now(timezone.utc)
        if offset:
            return time >= self._token_expiration - offset
        return time >= self._token_expiration

    async def post(self, url: str, *args, **kwargs) -> dict[str, str]:
        res = await self._session.request('POST', url, *args, **kwargs)
        return await res.json()

    async def renew_access_token(self) -> None:
        '''Renew session authorization'''
        res = await self._session.post(urls.auth_renew)
        await self._update_authorization(res)

    async def request_access_token(self, dict_: dict[str, str]) -> None:
        '''Request session authorization'''
        res = await self._session.post(urls.auth_request, json=dict_)
        res_dict = await self._update_authorization(res)
        # -Market Token
        await self._send_socket_request("authorize", body=res_dict['mdAccessToken'])
        ws_res = await self._socket.receive()
        ws_res_dict = json.loads(ws_res.data[1:])[0]
        if ws_res_dict['s'] != 200:
            raise WebsocketException()  # TODO: Better exception
        self.authenticated = True
        if self._authorization_renewal:
            self._timer_authorization()
