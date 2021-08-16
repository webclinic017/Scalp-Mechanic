##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##

## Imports
from __future__ import annotations
import asyncio

from session import Session


## Classes
class Client:
    """Scalp Mechanic Client"""

    # -Constructor
    def __init__(self) -> Client:
        self.id: int = 0
        self.loop: asyncio.AbstractEventLoop = asyncio.new_event_loop()
        self.session: Session = Session(loop=self.loop)

    # -Dunder Methods
    def __del__(self) -> None:
        del self.session

    # -Instance Methods
    def run(self, _dict: dict[str, str]) -> None:
        ''''''
        self.loop.run_until_complete(self.session.request_access_token(_dict))
