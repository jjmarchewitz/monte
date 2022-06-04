from algo_pg.data_manager import DataManager
from algo_pg.machine import TradingMachine
from algo_pg.util import AlpacaAPIBundle
from alpaca_trade_api import TimeFrame, TimeFrameUnit


def main():
    alpaca_api = AlpacaAPIBundle()

    # Only Days, Hours, and Minutes are supported as time frames
    machine = TradingMachine(
        alpaca_api, "2022-03-08", "2022-03-20",
        time_frame=TimeFrame.Day)

    # bar_iter = alpaca_api.market_data.get_bars_iter(
    #     "AAPL", timeframe=TimeFrame.Day, start="2020-06-28", end="2020-08-08")

    # bar_df = alpaca_api.market_data.get_bars(
    #     "AAPL", timeframe=TimeFrame(45, TimeFrameUnit.Minute),
    #     start="2020-06-29", end="2020-06-29").df

    dm = DataManager(alpaca_api, "GOOG", "2022-03-08", "2022-03-20")

    dm.get_df_between_dates("2022-03-08", "2022-03-20")

    breakpoint()


if __name__ == "__main__":
    main()
