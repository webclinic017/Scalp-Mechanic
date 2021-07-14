##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
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
        self.access_expiration: Optional[datetime] = None
        self.refresh_expiration: Optional[datetime] = None
        # -Session
        self.session: Optional[aiohttp.ClientSession] = None
        # -Loop
        self.loop = asyncio.new_event_loop()

    # -Dunder Methods
    def __del__(self) -> None:
        if self.session is not None:
            self.loop.run_until_complete(self.session.close())

    # -Instance Methods: Async Setup
    async def init(self):
        ''''''
        self.session = aiohttp.ClientSession()
        await self.request_access_token()

    # -Instance Methods: Authorization
    async def request_access_token(self) -> bool:
        '''Request access token from authorization code'''
        url = "https://demo.tradovateapi.com/v1/auth/accesstokenrequest"
        res = await self.session.post(url, json=auth_dict)
        if res.status != 200:
            self.authenticated = False
            return False
        res = await res.json()

    def run(self) -> None:
        ''''''
        self.loop.run_until_complete(self.init())


## Body
scalp_mechanic = Client()
scalp_mechanic.run()
