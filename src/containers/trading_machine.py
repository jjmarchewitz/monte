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


class TradingMachine():
    def __init__(
            self, trading_api, market_data_api, start_date, end_date,
            time_frame=TimeFrame.Minute):
        self.trading_api = trading_api
        self.market_data_api = market_data_api
        self.start_date = start_date
        self.end_date = end_date

        # The only supported time frames for this class are minutes, hours, and days.
        self.time_frame = time_frame

        # Create a list of all market days in range with start and end times
        self.market_days = []
        self._generate_market_day_list()

        # Pairs of algorithms and portfolios
        self.alg_port_pairs = {}

    def _generate_market_day_list(self):

        # Get a list of all market days between start_date and end_date, including their
        # open and close times
        raw_market_days = self.trading_api.get_calendar(self.start_date, self.end_date)

        for day in raw_market_days:

            # Grab the DST-aware timezone object for eastern time
            timezone = pytz.timezone("America/New_York")

            # Create a datetime object for the opening time with the timezone info attached
            open_time = timezone.localize(datetime(
                day.date.year,
                day.date.month,
                day.date.day,
                day.open.hour,
                day.open.minute
            ))

            # Create a datetime object for the closing time with the timezone info attached
            close_time = timezone.localize(datetime(
                day.date.year,
                day.date.month,
                day.date.day,
                day.close.hour,
                day.close.minute
            ))

            # Convert the opening and closing times to ISO-8601
            # Literally dont even fucking ask me how long it took to get the data in the
            # right format for this to work.
            open_time = open_time.isoformat()
            close_time = close_time.isoformat()

            # Create a MarketDay object with the right open/close times and append it to
            # the list of all such MarketDay objects within the span between start_date and
            # end_date
            market_day = MarketDay(open_time, close_time)
            self.market_days.append(market_day)
