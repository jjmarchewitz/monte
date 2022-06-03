"""
TODO:
"""

from dataclasses import dataclass
from datetime import date, datetime
from pytz import timezone


@dataclass
class MarketDay():
    """
    A dataclass holding information for a single day the market is open, like the date. \
    This dataclass also stores the market open time and close time in the ISO-8601 format.
    """
    date: str
    open_time_iso: str
    close_time_iso: str


def get_list_of_market_days_in_range(alpaca_api, start_date, end_date):
    """
    TODO:

    Args:
        alpaca_api: _description_
        start_date: _description_
        end_date: _description_

    Returns:
        _description_
    """
    raw_market_days = get_raw_market_dates_in_range(alpaca_api, start_date, end_date)
    return get_market_day_obj_list_from_date_list(raw_market_days)


def get_raw_market_dates_in_range(alpaca_api, start_date, end_date):
    """
    TODO:

    Args:
        alpaca_api: _description_
        start_date: _description_
        end_date: _description_

    Returns:
        _description_
    """
    return alpaca_api.trading.get_calendar(start_date, end_date)


def get_market_day_obj_list_from_date_list(market_date_list):
    """
    TODO:

    Args:
        market_date_list: _description_

    Returns:
        _description_
    """
    market_days = []

    for day in market_date_list:

        # Create a date object (from the datetime library) for the calendar date of the
        # market day
        market_date = date(
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
        open_time = open_time.isoformat()
        close_time = close_time.isoformat()

        # Create a MarketDay object with the right open/close times and append it to
        # the list of all such MarketDay objects within the span between start_date and
        # end_date
        market_day = MarketDay(market_date, open_time, close_time)
        market_days.append(market_day)

    return market_days


def get_datetime_obj_from_date(date):
    format_str = '%Y-%m-%d'

    dt_obj = datetime.strptime(date, format_str)

    return dt_obj
