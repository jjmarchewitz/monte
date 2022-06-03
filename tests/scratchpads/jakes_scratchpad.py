from algo_pg.data.manager import get_dataframe
from algo_pg.machine.portfolio import OrderType, Portfolio
from algo_pg.machine.position import Position
from algo_pg.machine.machine import TradingMachine
from algo_pg.util.alpaca import alpaca_setup
from alpaca_trade_api import TimeFrame
import algo_pg.util.dates as date_util


def main():
    alpaca_api = alpaca_setup()

    # print(
    #     get_dataframe(
    #         alpaca_api, "AAPL", "2021-05-30", "2021-06-20",
    #         time_frame=TimeFrame.Minute))

    breakpoint()


if __name__ == "__main__":
    main()
