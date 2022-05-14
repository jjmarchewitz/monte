from alpaca_trade_api import REST
from dataclasses import dataclass
from os import environ, getcwd, sep
from re import findall


# TODO: Rewrite docstrings in google-no-type style

@dataclass
class APISettings():
    api_key_ID: str = ""
    secret_key: str = ""
    trading_context: str = ""
    trading_website: str = ""


def alpaca_setup():
    """
    Grab the Alpaca API keys from alpaca.config and create an Alpaca trading REST API instance
    and an Alpaca market history REST API instance.

    Raises:
        ValueError: When the trading context in alpaca.config is invalid.

    Returns:
        An Alpaca trading REST API instance and an Alpaca market history REST API instance.
    """

    api_settings = APISettings()
    repo_dir = findall("^.*algo-playground", getcwd())[0]

    # Grab all of the info contained in alpaca.config
    with open(f"{repo_dir}{sep}alpaca.config", "r") as api_config_file:
        api_config_file_str = api_config_file.read()

        # Load the trading context
        api_settings.trading_context = (
            findall('TRADING_CONTEXT=".*"', api_config_file_str)[0]
            .lstrip("TRADING_CONTEXT=")
            .strip('"'))

        # Load the API key ID
        api_settings.api_key_ID = (
            findall('APCA-API-KEY-ID=".*"', api_config_file_str)[0]
            .lstrip("APCA-API-KEY-ID=")
            .strip('"'))

        # Load the secret key
        api_settings.secret_key = (
            findall('APCA-API-SECRET-KEY=".*"', api_config_file_str)[0]
            .lstrip("APCA-API-SECRET-KEY=")
            .strip('"'))

    # Set the trading website based on trading context (paper or live trading)
    if api_settings.trading_context.lower() == "paper":
        api_settings.trading_website = "https://paper-api.alpaca.markets"
    elif api_settings.trading_context.lower() == "live":
        api_settings.trading_website = "https://api.alpaca.markets"
    else:
        raise ValueError(
            "The trading context in alpaca.config can only be either "
            + "\"paper\" or \"live\".")

    # A variable for the historical market data website
    market_data_website = "https://data.alpaca.markets"

    # Set the API key ID and secret key as an environment variables
    environ["APCA-API-KEY-ID"] = api_settings.api_key_ID
    environ["APCA-API-SECRET-KEY"] = api_settings.secret_key

    # Create the instance of the alpaca trading API with the given keys and website
    trading_api = REST(
        api_settings.api_key_ID,
        api_settings.secret_key,
        api_settings.trading_website
    )

    # Create the instance of the alpaca market data API
    market_data_api = REST(
        api_settings.api_key_ID,
        api_settings.secret_key,
        market_data_website
    )

    return trading_api, market_data_api
