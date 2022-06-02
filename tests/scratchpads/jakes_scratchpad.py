from algo_pg.data.manager import get_dataframe
from algo_pg.machine.portfolio import OrderType, Portfolio
from algo_pg.machine.position import Position
from algo_pg.machine.machine import TradingMachine
from algo_pg.util.alpaca import alpaca_setup
from alpaca_trade_api import TimeFrame


def main():
    alpaca_api = alpaca_setup()

    print(get_dataframe(alpaca_api, "AAPL", "05-21-2020", "06-22-2020"))


if __name__ == "__main__":
    main()
