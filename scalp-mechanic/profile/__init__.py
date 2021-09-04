##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Profile Class       ##
##-------------------------------##

## Imports
from __future__ import annotations

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

    # -Instance Methods: Public
    async def authorize(self, authorization: CredentialAuthDict) -> bool:
        '''Initialize Profile authorization'''
        self.id = await self._session.request_access_token(authorization)
        return self.authenticated

    async def me(self) -> dict[str, str]:
        '''Profile details'''
        return await self._session.get(urls.http_auth_me)

    # -Property
    @property
    def authenticated(self) -> bool:
        return self._session.authenticated
