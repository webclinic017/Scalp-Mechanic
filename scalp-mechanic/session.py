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
from asyncio import AbstractEventLoop, TimerHandle
from datetime import datetime
from typing import Optional

import aiohttp
from aiohttp import (
    ClientSession, ClientResponse,
    ClientWebSocketResponse
)

from utils import timestamp_to_datetime, urls
from utils.errors import (
    LoginInvalidException, LoginCaptchaException, WebsocketException
)


## Classes
class Session:
    """Tradovate Session Class"""

    # -Constructor
    def __init__(self, *, loop: Optional[AbstractEventLoop] = None) -> Session:
        self.authenticated: bool = False
        self.token_expiration: Optional[datetime] = None
        self.__session: Optional[ClientSession] = None
        self._heartbeat_handle: Optional[TimerHandle] = None
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
            raise WebsocketException()  # TODO: Better exception
        self._request_number = 0
        self._heartbeat_handle = self.loop.call_at(
            self.loop.time() + 2.5, self._send_heartbeat
        )

    async def __async_del__(self) -> None:
        # TODO: Close method with better control
        if self.__session:
            await self.__session.close()
            await self.__socket.close()

    # -Instance Methods: Private
    def _send_heartbeat(self) -> None:
        '''Send heartbeat packet through websocket connection'''
        self.loop.create_task(self.__socket.send_str("[]"))
        self._heartbeat_handle = self.loop.call_at(
            self.loop.time() + 2.5, self._send_heartbeat
        )

    async def _send_socket_request(
        self, url: str, query: str = "", body: str = ""
    ) -> None:
        '''Send formatted request string through websocket'''
        req = f"{url}\n{self._request_number}\n{query}\n{body}"
        self._request_number += 1
        self.__socket.send_str(req)

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
        self.token_expiration = timestamp_to_datetime(res_dict['expirationTime'])
        self.__session.headers.update({
            'AUTHORIZATION': "Bearer " + res_dict['accessToken']
        })
        return res_dict

    # -Instance Methods
    async def request_access_token(self, _dict: dict[str, str]) -> None:
        '''Request session authorization'''
        res = await self.__session.post(urls.auth_request, json=_dict)
        res_dict = await self._update_authorization(res)
        # -Market Token
        await self._send_socket_request("authorize", body=res_dict['mdAccessToken'])
        #ws_res = json.loads((await self.__socket.receive()).data[1:])[0] -- one liner
        ws_res = await self.__socket.receive()
        ws_res_dict = json.loads(ws_res.data[1:])[0]
        if ws_res_dict['s'] != 200:
            raise WebsocketException()  # TODO: Better exception
        self.authenticated = True

    async def renew_access_token(self) -> None:
        '''Renew session authorization'''
        res = await self.__session.post(urls.auth_renew)
        await self._update_authorization(res)
