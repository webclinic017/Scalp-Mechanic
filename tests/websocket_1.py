##-------------------------------##
## [Tradovate] Scalp-Mechanic    ##
## Written By: Ryan Smith        ##
##-------------------------------##
## Test 1: Websockets            ##
##-------------------------------##

## Imports
import asyncio
import json

import aiohttp

## Constants
access: str = ""
market: str = ""
auth: dict[str, str] = {
}


## Functions
async def main():
    global access, market
    session = aiohttp.ClientSession()
    # -Authentication
    if access:
        session.headers.update({
            'AUTHORIZATION': "Bearer " + access
        })
    else:
        url = "https://live.tradovateapi.com/v1/auth/accesstokenrequest"
        res = await session.post(url, json=auth)
        res = await res.json()
        session.headers.update({
            'AUTHORIZATION': "Bearer " + res['accessToken']
        })
        access = res['accessToken']
        market = res['mdAccessToken']
        print(access)
        print(market)

    # -Me Test
    res = await session.get("https://live.tradovateapi.com/v1/auth/me")
    print(res.status)
    res = await res.json()
    print(res)

    # -Socket Test
    ws_handle = await session.ws_connect("wss://md.tradovateapi.com/v1/websocket")
    ws_handshake = await ws_handle.receive_str()
    if ws_handshake == 'o':
        await ws_handle.send_str(f'authorize\n1\n\n{market}')
        msg = await ws_handle.receive()
        print(msg)
        await ws_handle.send_str('md/subscribeQuote\n2\n\n{"symbol" : "MESU1"}')
        msg = await ws_handle.receive()
        print(msg)
        await ws_handle.send_str('md/subscribeQuote\n2\n\n{"symbol" : "MNQU1"}')
        msg = await ws_handle.receive()
        print(msg)
        #await ws_handle.send_str('md/subscribeDOM\n2\n\n{"symbol" : "MESU1"}')
        #msg = await ws_handle.receive()
        #print(msg)
        async for msg in ws_handle:
            await ws_handle.send_str("[]")
            print(msg)
        res = await session.get("https://live.tradovateapi.com/v1/auth/me")
        res = await res.json()
        print(res)

    # -Close
    await session.close()


## Body
asyncio.run(main())
