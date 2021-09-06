##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Profile Class       ##
##-------------------------------##

## Imports
from __future__ import annotations
from typing import AsyncGenerator

import aiohttp

from .account import Account
from .session import Session
from utils.typing import CredentialAuthDict, MeAuthDict

from utils import urls


## Classes
class Profile:
    """Tradovate Profile"""

    # -Constructor
    def __init__(self, session: Session) -> Profile:
        self.id: int = 0
        self._session = session

    # -Instance Methods: Private
    async def _get_account_by_ids(
        self, *, id_: int | None = None, ids: list[int] | None = None
    ) -> Account | tuple[Account]:
        '''Returns account or list of accounts from ID url endpoint'''
        # -TODO: DRY
        # -URLs
        if id_ is not None:
            live_url = urls.get_account(urls.ENDPOINT.LIVE, id_=id_)
            demo_url = urls.get_account(urls.ENDPOINT.DEMO, id_=id_)
        else:
            accounts = []
            live_url = urls.get_accounts(urls.ENDPOINT.LIVE, ids=ids)
            demo_url = urls.get_accounts(urls.ENDPOINT.DEMO, ids=ids)
        # -Live
        try:
            account = await self._session.get(live_url)
        except aiohttp.ClientResponseError:
            pass
        else:
            if id_:
                return await Account.from_profile(self, account, urls.ENDPOINT.LIVE)
            for acc in account:
                acc = await Account.from_profile(self, acc, urls.ENDPOINT.LIVE)
                accounts.append(acc)
        # -Demo
        try:
            account = await self._session.get(demo_url)
        except aiohttp.ClientResponseError:
            pass
        else:
            if id_:
                return await Account.from_profile(self, account, urls.ENDPOINT.DEMO)
            for acc in account:
                acc = await Account.from_profile(self, acc, urls.ENDPOINT.DEMO)
                accounts.append(acc)
        # -Return
        if ids and accounts:
            return tuple(accounts)
        return None

    async def _get_accounts_by_endpoint(
        self, endpoint: urls.ENDPOINT
    ) -> AsyncGenerator[Account, None]:
        '''Returns full list of accounts from given endpoint'''
        for account in await self._session.get(urls.get_accounts(endpoint)):
            yield await Account.from_profile(self, account, endpoint)

    async def _get_accounts(self) -> AsyncGenerator[Account, None]:
        '''Returns full list of accounts from live+demo endpoints'''
        async for account in self._get_accounts_by_endpoint(urls.ENDPOINT.LIVE):
            yield account
        async for account in self._get_accounts_by_endpoint(urls.ENDPOINT.DEMO):
            yield account

    # -Instance Methods: Public
    async def authorize(self, authorization: CredentialAuthDict) -> bool:
        '''Initialize Profile authorization'''
        self.id = await self._session.request_access_token(authorization)
        return self.authenticated

    async def get_account(
        self, *, id_: int | None = None,
        name: str | None = None, nickname: str | None = None
    ) -> Account | None:
        '''Get account by id, name, or nickname'''
        if id_ is not None:
            return await self._get_account_by_ids(id_=id_)
        async for account in self._get_accounts():
            if account.name == name:
                return account
            elif account.nickname and account.nickname == nickname:
                return account
        return None

    async def get_accounts(
        self, *, ids: list[int] | None = None,
        names: list[str] | None = None, nicknames: list[str] | None = None
    ) -> tuple[Account] | None:
        '''Get accounts by ids, names, or nicknames or full account list'''
        # -TODO: Async Generator?
        if ids:
            return await self._get_account_by_ids(ids=ids)
        if names or nicknames:
            accounts = []
            async for account in self._get_accounts():
                if account.name in names:
                    accounts.append(account)
                elif account.nickname and account.nickname in nicknames:
                    accounts.append(account)
            if accounts:
                return tuple(accounts)
            return None
        else:
            return tuple([account async for account in self._get_accounts()])

    async def me(self) -> MeAuthDict:
        '''Profile details'''
        return await self._session.get(urls.http_auth_me)

    # -Property
    @property
    def authenticated(self) -> bool:
        return self._session.authenticated

    @property
    def session(self) -> Session:
        return self._session
