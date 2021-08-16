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
from client import Client
from utils.account import auth_dict

## Variables
scalp_mechanic = Client()

## Functions

## Body
scalp_mechanic.run(auth_dict)
