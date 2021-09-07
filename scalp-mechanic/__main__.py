##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##

"""
$200/day + commissions

004 points ES  -- $4.64/trade
040 points MES -- $1.60/trade
010 points NQ  -- $4.64/trade
100 points MNQ -- $1.60/trade
"""

## Imports
#import logging
import logging
from configparser import ConfigParser
from datetime import date

from client import Client

## Constants
logging.basicConfig(
    filename=f"logs/{date.today()}.log",
    encoding='utf-8',
    format="[%(asctime)s:%(msecs)d](%(name)s)%(levelname)s: %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.DEBUG
)
log = logging.getLogger("Scalp-Mechanic")
credentials = ConfigParser()


## Classes
class Scalp_Mechanic(Client):
    """Scalp-Mechanic Tradovate Client"""

    async def on_connect(self) -> None:
        print("Connected Successfully")


## Body
client = Scalp_Mechanic()
credentials.read("account.ini")
authorization_dict = {
    'name': credentials['authentication']['username'],
    'password': credentials['authentication']['password'],
    'deviceId': credentials['application']['device_id'],
    'cid': credentials['authentication']['cid'],
    'sec': credentials['authentication']['security_key'],
    'appID': credentials['application']['name'],
    'appVersion': credentials['application']['version'],
}
client.run(authorization_dict)
