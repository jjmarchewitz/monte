from algo_pg.algorithms.monthly_s_p.alg import MonthlySP
from algo_pg.machine import TradingMachine, DataSettings
from algo_pg.portfolio import Portfolio
from algo_pg.stat_calculators import dummy_420_69, avg_last_5, net_last_5
from algo_pg.util import AlpacaAPIBundle
from alpaca_trade_api import TimeFrame
from datetime import timedelta


def main():
    alpaca_api = AlpacaAPIBundle()

    # Keys will become column names and the function object that is the value will be
    # called on every row of every Position's DataManager
    stat_dict = {
    }

    # A dataclass that stores general information about data settings and how the data
    # should be collected
    data_settings = DataSettings(
        start_date="2018-01-01",
        end_date="2019-01-01",
        time_frame=TimeFrame.Day,
        stat_dict=stat_dict,
        max_rows_in_df=5_000,
        start_buffer_time_delta=timedelta(days=5),
        time_frames_between_algo_runs=1
    )

    # Create the trading machine with the appropriate data settings
    machine = TradingMachine(alpaca_api, data_settings)

    # Define an instance of an algorithm with a portfolio
    portfolio1 = Portfolio(alpaca_api, data_settings, starting_cash=5_000, name="P1")
    algo1 = MonthlySP(alpaca_api, data_settings, portfolio1)

    machine.add_algo_instance(algo1)

    machine.run()

    ############

    # dm = DataManager(alpaca_api, data_settings, "GOOG")

    # dm.set_df_with_dates("2022-03-08", "2022-03-20")

    ############

    breakpoint()


if __name__ == "__main__":
    main()
