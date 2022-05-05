import alpaca_trade_api as tradeapi
import os
import re
from dataclasses import dataclass


@dataclass
class APISettings():
    api_key_ID: str = ""
    secret_key: str = ""
    trading_context: str = ""
    trading_website: str = ""


def alpaca_setup():

    api_settings = APISettings()
    repo_dir = re.findall("^.*algo-playground", os.getcwd())[0]

    # Grab all of the info contained in ALPACA_CONFIG.txt
    with open(f"{repo_dir}/ALPACA_CONFIG.txt", "r") as api_config_file:
        api_config_file_str = api_config_file.read()

        # Load the trading context
        api_settings.trading_context = (
            re.findall('TRADING_CONTEXT=".*"', api_config_file_str)[0]
            .lstrip("TRADING_CONTEXT=")
            .strip('"'))

        # Load the API key ID
        api_settings.api_key_ID = (
            re.findall('APCA-API-KEY-ID=".*"', api_config_file_str)[0]
            .lstrip("APCA-API-KEY-ID=")
            .strip('"'))

        # Load the secret key
        api_settings.secret_key = (
            re.findall('APCA-API-SECRET-KEY=".*"', api_config_file_str)[0]
            .lstrip("APCA-API-SECRET-KEY=")
            .strip('"'))

    # Set the trading website based on trading context (paper or live trading)
    if api_settings.trading_context.lower() == "paper":
        api_settings.trading_website = "https://paper-api.alpaca.markets"
    elif api_settings.trading_context.lower() == "live":
        api_settings.trading_website = "https://api.alpaca.markets"
    else:
        raise ValueError(
            "The trading context in ALPACA_CONFIG.txt can only be either "
            + "\"paper\" or \"live\".")

    # Set the API key ID and secret key as an environment variables
    os.environ["APCA-API-KEY-ID"] = api_settings.api_key_ID
    os.environ["APCA-API-SECRET-KEY"] = api_settings.secret_key

    # Create the instance of the alpaca API with the given keys and website
    api = tradeapi.REST(
        api_settings.api_key_ID,
        api_settings.secret_key,
        api_settings.trading_website
    )

    return api
