##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Client Class                  ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta
from typing import Optional

import aiohttp

from utils.account import auth_dict


## Classes
class Client:
    # -Constructor
    def __init__(self) -> Client:
        # -Authentication
        self.authenticated: bool = False
        self.market_token: Optional[str] = None
        self.access_expiration: Optional[datetime] = None
        # -Session
        self.session: Optional[aiohttp.ClientSession] = None
        # -Loop
        self.loop = asyncio.new_event_loop()

    # -Dunder Methods
    def __del__(self) -> None:
        if self.session is not None:
            self.loop.run_until_complete(self.session.close())

    # -Instance Methods: Async Setup
    async def _init(self, access_token: Optional[str] = None):
        '''Initialize async loop'''
        self.session = aiohttp.ClientSession()
        if access_token:
            pass
        else:
            await self.request_access_token()
        await self.me()

    # -Instance Methods: Authorization
    async def request_access_token(self) -> bool:
        '''Request access token from authorization code'''
        url = "https://demo.tradovateapi.com/v1/auth/accesstokenrequest"
        res = await self.session.post(url, json=auth_dict)
        if res.status != 200:
            self.authenticated = False
            return False
        res = await res.json()
        # -Expiration time
        self.access_expiration = datetime.strptime(
            res['expirationTime'], "%Y-%m-%dT%H:%M:%S.%f%z"
        )
        # -Get tokens
        self.session.headers.update({
            'AUTHORIZATION': "Bearer " + res['accessToken']
        })
        print(res)

    async def renew_access_token(self) -> bool:
        ''''''
        pass

    async def me(self) -> None:
        ''''''
        pass

    # -Instance Methods
    def run(self, access_token: Optional[str] = None) -> None:
        ''''''
        self.loop.run_until_complete(self._init(access_token))
