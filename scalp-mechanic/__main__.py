##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##

"""
$200/day

004 points ES
040 points MES
010 points NQ
100 points MNQ

"""

## Imports
from __future__ import annotations
import asyncio

from utils.session import Session

## Constants


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


## Body
client = Client()
client.run("")
