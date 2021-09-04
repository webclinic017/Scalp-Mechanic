##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Session Classes     ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
import logging
from datetime import datetime, timedelta, timezone
from typing import Optional

import aiohttp

from utils import timestamp_to_datetime, urls
from utils.errors import (
    LoginInvalidException, LoginCaptchaException
)
from utils.typing import CredentialAuthDict

## Constants
log = logging.getLogger(__name__)


## Classes
class Session:
    """Tradovate Session"""

    # -Constructor
    def __init__(
        self, *, loop: Optional[asyncio.AbstractEventLoop] = None
    ) -> Session:
        self.authenticated: bool = False
        self.token_expiration: Optional[datetime] = None
        self._loop = loop if loop else asyncio.get_event_loop()
        self._aiosession: Optional[aiohttp.ClientSession] = None
        self._loop.create_task(self.__ainit__())

    # -Dunder Methods
    async def __ainit__(self) -> None:
        self._aiosession = aiohttp.ClientSession(loop=self._loop, raise_for_status=True)

    # -Instance Methods: Private
    async def _update_authorization(
        self, res: aiohttp.ClientResponse
    ) -> dict[str, str]:
        '''Updates Session authorization fields'''
        res_dict = await res.json()
        # -Invalid Credentials
        if 'errorText' in res_dict:
            self.authenticated = False
            raise LoginInvalidException(res_dict['errorText'])
        # -Captcha Limiting
        if 'p-ticket' in res_dict:
            self.authenticated = False
            raise LoginCaptchaException(
                res_dict['p-ticket'], int(res_dict['p-time']),
                bool(res_dict['p-captcha'])
            )
        # -Access Token
        log.debug("Authenticated session")
        self.authenticated = True
        self.token_expiration = timestamp_to_datetime(res_dict['expirationTime'])
        self._aiosession.headers.update({
            'AUTHORIZATION': "Bearer " + res_dict['accessToken']
        })
        return res_dict

    # -Instance Methods: Public
    async def close(self) -> None:
        self.authenticated = False
        await self._aiosession.close()

    async def get(self, url, *args, **kwargs) -> dict[str, str]:
        res = await self._aiosession.request('GET', url, *args, **kwargs)
        return await res.json()

    async def renew_access_token(self) -> None:
        '''Renew Session authorization'''
        log.debug("Renewing session token")
        res = await self._aiosession.post(urls.http_auth_renew)
        await self._update_authorization(res)

    async def request_access_token(self, auth: CredentialAuthDict) -> int:
        '''Request Session authorization'''
        log.debug("Requesting session token")
        res = await self._aiosession.post(urls.http_auth_request, json=auth)
        res_dict = await self._update_authorization(res)
        # -Handle Websockets
        return res_dict['userId']

    # -Property
    @property
    def loop(self) -> asyncio.AbstractEventLoop:
        return self._loop

    @property
    def token_duration(self) -> timedelta:
        return self.token_expiration - datetime.now(timezone.utc)

    @property
    def token_expired(self) -> bool:
        return datetime.now(timezone.utc) >= self.token_expiration


class WebSocket:
    """Tradovate WebSocket"""

    # -Constructor
    def __init__(self) -> WebSocket:
        pass
