import gzip
import json

import asks
import trio
from alpaca_trade_api import TimeFrame, TimeFrameUnit

KEY_ID = ""
SECRET_KEY = ""


async def get_barz(symbol, out_dict, headers, params):

    out_dict[symbol] = []

    while True:
        response = await asks.get(
            f"https://data.alpaca.markets/v2/stocks/{symbol}/bars",
            headers=headers,
            params=params,
            follow_redirects=False
            # data=opts
        )

        if response.status_code == 200:
            body_dict = json.loads(str(gzip.decompress(response.body), 'utf-8'))
        else:
            raise ConnectionError(
                f"Bad response from Alpaca with response code: {response.status_code}")

        out_dict[symbol].extend(body_dict['bars'])

        next_page_token = body_dict['next_page_token']

        if next_page_token:
            params['next_page_token'] = next_page_token
        else:
            break


async def amain():

    dict_a = {}

    symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA"]

    headers = {
        "APCA-API-KEY-ID": KEY_ID,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }

    params = {
        "adjustment": "raw",
        "start": "2021-09-09",
        "end": "2022-10-04",
        "timeframe": str(TimeFrame(1, TimeFrameUnit.Hour)),
        "limit": 10000,
    }

    # await get_barz(symbols[0], dict_a, headers, params)

    async with trio.open_nursery() as n:
        for symbol in symbols:
            n.start_soon(get_barz, symbol, dict_a, headers, params)

    breakpoint()


if __name__ == "__main__":
    trio.run(amain)
