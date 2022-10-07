"""DOC:"""

import gzip
import json
import os
import re
from typing import TypeVar

import asks
import pandas as pd
import trio
from alpaca_trade_api import REST, TimeFrame

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

    headers: dict[str, str]
    base_url: str

    def __init__(self, key_id: str, secret_id: str, base_url: str) -> None:
        """DOC:"""
        # HTTPS header, this contains the API key info to authenticate with Alpaca
        self.headers = {
            "APCA-API-KEY-ID": key_id,
            "APCA-API-SECRET-KEY": secret_id
        }

        # The base url is something like "https://data.alpaca.markets"
        self.base_url = base_url

    async def get_bars(self, symbol: str, time_frame: TimeFrame, start_date: str, end_date: str,
                       output_dict: dict[str, pd.DataFrame], adjustment: str = 'all', limit: int = 10000) -> None:
        """DOC:"""

        # Create an empty list to store all of the bars received from Alpaca
        list_of_bars = []

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
                try:
                    body_dict = json.loads(str(gzip.decompress(response.body), 'utf-8'))
                except gzip.BadGzipFile:
                    raise ValueError(
                        f"Alpaca does not have any data for {symbol} between {start_date} and {end_date}")

            # Response code 500 means "internal error", retry with the same parameters
            elif response.status_code == 500:
                continue

            elif response.status_code == 400 and len(list_of_bars) >= limit:
                raise OverflowError(
                    "Hit the limit of 10,000 rows in a single request from alpaca. To get around this, "
                    "consider making your data buffer size smaller. This will break up the request into "
                    "smaller requests.")

            # Something went wrong and we can't recover. Raise an error.
            else:
                raise ConnectionError(
                    f"Bad response from Alpaca with response code: {response.status_code}")

            # Add the bars from the latest Alpaca request to the list of all the bars
            list_of_bars.extend(body_dict['bars'])

            # Extract the token ID for the next data 'page' from the parsed body of the HTTPS response.
            next_page_token = body_dict['next_page_token']

            # If there is a next_page_token, add it as an HTTPS parameter for the next request.
            if next_page_token:
                params['next_page_token'] = next_page_token

            # Else, there is no more data to request.
            else:
                break

        # Put the data into a dataframe
        df = pd.DataFrame(list_of_bars)

        output_dict[symbol] = df

    def get_bulk_bars(self, symbols: str, time_frame: TimeFrame, start_date: str, end_date: str,
                      adjustment: str = 'all', limit: int = 10000) -> dict[str, pd.DataFrame]:

        output_dict = {}

        trio.run(
            self._async_get_bulk_bars,
            symbols,
            time_frame,
            start_date,
            end_date,
            output_dict,
            adjustment,
            limit)

        return output_dict

    async def _async_get_bulk_bars(self, symbols: str, time_frame: TimeFrame, start_date: str, end_date: str, output_dict: dict[str, pd.DataFrame], adjustment: str = 'all', limit: int = 10000) -> None:
        async with trio.open_nursery() as n:
            for symbol in symbols:
                n.start_soon(
                    self.get_bars,
                    symbol,
                    time_frame,
                    start_date,
                    end_date,
                    output_dict,
                    adjustment,
                    limit)


class AlpacaAPIBundle():
    """DOC:"""

    _trading_instances: list[REST]
    _market_data_instances: list[REST]
    _crypto_instances: list[REST]
    _async_market_data_instances: list[AsyncAlpacaBars]
    T = TypeVar('T')

    def __init__(self) -> None:
        # Get the repo dir as a string
        repo_dir = self._get_repo_dir()

        with open(f"{repo_dir}{os.sep}alpaca_config.json", "r") as alpaca_config_file:
            try:
                self.alpaca_config = json.load(alpaca_config_file)
            except BaseException:
                raise RuntimeError("Failed to load alpaca_config.json")

        # Create an instance of each of alpaca API for each API key-pair
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
    def trading(self) -> REST:
        """DOC:"""
        # The least recently-used instance should be located at self._api_instance_index, since the instances
        # are stored in a circular queue. The next instance is always the least-recently used one.
        lru_instance = self._trading_instances[self._api_instance_index]
        self._api_instance_index += 1

        # Reset the api instance index if it's past the end of the list
        if self._api_instance_index >= self._num_api_instances:
            self._api_instance_index = 0

        return lru_instance

    @property
    def market_data(self) -> REST:
        """DOC:"""
        # The least recently-used instance should be located at self._api_instance_index, since the instances
        # are stored in a circular queue. The next instance is always the least-recently used one.
        lru_instance = self._market_data_instances[self._api_instance_index]
        self._api_instance_index += 1

        # Reset the api instance index if it's past the end of the list
        if self._api_instance_index >= self._num_api_instances:
            self._api_instance_index = 0

        return lru_instance

    @property
    def crypto(self) -> REST:
        """DOC:"""
        # The least recently-used instance should be located at self._api_instance_index, since the instances
        # are stored in a circular queue. The next instance is always the least-recently used one.
        lru_instance = self._crypto_instances[self._api_instance_index]
        self._api_instance_index += 1

        # Reset the api instance index if it's past the end of the lsit
        if self._api_instance_index >= self._num_api_instances:
            self._api_instance_index = 0

        return lru_instance

    @property
    def async_market_data_bars(self) -> AsyncAlpacaBars:
        # The least recently-used instance should be located at self._api_instance_index, since the instances
        # are stored in a circular queue. The next instance is always the least-recently used one.
        lru_instance = self._async_market_data_instances[self._api_instance_index]
        self._api_instance_index += 1

        # Reset the api instance index if it's past the end of the lsit
        if self._api_instance_index >= self._num_api_instances:
            self._api_instance_index = 0

        return lru_instance

    def _create_api_instances(self, api_class: T, endpoint: str) -> list[T]:
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

    def _get_repo_dir(self) -> str:
        """DOC:"""
        repo_name_matches = re.findall(f"^.*monte{os.sep}monte", __file__)

        # If the repo name can't be found inside of the full file path
        if not repo_name_matches:
            raise FileNotFoundError("Could not find the parent repo directory.")

        # Trims the end of the path so that it says "/monte" instead of "/monte/monte"
        repo_dir = re.sub(f"{os.sep}monte{os.sep}monte",
                          f"{os.sep}monte", repo_name_matches[0])

        return repo_dir
