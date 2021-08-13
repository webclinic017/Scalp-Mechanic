##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Client Class                  ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio
from datetime import datetime, timedelta, timezone
from typing import Optional

import aiohttp

import utils
from utils import urls
from utils.account import auth_dict


## Classes
class Client:
    """Tradovate Client"""

    # -Constructor
    def __init__(self) -> Client:
        # -Client
        self.id: int = 0
        self.loop = asyncio.new_event_loop()
        # -Session
        self.session = Client.Session(self.loop)

    # -Instance Methods: Public
    def run(self) -> None:
        '''Runs client async loop'''
        self.loop.run_until_complete(self._init())

    # -Instance Methods: Private
    async def _init(self) -> None:
        '''Initializes client async'''
        self.id = await self.session.request_access_token()

    # -Sub-Classes
    class Session:
        """Tradovate Session"""

        # -Constructor
        def __init__(self, loop: asyncio.AbstractEventLoop) -> Client.Session:
            # -Authentication
            self.authenticated: bool = False
            self.market_token: Optional[str] = None
            self.expiration: Optional[datetime] = None
            self.loop: asyncio.AbstractEventLoop = loop
            # -Session Client
            self._session: Optional[aiohttp.ClientSession] = None
            self.loop.run_until_complete(self._init())

        # -Dunder Methods
        def __del__(self) -> None:
            if self._session:
                self.loop.run_until_complete(self._session.close())

        # -Instance Methods: Authorization
        def is_expired(self, offset: Optional[timedelta] = None) -> bool:
            '''Returns if token has expired with optional offset'''
            d = datetime.now(timezone.utc)
            if offset:
                return d >= self.expiration - offset
            return d >= self.expiration

        async def request_access_token(self) -> bool:
            '''Request access token'''
            res = await self._session.post(urls.auth_request, json=auth_dict)
            # -Invalid Request
            if res.status != 200:
                self.authenticated = False
                return None
            res = await res.json()
            # -Invalid Credentials
            if 'errorText' in res:
                self.authenticated = False
                return None
            # -Valid Credentials
            self.authenticated = True
            self.id = res['userId']
            # -Expiration time
            self.expiration = utils.timestamp_to_datetime(res['expirationTime'])
            # -Get tokens
            self._session.headers.update({
                'AUTHORIZATION': "Bearer " + res['accessToken']
            })
            self.market_token = res['mdAccessToken']
            print(res['accessToken'])
            print(res['mdAccessToken'])
            return res['userId']

        async def renew_access_token(self) -> bool:
            '''Renew access token'''
            res = await self._session.post(urls.auth_renew)
            # -Invalid Request
            if res.status != 200:
                self.authenticated = False
                return False
            res = await res.json()
            # -Invalid Credentials
            if 'errorText' in res:
                self.authenticated = False
                return False
            # -Valid Credentials
            self.authenticated = True
            # -Expiration time
            self.expiration = utils.timestamp_to_datetime(res['expirationTime'])
            # -Get tokens
            self._session.headers.update({
                'AUTHORIZATION': "Bearer " + res['accessToken']
            })
            self.market_token = res['mdAccessToken']

        # -Instance Methods: Request
        async def request(
            self, method: str, url: str, *args, **kwargs
        ) -> aiohttp.ClientResponse:
            '''Internal request method with expire check'''
            if self.is_expired(timedelta(minutes=30)):
                await self.renew_access_token()
            if self.authenticated:
                return await self._session.request(method, url, *args, **kwargs)

        async def get(self, url, *args, **kwargs) -> aiohttp.ClientResponse:
            '''Get request'''
            return await self.request('GET', url, *args, **kwargs)

        async def post(self, url, *args, **kwargs) -> aiohttp.ClientResponse:
            '''Post request'''
            return await self.request('POST', url, *args, **kwargs)

        # -Instance Methods: Private
        async def _init(self) -> None:
            '''Initializes aiohttp session async'''
            self._session = aiohttp.ClientSession()
