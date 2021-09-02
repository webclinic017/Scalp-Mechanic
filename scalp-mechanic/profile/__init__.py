##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Tradovate Profile             ##
##-------------------------------##

## Imports
from __future__ import annotations

from utils.session import Session


## Classes
class Profile:
    """Tradovate Profile Class"""

    # -Constructor
    def __init__(self, session: Session) -> Profile:
        self.id: int = 0
        self._session: Session = session

    # -Instance Methods
    async def authorize(self, dict_: dict[str, str]) -> bool:
        ''''''
        self.id = await self._session.request_access_token(dict_)
        return self._session.authenticated

    async def me(self) -> None:
        ''''''
        pass
