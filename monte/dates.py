##################
# DATE UTILITIES #
##################

from dataclasses import dataclass
from datetime import date, datetime

from alpaca_trade_api import entity
from dateutil.parser import isoparse
from pytz import timezone

from monte.util import AlpacaAPIBundle


@dataclass
class TradingDay():
    """
    A dataclass holding information for a single day the market is open, like the date.
    This dataclass also stores the market open time and close time in the ISO-8601
    format.
    """
    date: date
    open_time: datetime
    close_time: datetime


def get_list_of_trading_days_in_range(alpaca_api: AlpacaAPIBundle,
                                      start_date: str, end_date: str) -> list[TradingDay]:
    """
    Returns a list of days (as TradingDay instances) that U.S. markets are open between the start and end
    dates provided. The result is inclusive of both the start and end dates.

    Args:
        alpaca_api:
            A valid, authenticated util.AlpacaAPIBundle instance.

        start_date:
            The beginning of the range of trading days. The date is represented as YYYY-MM-DD. This follows
            the ISO-8601 date standard.

        end_date:
            The end of the range of trading days. The date is represented as YYYY-MM-DD. This follows the
            ISO-8601 date standard.

    Returns:
        A list of TradingDay instances that represents all of the days that U.S. markets were open.
    """
    raw_market_days = _get_raw_trading_dates_in_range(alpaca_api, start_date, end_date)
    return _get_trading_day_obj_list_from_date_list(raw_market_days)


def _get_raw_trading_dates_in_range(alpaca_api: AlpacaAPIBundle,
                                    start_date: str, end_date: str) -> list[entity.Calendar]:
    """
    This should not be used by end-users.

    Returns a list of days (as alpaca_trade_api.Calendar instances) that U.S. markets are open between the
    start and end dates provided. The result is inclusive of both the start and end dates.

    Args:
        alpaca_api:
            A valid, authenticated util.AlpacaAPIBundle instance.

        start_date:
            The beginning of the range of trading days. The date is represented as YYYY-MM-DD. This follows
            the ISO-8601 date standard.

        end_date:
            The end of the range of trading days. The date is represented as YYYY-MM-DD. This follows the
            ISO-8601 date standard.

    Returns:
        A list of alpaca_trade_api.Calendar instances that represents all of the days that U.S. markets were
        open.
    """
    return alpaca_api.trading.get_calendar(start_date, end_date)


def _get_trading_day_obj_list_from_date_list(
        calendar_instance_list: list[entity.Calendar]) -> list[TradingDay]:
    """
    Converts a list of alpaca_trade_api.Calendar instances into a list of TradingDay instances.

    Args:
        calendar_instance_list:
            A list of alpaca_trade_api.Calendar instances that represents a range of days the market was
            open.

    Returns:
        A list of TradingDay instances that represents a range of days the market was open.
    """
    trading_days = []

    for day in calendar_instance_list:

        # Create a date object (from the datetime library) for the calendar date of the
        # market day
        trading_date = date(
            day.date.year,
            day.date.month,
            day.date.day
        )

        # Grab the DST-aware timezone object for eastern time
        timezone_ET = timezone("America/New_York")

        # Create a datetime object for the opening time with the timezone info attached
        open_time = timezone_ET.localize(datetime(
            day.date.year,
            day.date.month,
            day.date.day,
            day.open.hour,
            day.open.minute
        ))

        # Create a datetime object for the closing time with the timezone info attached
        close_time = timezone_ET.localize(datetime(
            day.date.year,
            day.date.month,
            day.date.day,
            day.close.hour,
            day.close.minute
        ))

        # Convert the opening and closing times to ISO-8601
        # Literally dont even fucking ask me how long it took to get the data in the
        # right format for this to work.
        open_time = isoparse(open_time.isoformat())
        close_time = isoparse(close_time.isoformat())

        # Create a TradingDay object with the right open/close times and append it to
        # the list of all such TradingDay objects within the span between start_date and
        # end_date
        trading_day = TradingDay(trading_date, open_time, close_time)
        trading_days.append(trading_day)

    return trading_days
