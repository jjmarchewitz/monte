"""
The data manager will handle interactions between the trading machine/related objects and any
asset data - either from downloaded CSVs in the top-level data/ folder or from Alpaca itself.
"""

from alpaca_trade_api import TimeFrame
import trio


def get_dataframe(alpaca_api, symbol, start_date, end_date, time_frame=TimeFrame.Hour):

    breakpoint()

    return alpaca_api.market_data.get_bars(symbol, time_frame, start_date, end_date).df
