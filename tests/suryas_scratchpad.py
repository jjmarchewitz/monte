# from alpaca_trade_api import TimeFrame

# BARS_URL = 'https://data.alpaca.markets/v2/bars'
# API_KEY = 'PKQVIMNY5B00QRXZUYV8'
# SECRET_KEY = 'PmbQanQbkqh8YyltN1t63euWZTpPr6LyVZ4IfGwV'
# HEADERS = {
#     'APCA-API_KEY-ID': API_KEY,
#     'APCA-API-SECRET-KEY': SECRET_KEY
# }

# minute_bars_url = BARS_URL + '/5Min?symbols+MSFT'


# def main():
#     tradeapi = alpaca_setup()
#     account = tradeapi.get_account()

#     # Demo buy order
#     tradeapi.submit_order(
#         symbol="IVV",
#         qty="1",
#         side="buy",
#         type="market",
#     )

#     tradeapi.list_positions()
#     breakpoint()


# if __name__ == "__main__":
#     main()


# How do I incorporate my own keys with Jake's Architecture.
# I think I need to add it somehow to a configure file and then have the alpaca.py file in src choose between the keys on input arg
# Right now, testing collecting bar data with Jake's keys
from algo_pg_util.alpaca import alpaca_setup
from alpaca_trade_api import TimeFrame
from containers.portfolio import Portfolio
from containers.position import Position
from containers.trading_machine import TradingMachine


def main():
    trading_api, market_data_api = alpaca_setup()

    # Only Days, Hours, and Minutes are supported as time frames
    machine_day = TradingMachine(
        trading_api, market_data_api, "2021-03-08", "2021-03-20",
        time_frame=TimeFrame.Day)

    # machine_hours = TradingMachine(
    #      trading_api, market_data_api, "2022-03-08", "2022-03-20",
    #     time_frame=TimeFrame.Hours)
    # )
    machine_day._generate_market_day_list


if __name__ == "__main__":
    main()
    breakpoint()