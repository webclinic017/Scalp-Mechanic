##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Utilities                     ##
##-------------------------------##

## Imports
from datetime import datetime


## Functions
def timestamp_to_datetime(
    timestamp: str, timestring: str = "%Y-%m-%dT%H:%M:%S.%f%z"
) -> datetime:
    """"""
    return datetime.strptime(timestamp, timestring)
