from alpaca_trade_api import REST, TimeFrameUnit
import json
import os
import re

REPO_NAME = "monte"

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

        # Create an instance of each API for each API key
        self._trading_instances = self._create_api_instances(
            self.alpaca_config["ENDPOINT"])
        self._market_data_instances = self._create_api_instances(
            "https://data.alpaca.markets")
        self._crypto_instances = self._create_api_instances(
            "https://data.alpaca.markets/v1beta1/crypto")

        # Create an index variable to track which instance within the API instance lists
        # should be used
        self._trading_instance_index = 0
        self._market_data_instance_index = 0
        self._crypto_instance_index = 0

    @property
    def trading(self):
        """DOC:"""
        lru_trading_instance = self._trading_instances[self._trading_instance_index]
        self._trading_instance_index += 1

        # Reset the trading instance index if it's past the end of the list
        if self._trading_instance_index >= len(self._trading_instances):
            self._trading_instance_index = 0

        return lru_trading_instance

    @property
    def market_data(self):
        """DOC:"""
        lru_market_data_instance = self._market_data_instances[self._market_data_instance_index]
        self._market_data_instance_index += 1

        # Reset the market data instance index if it's past the end of the list
        if self._market_data_instance_index >= len(self._market_data_instances):
            self._market_data_instance_index = 0

        return lru_market_data_instance

    @property
    def crypto(self):
        """DOC:"""
        lru_crypto_instance = self._crypto_instances[self._crypto_instance_index]
        self._crypto_instance_index += 1

        # Reset the crypto instance index if it's past the end of the lsit
        if self._crypto_instance_index >= len(self._crypto_instances):
            self._crypto_instance_index = 0

        return lru_crypto_instance

    def _create_api_instances(self, endpoint):
        """DOC:"""
        api_instance_list = []

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

        # sTrims the end of the path so that it says "/monte" instead of "/monte/monte"
        repo_dir = re.sub(f"{os.sep}monte{os.sep}monte",
                          f"{os.sep}monte", repo_name_matches[0])

        return repo_dir
