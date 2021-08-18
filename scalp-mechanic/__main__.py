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
from configparser import ConfigParser

from client import Client

## Constants
account = ConfigParser()
scalp_mechanic = Client()

## Functions

## Body
account.read("account.ini")
authorization = {
    'name': account['authentication']['username'],
    'password': account['authentication']['password'],
    'deviceId': account['application']['device_id'],
    'cid': account['authentication']['cid'],
    'sec': account['authentication']['security_key'],
    'appID': account['application']['name'],
    'appVersion': account['application']['version'],
}
scalp_mechanic.run(authorization)
