##-----------------------------##
## Tradovate PyAPI             ##
## Written By: Ryan Smith      ##
##-----------------------------##
## URL Endpoints               ##
##-----------------------------##

## Constants
# -Base URLs
_domains = (
    "://live.tradovateapi.com/v1/",     # -Live Account Functionality
    "://demo.tradovateapi.com/v1/",     # -Demo Account Functionality
    "://md.tradovateapi.com/v1/",       # -Live Market Functionality
    #"://md-demo.tradovateapi.com/v1/",  # -Demo Market Functionality
    #"://replay.tradovateapi.com/v1",    # -Replay Market Functionality
)
http_base_demo, http_base_live, http_base_market, http_base_market_demo = [
    f"https{domain}" for domain in _domains
]
wss_base_demo, wss_base_live, wss_base_market, wss_base_market_demo = [
    f"wss{domain}websocket" for domain in _domains
]
# -Authorization
# -HTTP[Live Only]
http_base_auth = http_base_live + "auth/"
http_auth_oauth = http_base_auth + "oauthtoken"
http_auth_request = http_base_auth + "accesstokenrequest"
http_auth_renew = http_base_auth + "renewaccesstoken"
http_auth_me = http_base_auth + "me"
# -Websocket
wss_base_auth = "authorize"
