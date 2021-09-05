##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Profile Class       ##
##-------------------------------##

## Imports
from __future__ import annotations
from typing import Optional

import aiohttp

from .account import Account
from .session import Session
from utils.typing import CredentialAuthDict

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
        self, *, id_: Optional[int] = None, ids: Optional[list[int]] = None
    ) -> Account | list[Account]:
        '''Returns account or list of accounts from ID url endpoint'''
        # -URLs
        if id_:
            live_url = urls.get_account(urls.ENDPOINT.LIVE, id_=id_)
            demo_url = urls.get_account(urls.ENDPOINT.DEMO, id_=id_)
        elif ids:
            accounts = []
            live_url = urls.get_accounts(urls.ENDPOINT.LIVE, ids=ids, list_=False)
            demo_url = urls.get_accounts(urls.ENDPOINT.DEMO, ids=ids, list_=False)
        # -Live
        try:
            account = await self._session.get(live_url)
        except aiohttp.ClientResponseError:
            pass
        else:
            if id_:
                account['endpoint'] = urls.ENDPOINT.LIVE
                return account
            for acc in account:
                acc['endpoint'] = urls.ENDPOINT.LIVE
                accounts.append(acc)
        # -Demo
        try:
            account = await self._session.get(demo_url)
        except aiohttp.ClientResponseError:
            pass
        else:
            if id_:
                account['endpoint'] = urls.ENDPOINT.DEMO
                return account
            for acc in account:
                acc['endpoint'] = urls.ENDPOINT.DEMO
                accounts.append(acc)
        # -Return
        if ids and accounts:
            return accounts
        return None

    async def _get_full_account_list(self) -> list[Account]:
        '''Returns full list of accounts dictionary - live+demo'''
        accounts = []
        # -Live
        url = urls.get_accounts(urls.ENDPOINT.LIVE)
        for account in await self._session.get(url):
            account['endpoint'] = urls.ENDPOINT.LIVE
            accounts.append(account)
        # -Demo
        url = urls.get_accounts(urls.ENDPOINT.DEMO)
        for account in await self._session.get(url):
            account['endpoint'] = urls.ENDPOINT.DEMO
            accounts.append(account)
        return accounts

    # -Instance Methods: Public
    async def authorize(self, authorization: CredentialAuthDict) -> bool:
        '''Initialize Profile authorization'''
        self.id = await self._session.request_access_token(authorization)
        return self.authenticated

    async def get_account(
        self, *, id_: Optional[int] = None,
        name: Optional[str] = None,
        nickname: Optional[str] = None
    ) -> Account:
        '''Get account by id, name, or nickname'''
        account = None
        if id_:
            account = await self._get_account_by_ids(id_=id_)
            if account:
                return account
            return None
        for account_ in await self._get_full_account_list():
            if account_['name'] == name:
                account = account_
                break
            elif 'nickname' in account_ and account_['nickname'] == nickname:
                account = account_
                break
        if account:
            return account
        return None

    async def get_accounts(
        self, *, ids: Optional[list[int]] = None,
        names: Optional[list[str]] = None,
        nicknames: Optional[list[str]] = None
    ) -> list[Account]:
        '''Get accounts by ids, names, or nicknames or full account list'''
        accounts = []
        if ids:
            accounts = await self._get_account_by_ids(ids=ids)
            if accounts:
                return accounts
            return None
        for account in await self._get_full_account_list():
            if names:
                if account['name'] in names:
                    accounts.append(account)
            elif nicknames:
                if 'nickname' in account and account['nickname'] in nicknames:
                    accounts.append(account)
            else:
                accounts.append(account)
        # -Create Accounts
        if accounts:
            return accounts
        return None

    async def me(self) -> dict[str, str]:
        '''Profile details'''
        return await self._session.get(urls.http_auth_me)

    # -Property
    @property
    def authenticated(self) -> bool:
        return self._session.authenticated

    @property
    def session(self) -> Session:
        return self._session
