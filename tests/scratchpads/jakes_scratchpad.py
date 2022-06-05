from algo_pg.data_manager import DataManager
from algo_pg.machine import TradingMachine, DataSettings
from algo_pg.portfolio import Portfolio, OrderType
from algo_pg.position import Position
from algo_pg.stat_calculators import dummy_420_69
from algo_pg.util import AlpacaAPIBundle
from alpaca_trade_api import TimeFrame, TimeFrameUnit
from datetime import timedelta


def main():
    alpaca_api = AlpacaAPIBundle()

    # Keys will become column names and the function object that is the value will be
    # called on every row of every Position's DataManager
    stat_dict = {
        "TEST": dummy_420_69,
        "TEST2": dummy_420_69,
        "TEST3": dummy_420_69
    }

    # A dataclass that stores general information about data settings and how the data
    # should be collected
    data_settings = DataSettings(
        start_date="2021-09-09",
        end_date="2021-11-09",
        time_frame=TimeFrame.Minute,
        stat_dict=stat_dict,
        max_rows_in_history_df=10_000,
        buffer_data_length=timedelta(days=0),
        time_frames_between_algo_runs=1
    )

    # Only Days, Hours, and Minutes are supported as time frames
    machine = TradingMachine(alpaca_api, data_settings)

    portfolio1 = Portfolio(alpaca_api, data_settings, starting_cash=5_000, name="P1")

    portfolio1.create_new_position("AAPL", 5)

    portfolio1.place_order("AAPL", 2, OrderType.BUY)

    machine.add_algo_portfolio_pair("DummyAlgo1", portfolio1)

    machine.run()

    #########

    # bar_iter = alpaca_api.market_data.get_bars_iter(
    #     "AAPL", timeframe=TimeFrame.Day, start="2020-06-28", end="2020-08-08")

    # bar_df = alpaca_api.market_data.get_bars(
    #     "AAPL", timeframe=TimeFrame(45, TimeFrameUnit.Minute),
    #     start="2020-06-29", end="2020-06-29").df

    #########

    # dm = DataManager(alpaca_api, "GOOG", "2022-03-08", "2022-03-20")

    # dm.get_df_between_dates("2022-03-08", "2022-03-20")

    #########

    # pos = Position(alpaca_api, "GOOG", 5.0)
    # pos.data_manager.set_start_and_end_dates("2022-03-08", "2022-03-20")
    # pos.data_manager.set_time_frame(TimeFrame.Day)

    # rg = pos.data_manager._row_generator()

    # next(rg)

    # pos.update_price()

    breakpoint()


if __name__ == "__main__":
    main()
