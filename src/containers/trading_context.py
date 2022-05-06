# DEFINITION: The "trading context" is meant to represent the timeline that a portfolio
# and trading algorithm are being run on. This encompasses backtesting (testing on
# historical data) as well as running an algorithm live.


from enum import Enum
from alpaca_trade_api import TimeFrame
from dataclasses import dataclass
from datetime import date, time, datetime
import pytz


@dataclass
class MarketDay():
    open_time_iso: str
    close_time_iso: str


class TradingContext():
    def __init__(
            self, trading_api, market_data_api, start_date, end_date,
            time_frame=TimeFrame.Minute):
        self.trading_api = trading_api
        self.market_data_api = market_data_api
        self.start_date = start_date
        self.end_date = end_date
        self.time_frame = time_frame
        self.market_days = []

        # Create a list of all market days in range with start and end times
        self._populate_all_market_days()

        # Pairs of algorithms and portfolios
        self.alg_port_pairs = {}

    def _populate_all_market_days(self):
        raw_market_days = self.trading_api.get_calendar(self.start_date, self.end_date)

        for day in raw_market_days:

            timezone = pytz.timezone("America/New_York")

            open_time = timezone.localize(datetime(
                day.date.year,
                day.date.month,
                day.date.day,
                day.open.hour,
                day.open.minute
            ))

            close_time = timezone.localize(datetime(
                day.date.year,
                day.date.month,
                day.date.day,
                day.close.hour,
                day.close.minute
            ))

            open_time = open_time.isoformat()
            close_time = close_time.isoformat()

            market_day = MarketDay(open_time, close_time)
            self.market_days.append(market_day)
