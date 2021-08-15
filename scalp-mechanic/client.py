##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio

from utils.session import Session


## Classes
class Client:
    """Scalp Mechanic Client"""

    # -Constructor
    def __init__(self) -> Client:
        # -Account
        self.id: int = 0
        # -Async
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.session: Session = Session(loop=self.loop)
        self.loop.run_until_complete(self.__async_init__())

    # -Dunder Methods
    def __del__(self) -> None:
        del self.session

    async def __async_init__(self) -> None:
        pass

    # -Instance Methods
    def run(self, _dict: dict[str, str]) -> None:
        pass
