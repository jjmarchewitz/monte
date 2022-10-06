from alpaca_trade_api import AsyncRest, TimeFrame, TimeFrameUnit
import trio
import asks

KEY_ID = "PK9SGOA95VQ5DLDHA1BX"
SECRET_KEY = "4TUj95KLyJuq4sZfK3Pt1uSrLI6efUrnWRG7KZDJ"


async def get_barz(symbol, out_dict, headers, params):
    out_dict[symbol] = await asks.get(
        f"https://paper-api.alpaca.markets/v2/stocks/{symbol}/bars",
        headers=headers,
        json=params,
        follow_redirects=False
        # data=opts
    )


async def amain():

    dict_a = {}

    # payload = {
    #     "adjustment": 'raw',
    #     "start": "2021-09-09",
    #     "end": "2021-10-09",
    #     "timeframe": TimeFrame.Hour,
    #     "limit": 1000,
    # }

    # with asks.Session(base_location="https://paper-api.alpaca.markets", endpoint="") as s:
    #     pass

    symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA"]

    headers = {
        "APCA-API-KEY-ID": KEY_ID,
        "APCA-API-SECRET-KEY": SECRET_KEY
    }

    params = {
        "adjustment": "raw",
        "start": "2021-09-09",
        "end": "2021-10-09",
        "timeframe": str(TimeFrame(1, TimeFrameUnit.Hour)),
        "limit": 1000,
    }

    # opts = {
    #     'allow_redirects': False,
    # }

    await get_barz(symbols[0], dict_a, headers, params)

    # async with trio.open_nursery() as n:
    #     for symbol in symbols:
    #         n.start_soon(get_barz, symbol, dict_a, headers, params)

    breakpoint()
    # dict_a["AAPL"] = await arest.get_bars_async("AAPL", "2021-09-09", "2021-10-09", TimeFrame.Minute)
    # dict_a["GOOG"] = await arest.get_bars_async("GOOG", "2021-09-09", "2021-10-09", TimeFrame.Day)
    # dict_a["IVV"] = await arest.get_bars_async("IVV", "2021-09-09", "2021-10-09", TimeFrame.Day)
    # dict_a["NVDA"] = await arest.get_bars_async("NVDA", "2021-09-09", "2021-10-09", TimeFrame.Day)
    # dict_a["AMD"] = await arest.get_bars_async("AMD", "2021-09-09", "2021-10-09", TimeFrame.Day)
    # dict_a["INTC"] = await arest.get_bars_async("INTC", "2021-09-09", "2021-10-09", TimeFrame.Day)

    # async with trio.open_nursery() as nursery:
    #     nursery.start_soon(barz, arest, "AAPL", dict_a)


if __name__ == "__main__":
    trio.run(amain)
