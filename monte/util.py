"""DOC:"""

from alpaca_trade_api import REST
from dataclasses import dataclass
from datetime import date, datetime
from pytz import timezone
import json
import os
import re


#############
# CONSTANTS #
#############

REPO_NAME = "monte"
MARKET_DATA_ENDPOINT = "https://data.alpaca.markets"
CRYPTO_ENDPOINT = "https://data.alpaca.markets/v1beta1/crypto"


##############
# ALPACA API #
##############

class AlpacaAPIBundle():
    """DOC:"""

    def __init__(self) -> None:
        # Get the repo dir as a string
        repo_dir = self._get_repo_dir()

        with open(f"{repo_dir}{os.sep}alpaca_config.json", "r") as alpaca_config_file:
            try:
                self.alpaca_config = json.load(alpaca_config_file)
            except:
                raise RuntimeError("Failed to load alpaca_config.json")

        # Create an instance of each of alpaca's APIs for each API key-pair
        self._trading_instances = self._create_api_instances(
            self.alpaca_config["ENDPOINT"])
        self._market_data_instances = self._create_api_instances(
            MARKET_DATA_ENDPOINT)
        self._crypto_instances = self._create_api_instances(
            CRYPTO_ENDPOINT)

        # Store the number of API instances there are in every instance list. The number of API instances
        # is equivalent to the number of API key pairs
        self._num_api_instances = len(self.alpaca_config["API_KEYS"])

        # Create an index variable to track which instance within the API instance lists
        # should be used
        self._api_instance_index = 0

    @property
    def trading(self):
        """DOC:"""
        # The least recently-used instance should be located at self._api_instance_index, since the instances
        # are stored in a circular queue. The next instance is always the least-recently used one.
        lru_instance = self._trading_instances[self._api_instance_index]
        self._api_instance_index += 1

        # Reset the trading instance index if it's past the end of the list
        if self._api_instance_index >= self._num_api_instances:
            self._api_instance_index = 0

        return lru_instance

    @property
    def market_data(self):
        """DOC:"""
        # The least recently-used instance should be located at self._api_instance_index, since the instances
        # are stored in a circular queue. The next instance is always the least-recently used one.
        lru_instance = self._market_data_instances[self._api_instance_index]
        self._api_instance_index += 1

        # Reset the market data instance index if it's past the end of the list
        if self._api_instance_index >= self._num_api_instances:
            self._api_instance_index = 0

        return lru_instance

    @property
    def crypto(self):
        """DOC:"""
        # The least recently-used instance should be located at self._api_instance_index, since the instances
        # are stored in a circular queue. The next instance is always the least-recently used one.
        lru_instance = self._crypto_instances[self._api_instance_index]
        self._api_instance_index += 1

        # Reset the crypto instance index if it's past the end of the lsit
        if self._api_instance_index >= self._num_api_instances:
            self._api_instance_index = 0

        return lru_instance

    def _create_api_instances(self, endpoint):
        """DOC:"""
        api_instance_list = []

        # For every loaded API key-secret key pair, create an instance of the REST API using the "endpoint"
        # argument.
        for api_key in self.alpaca_config["API_KEYS"]:
            api_instance = REST(
                api_key["API_KEY_ID"],
                api_key["SECRET_KEY"],
                endpoint
            )

            api_instance_list.append(api_instance)

        return api_instance_list

    def _get_repo_dir(self):
        """DOC:"""
        repo_name_matches = re.findall(f"^.*monte{os.sep}monte", __file__)

        # If the repo name can't be found inside of the full file path
        if not repo_name_matches:
            raise FileNotFoundError("Could not find the parent repo directory.")

        # Trims the end of the path so that it says "/monte" instead of "/monte/monte"
        repo_dir = re.sub(f"{os.sep}monte{os.sep}monte",
                          f"{os.sep}monte", repo_name_matches[0])

        return repo_dir


##################
# DATE UTILITIES #
##################

@dataclass
class TradingDay():
    """
    A dataclass holding information for a single day the market is open, like the date.
    This dataclass also stores the market open time and close time in the ISO-8601
    format.
    """
    date: str
    open_time_iso: str
    close_time_iso: str


def get_list_of_trading_days_in_range(alpaca_api, start_date, end_date):
    """
    DOC:
    """
    raw_market_days = get_raw_trading_dates_in_range(alpaca_api, start_date, end_date)
    return get_trading_day_obj_list_from_date_list(raw_market_days)


def get_raw_trading_dates_in_range(alpaca_api, start_date, end_date):
    """
    DOC:
    """
    return alpaca_api.trading.get_calendar(start_date, end_date)


def get_trading_day_obj_list_from_date_list(trading_date_list):
    """
    DOC:
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
