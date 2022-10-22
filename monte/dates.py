##################
# DATE UTILITIES #
##################

from dataclasses import dataclass
from datetime import date, datetime
from typing import no_type_check

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
                                      start_date: date, end_date: date) -> list[TradingDay]:
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
                                    start_date: date, end_date: date) -> list[entity.Calendar]:
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
    return alpaca_api.trading.get_calendar(start_date.isoformat(), end_date.isoformat())


@no_type_check
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
            # Types are ignored because the Alpaca API is using a non-type-hinted __getattr__ function
            # so Pylance freaks out when it doesn't need to.
            day.date.year,  # type: ignore
            day.date.month,  # type: ignore
            day.date.day  # type: ignore
        )

        # Grab the DST-aware timezone object for eastern time
        timezone_ET = timezone("America/New_York")

        # Create a datetime object for the opening time with the timezone info attached
        open_time = timezone_ET.localize(datetime(
            # Types are ignored because the Alpaca API is using a non-type-hinted __getattr__ function
            # so Pylance freaks out when it doesn't need to.
            day.date.year,  # type: ignore
            day.date.month,  # type: ignore
            day.date.day,  # type: ignore
            day.open.hour,  # type: ignore
            day.open.minute  # type: ignore
        ))

        # Create a datetime object for the closing time with the timezone info attached
        close_time = timezone_ET.localize(datetime(
            # Types are ignored because the Alpaca API is using a non-type-hinted __getattr__ function
            # so Pylance freaks out when it doesn't need to.
            day.date.year,  # type: ignore
            day.date.month,  # type: ignore
            day.date.day,  # type: ignore
            day.close.hour,  # type: ignore
            day.close.minute  # type: ignore
        ))

        # Create a TradingDay object with the right open/close times and append it to
        # the list of all such TradingDay objects within the span between start_date and
        # end_date
        trading_day = TradingDay(trading_date, open_time, close_time)
        trading_days.append(trading_day)

    return trading_days


def get_list_of_buffer_ranges(alpaca_api: AlpacaAPIBundle, buffer_length: int, start_date: date,
                              end_date: date) -> list[tuple[date, date]]:
    """DOC:"""

    trading_days = get_list_of_trading_days_in_range(alpaca_api, start_date, end_date)

    start_index = 0
    end_index = min(buffer_length - 1, len(trading_days) - 1)
    list_of_pairs = []

    while True:
        # Get the start and end buffer dates from the list of TradingDays
        buffer_start_date = trading_days[start_index].date
        buffer_end_date = trading_days[end_index].date

        # Add the start and end buffer dates to the list
        list_of_pairs.append((buffer_start_date, buffer_end_date))

        # If the next start index would go past the end of trading_days, break out of the loop
        if start_index + buffer_length > len(trading_days):
            break

        # Update the indexes
        start_index = min(start_index + buffer_length, len(trading_days) - 1)
        end_index = min(end_index + buffer_length, len(trading_days) - 1)

    return list_of_pairs
