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
        print("On Connect")

    async def on_ready(self) -> None:
        print("On Ready")

    async def on_alert(self, alert) -> None:
        print("On Alert")
        print(f"Alert Data: {alert}")

    async def on_market_update(self, market) -> None:
        print("On Market Update")
        print(f"Market Data: {market}")

    async def on_dom_update(self, dom) -> None:
        print("On DOM Update")
        print(f"DOM Data: {dom}")

    async def on_chart_update(self, chart) -> None:
        print("On Chart Update")
        print(f"Chart Data: {chart}")

    async def on_histogram_update(self, histogram) -> None:
        print("On Histogram Update")
        print(f"Histogram Data: {histogram}")

    async def on_order_update(self, order) -> None:
        print("On Order Update")
        print(f"Order Data: {order}")


## Body
scalp_mechanic = Scalp_Mechanic()
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
scalp_mechanic.run(authorization_dict)
