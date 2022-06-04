"""
A general utility module to containing useful automation functions available globally to
the project.

"""

from alpaca_trade_api import REST, TimeFrameUnit
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from os import environ, getcwd, sep
from pytz import timezone
from re import findall


##############
# ALPACA API #
##############


class AlpacaAPIBundle():
    """
    Grabs the Alpaca API keys from alpaca.config and uses them to instantiate each 
    Alpaca REST API.
    """

    def __init__(self):
        repo_dir = findall("^.*algo-playground", getcwd())[0]

        # Grab all of the info contained in alpaca.config
        with open(f"{repo_dir}{sep}alpaca.config", "r") as api_config_file:
            api_config_file_str = api_config_file.read()

            # Load the trading context
            trading_context = (
                findall('TRADING_CONTEXT=".*"', api_config_file_str)[0]
                .lstrip("TRADING_CONTEXT=")
                .strip('"'))

            # Load the API key ID
            api_key_ID = (
                findall('APCA-API-KEY-ID=".*"', api_config_file_str)[0]
                .lstrip("APCA-API-KEY-ID=")
                .strip('"'))

            # Load the secret key
            secret_key = (
                findall('APCA-API-SECRET-KEY=".*"', api_config_file_str)[0]
                .lstrip("APCA-API-SECRET-KEY=")
                .strip('"'))

        # Set the trading website based on trading context (paper or live trading)
        if trading_context.lower() == "paper":
            trading_website = "https://paper-api.alpaca.markets"
        elif trading_context.lower() == "live":
            trading_website = "https://api.alpaca.markets"
        else:
            raise ValueError(
                "The trading context in alpaca.config can only be either "
                + "\"paper\" or \"live\".")

        # Variables for the market data and crypto websites
        market_data_website = "https://data.alpaca.markets"
        crypto_website = "https://data.alpaca.markets/v1beta1/crypto"

        # Set the API key ID and secret key as an environment variables
        environ["APCA-API-KEY-ID"] = api_key_ID
        environ["APCA-API-SECRET-KEY"] = secret_key

        # Create the instance of the alpaca trading API with the given keys and website
        self.trading = REST(
            api_key_ID,
            secret_key,
            trading_website
        )

        # Create the instance of the alpaca market data API
        self.market_data = REST(
            api_key_ID,
            secret_key,
            market_data_website
        )

        # Create the instance of the alpaca crypto API
        self.crypto = REST(
            api_key_ID,
            secret_key,
            crypto_website
        )


##################
# DATE UTILITIES #
##################


@dataclass
class TradingDay():
    """
    A dataclass holding information for a single day the market is open, like the date. \
    This dataclass also stores the market open time and close time in the ISO-8601 format.
    """
    date: str
    open_time_iso: str
    close_time_iso: str


def get_list_of_trading_days_in_range(alpaca_api, start_date, end_date):
    """
    TODO:

    Args:
        alpaca_api: _description_
        start_date: _description_
        end_date: _description_

    Returns:
        _description_
    """
    raw_market_days = get_raw_trading_dates_in_range(alpaca_api, start_date, end_date)
    return get_trading_day_obj_list_from_date_list(raw_market_days)


def get_raw_trading_dates_in_range(alpaca_api, start_date, end_date):
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


def get_trading_day_obj_list_from_date_list(trading_date_list):
    """
    TODO:

    Args:
        market_date_list: _description_

    Returns:
        _description_
    """
    trading_days = []

    for day in trading_date_list:

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
        open_time = open_time.isoformat()
        close_time = close_time.isoformat()

        # Create a TradingDay object with the right open/close times and append it to
        # the list of all such TradingDay objects within the span between start_date and
        # end_date
        trading_day = TradingDay(trading_date, open_time, close_time)
        trading_days.append(trading_day)

    return trading_days


def get_datetime_obj_from_date(date):
    """
    TODO:

    Args:
        date: _description_

    Returns:
        _description_
    """
    format_str = '%Y-%m-%d'

    dt_obj = datetime.strptime(date, format_str)

    return dt_obj


def get_time_delta_from_time_frame(time_frame):
    """
    TODO:

    Args:
        time_frame: _description_

    Raises:
        ValueError: _description_

    Returns:
        _description_
    """
    delta = None

    if time_frame.unit is TimeFrameUnit.Minute:
        delta = timedelta(minutes=time_frame.amount)
    elif time_frame.unit is TimeFrameUnit.Hour:
        delta = timedelta(hours=time_frame.amount)
    elif time_frame.unit is TimeFrameUnit.Day:
        delta = timedelta(days=time_frame.amount)
    else:
        raise ValueError(
            "Invalid time frame passed in. TimeFrameUnit must be Minutes, Hours, or Days.")

    return delta


###################
# MONEY UTILITIES #
###################


def get_price_from_bar(bar):
    """
    Determines an equivalent price for an asset during a bar from info about the
    bar itself.

    Args:
        bar: One bar of stock information that takes up one TimeFrame's worth of time.

    Returns:
        An average price to represent the bar, determined from information about the
        bar.
    """
    # TODO: Find a better way to approximate the average price during a bar
    price = (bar.h + bar.l) / 2
    # price = (bar.o + bar.c) / 2

    return price
