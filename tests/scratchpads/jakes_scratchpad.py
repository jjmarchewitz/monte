from algo_pg.data_manager import DataManager
from algo_pg.machine import TradingMachine
from algo_pg.portfolio import Portfolio
from algo_pg.position import Position
from algo_pg.stat_calculators import dummy_420_69
from algo_pg.util import AlpacaAPIBundle
from alpaca_trade_api import TimeFrame, TimeFrameUnit


def main():
    alpaca_api = AlpacaAPIBundle()

    stat_dict = {
        "TEST": dummy_420_69,
        "TEST2": dummy_420_69,
        "TEST3": dummy_420_69
    }

    # Only Days, Hours, and Minutes are supported as time frames
    machine = TradingMachine(
        alpaca_api, "2022-03-08", "2022-03-20",
        time_frame=TimeFrame.Day,
        stat_dict=stat_dict)

    portfolio1 = Portfolio(alpaca_api, starting_cash=0, name="P1")

    portfolio1.create_new_position("AAPL", 5)

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
