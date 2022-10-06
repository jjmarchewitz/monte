"""DOC:"""

from alpaca_trade_api import REST
from dataclasses import dataclass
from datetime import date, datetime
from pytz import timezone
import asks
import gzip
import json
import os
import re


#############
# CONSTANTS #
#############

REPO_NAME = "monte"
MARKET_DATA_BASE_URL = "https://data.alpaca.markets"
CRYPTO_BASE_URL = "https://data.alpaca.markets/v1beta1/crypto"


##############
# ALPACA API #
##############

class AsyncAlpacaBars():
    """DOC:"""

    def __init__(self, key_id, secret_id, base_url) -> None:
        """DOC:"""
        # HTTPS header, this contains the API key info to authenticate with Alpaca
        self.headers = {
            "APCA-API-KEY-ID": key_id,
            "APCA-API-SECRET-KEY": secret_id
        }

        # The base url is something like "https://data.alpaca.markets"
        self.base_url = base_url

    async def get_bars(self, symbol, time_frame, start_date, end_date, adjustment='raw', limit=1000):
        """DOC:"""

        # TODO: Format output as a dataframe, and sort by timestamp

        # Create an empty list to store all of the bars received from Alpaca
        output_list = []

        # HTTPS GET request parameters
        params = {
            "adjustment": adjustment,
            "start": start_date,
            "end": end_date,
            "timeframe": str(time_frame),
            "limit": limit
        }

        # Alpaca does not let us request all the data at once, and instead forces us to request it in
        # "pages". This loop goes through all the pages until there is no more data to get and returns.
        while True:

            # Get the data from Alpaca asynchronously
            response = await asks.get(
                f"https://data.alpaca.markets/v2/stocks/{symbol}/bars",
                headers=self.headers,
                params=params,
                follow_redirects=False
            )

            # Response code 200 means success. If the data was received successfully, load it as a dictionary
            if response.status_code == 200:
                body_dict = json.loads(str(gzip.decompress(response.body), 'utf-8'))

            # If the response code was not 200, something went wrong. Raise an error.
            else:
                raise ConnectionError(
                    f"Bad response from Alpaca with response code: {response.status_code}")

            # Add the bars from the latest Alpaca request to the list of all the bars
            output_list.extend(body_dict['bars'])

            # Extract the token ID for the next data 'page' from the parsed body of the HTTPS response.
            next_page_token = body_dict['next_page_token']

            # If there is a next_page_token, add it as an HTTPS parameter for the next request.
            if next_page_token:
                params['next_page_token'] = next_page_token

            # Else, there is no more data to request.
            else:
                break

        return output_list


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
            REST, self.alpaca_config["ENDPOINT"])
        self._market_data_instances = self._create_api_instances(
            REST, MARKET_DATA_BASE_URL)
        self._crypto_instances = self._create_api_instances(
            REST, CRYPTO_BASE_URL)
        self._async_market_data_instances = self._create_api_instances(
            AsyncAlpacaBars, MARKET_DATA_BASE_URL)

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

    def _create_api_instances(self, api_class, endpoint):
        """DOC:"""
        api_instance_list = []

        # For every loaded API key-secret key pair, create an instance of the REST API using the "endpoint"
        # argument.
        for api_key in self.alpaca_config["API_KEYS"]:
            api_instance = api_class(
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
