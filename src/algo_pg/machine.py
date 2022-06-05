"""
A trading machine is an object that encompasses the running of algorithms with portfolios
attached. These algorithm-portfolio pairs can be either run on historical data or on live data.
"""

from algo_pg.algorithms.base_algorithm import Algorithm
from algo_pg.portfolio import Portfolio
from algo_pg.util import get_list_of_trading_days_in_range
from alpaca_trade_api import TimeFrame
from dataclasses import dataclass
from datetime import timedelta


@dataclass
class DataSettings():
    """
    Used to store all of the trading machine/data manager settings so this object can be
    passed around and settings can be synchronized.
    """
    start_date: str
    end_date: str
    time_frame: TimeFrame
    stat_dict: dict
    max_rows_in_history_df: int
    buffer_data_length: timedelta
    time_frames_between_algo_runs: int = 1


@dataclass
class AlgoPortfolioPair():
    """
    A trading algorithm-portfolio pair is run together across a trading machine's timeline
    as one unit.
    """
    algo: Algorithm
    portfolio: Portfolio


class TradingMachine():
    """
    The "trading machine" is meant to represent a machine running an algorithm with data 
    across the timeline that are provided as constructor arguments. This encompasses
    backtesting (testing on historical data) as well as running an algorithm live.
    """

    def __init__(self, alpaca_api, data_settings):
        """
        Constructor for the TradingMachine class.

        Args:
            alpaca_api: A bundle of Alpaca APIs all created and authenticated with the keys
                in the repo's alpaca.config.
            data_settings: An instance of the DataSettings dataclass.
        """

        # Bundled alpaca API dataclass
        self.alpaca_api = alpaca_api

        # Attributes to keep track of the time span of the trading_machine
        self.start_date = data_settings.start_date
        self.end_date = data_settings.end_date
        # TODO: self.current_datetime = None
        self.stat_dict = data_settings.stat_dict

        # The only supported time frames for this class are minutes, hours, and days.
        self.time_frame = data_settings.time_frame

        # Generates a list of MarketDay instances in order from self.start_date to
        # self.end_date to represent all of the days the market is open, and *only*
        # the days the market is open.
        self.trading_days = get_list_of_trading_days_in_range(
            self.alpaca_api, self.start_date, self.end_date)

        # Pairs of algorithms and portfolios
        self.algo_portfolio_pairs = []

    def add_algo_portfolio_pair(self, algorithm, portfolio):
        """
        Adds an algorithm-portfolio pair to the list of all such pairs for the trading
        machine. This is useful because the run() function can iterate over these pairs and
        all of the provided algorithms against their corresponding portfolios.

        Args:
            algorithm: A TradingAlgorithm instance or instance of a sub-class.
            portfolio: A Portfolio instance.
        """
        # TODO: Add a check to make sure the algorithm and portfolio are set up correctly
        # before adding (type check)
        algo_portfolio_pair = AlgoPortfolioPair(algorithm, portfolio)
        self.algo_portfolio_pairs.append(algo_portfolio_pair)

    def run(self):
        """
        Run the trading machine and run all of the algorithm portfolio pairs from the start
        date to the end date.
        """

        # For every day that the market will be open
        for trading_day in self.trading_days:

            # Update the current date variable in the machine
            self.current_trading_date = trading_day.date

            # For every algo - portfolio pair, simulate an entire day no matter what the
            # time frame is.
            for algo_portfolio_pair in self.algo_portfolio_pairs:

                algo = algo_portfolio_pair.algo
                portfolio = algo_portfolio_pair.portfolio

                portfolio._create_new_daily_row_generators(
                    trading_day.open_time_iso, trading_day.close_time_iso)

                while not portfolio._any_generator_reached_end_of_day():
                    portfolio._increment_all_positions()
                    completed_order_ids = portfolio._process_pending_orders()
                    # TODO: Call algorithm increment/run function here

                    if not portfolio._any_generator_reached_end_of_day():
                        # TODO: Change to Logging library
                        print(
                            f"{portfolio.get_current_timestamp()} - "
                            f"${round(portfolio.total_value(), 2):,.2f} - "
                            f"#{portfolio._increment_count}")
