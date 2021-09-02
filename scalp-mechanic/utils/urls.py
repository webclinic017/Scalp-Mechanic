##-----------------------------##
## Tradovate PyAPI             ##
## Written By: Ryan Smith      ##
##-----------------------------##
## URL Endpoints               ##
##-----------------------------##

## Constants
# -Base URLS
base_live = "https://live.tradovateapi.com/v1/"
base_demo = "https://demo.tradovateapi.com/v1/"
base_market_live = "wss://md.tradovateapi.com/v1/websocket"
base_market_demo = "wss://md-demo.tradovateapi.com/v1/websocket"
# -Authorization
base_auth = base_live + "auth/"
auth_oauth = base_auth + "oauthtoken"
auth_request = base_auth + "accesstokenrequest"
auth_renew = base_auth + "renewaccesstoken"
auth_me = base_auth + "me"
auth_websocket = "authorize"
