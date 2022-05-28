"""
A utility class to handle the setup and configuration of alpaca's APIs.
"""

from alpaca_trade_api import REST
from dataclasses import dataclass
from os import environ, getcwd, sep
from re import findall


@dataclass
class AlpacaAPIBundle():
    crypto: REST
    market_data: REST
    trading: REST


def alpaca_setup():
    """
    Grab the Alpaca API keys from alpaca.config and create an Alpaca trading REST API instance
    and an Alpaca market history REST API instance.
    # TODO: Update this documentation to be about the API bundle

    Raises:
        ValueError: When the trading context in alpaca.config is invalid.

    Returns:
        An Alpaca trading REST API instance and an Alpaca market history REST API instance.
    """
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
    trading_api = REST(
        api_key_ID,
        secret_key,
        trading_website
    )

    # Create the instance of the alpaca market data API
    market_data_api = REST(
        api_key_ID,
        secret_key,
        market_data_website
    )

    # Create the instance of the alpaca crypto API
    crypto_api = REST(
        api_key_ID,
        secret_key,
        crypto_website
    )

    # Create the API bundle object with all 3 alpaca APIs
    api_bundle = AlpacaAPIBundle(
        crypto=crypto_api,
        market_data=market_data_api,
        trading=trading_api
    )

    return api_bundle
