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
from client import Client
from utils.account import auth_dict

## Variables
scalp_mechanic = Client()

## Functions

## Body
scalp_mechanic.run(auth_dict)
