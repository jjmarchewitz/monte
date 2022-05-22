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
    trading_api, market_data_api = alpaca_setup()

    portfolio1 = Portfolio(market_data_api, starting_cash=10000, name="P1")

    breakpoint()

    order_num = portfolio1.place_order("AAPL", 5.0, OrderType.BUY)

    portfolio1.cancel_order(order_num)


if __name__ == "__main__":
    main()
