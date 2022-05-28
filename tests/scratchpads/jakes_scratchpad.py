# -*- coding: UTF-8 -*-

from algo_pg.machine.portfolio import OrderType, Portfolio
from algo_pg.machine.position import Position
from algo_pg.machine.trading_machine import TradingMachine
from algo_pg.util.alpaca import alpaca_setup
from alpaca_trade_api import TimeFrame

######################################################
# 🥹🙃🥰😙🤪🤓🤩🫥🫥🫥😑😵‍💫🤤🥱😷🤮🤢🤮😈😈🎱🎱🏐🏀⚽️⚾️🥍😈👿👺 #
# I put these here to get your attention! I moved    #
# the example to usage_examples.py so I could have   #
# my scratchpad back!                                #
# 🥹🙃🥰😙🤪🤓🤩🫥🫥🫥😑😵‍💫🤤🥱😷🤮🤢🤮😈😈🎱🎱🏐🏀⚽️⚾️🥍😈👿👺 #
######################################################


def main():
    alpaca_api = alpaca_setup()

    machine = TradingMachine(
        alpaca_api, "2022-03-08", "2022-03-20",
        time_frame=TimeFrame.Day)

    portfolio1 = Portfolio(alpaca_api, starting_cash=10000, name="P1")

    # Old call // New call
    crypto_api = alpaca_api.crypto
    market_data_api = alpaca_api.market_data
    trading_api = alpaca_api.trading

    breakpoint()

    order_num = portfolio1.place_order("AAPL", 5.0, OrderType.BUY)

    portfolio1.cancel_order(order_num)


if __name__ == "__main__":
    main()
