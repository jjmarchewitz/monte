"""
A trading machine is an object that encompasses the running of algorithms with portfolios
attached. These algorithm-portfolio pairs can be either run on historical data or on live data.
"""

from algo_pg.algorithms.trading_algorithm import TradingAlgorithm
from algo_pg.machine.portfolio import Portfolio
from alpaca_trade_api import TimeFrame
from dataclasses import dataclass
from datetime import date, datetime
from pytz import timezone


@dataclass
class MarketDay():
    """
    A dataclass holding information for a single day the market is open, like the date. \
    This dataclass also stores the market open time and close time in the ISO-8601 format.
    """
    date: str
    open_time_iso: str
    close_time_iso: str


@dataclass
class AlgoPortfolioPair():
    """
    A trading algorithm-portfolio pair is run together across a trading machine's timeline\
    as one unit.
    """
    algo: TradingAlgorithm
    portfolio: Portfolio


class TradingMachine():
    """
    The "trading machine" is meant to represent a machine running an algorithm with data \
    across the timeline that are provided as constructor arguments. This encompasses\
    backtesting (testing on historical data) as well as running an algorithm live.
    """

    def __init__(
            self, alpaca_api, start_date, end_date,
            time_frame=TimeFrame.Minute):
        """
        Constructor for the TradingMachine class.

        Args:
            alpaca_api: A bundle of Alpaca APIs all created and authenticated with the keys
                in the repo's alpaca.config.
            start_date: The YYYY-MM-DD formatted date for the trading machine to start its
                run at.
            end_date: The YYYY-MM-DD formatted date for the trading machine to end its
                run at. 
            time_frame: An alpaca_trade_api.TimeFrame value corresponding to the time
                delta between price values. Defaults to TimeFrame.Minute.
        """
        # Bundled alpaca API dataclass
        self.alpaca_api = alpaca_api

        # Attributes to keep track of the time span of the trading_machine
        self.start_date = start_date
        self.end_date = end_date

        # The only supported time frames for this class are minutes, hours, and days.
        self.time_frame = time_frame

        # Create a list of all market days in range with start and end times
        self.market_days = []
        self.current_market_date = None
        self._generate_market_day_list()

        # Pairs of algorithms and portfolios
        self.algo_portfolio_pairs = []

    def _generate_market_day_list(self):
        """
        Generates a list of MarketDay instances in order from self.start_date to self.end_date
        to represent all of the days the market is open, and *only* the days the market is open.
        """
        # Get a list of all market days between start_date and end_date, including their
        # open and close times
        raw_market_days = self.alpaca_api.trading.get_calendar(
            self.start_date, self.end_date)

        for day in raw_market_days:

            # Create a date object (from the datetime library) for the calendar date of the
            # market day
            market_date = date(
                day.date.year,
                day.date.month,
                day.date.day
            )

            # Grab the DST-aware timezone object for eastern time
            timezone_ET = timezone("America/New_York")

            # Create a datetime object for the opening time with the timezone info attached
            open_time = timezone_ET.localize(datetime(
                day.date.year,
                day.date.month,
                day.date.day,
                day.open.hour,
                day.open.minute
            ))

            # Create a datetime object for the closing time with the timezone info attached
            close_time = timezone_ET.localize(datetime(
                day.date.year,
                day.date.month,
                day.date.day,
                day.close.hour,
                day.close.minute
            ))

            # Convert the opening and closing times to ISO-8601
            # Literally dont even fucking ask me how long it took to get the data in the
            # right format for this to work.
            open_time = open_time.isoformat()
            close_time = close_time.isoformat()

            # Create a MarketDay object with the right open/close times and append it to
            # the list of all such MarketDay objects within the span between start_date and
            # end_date
            market_day = MarketDay(market_date, open_time, close_time)
            self.market_days.append(market_day)

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
        for market_day in self.market_days:

            # Update the current date variable in the machine
            self.current_market_date = market_day.date

            # For every algo - portfolio pair, simulate an entire day no matter what the
            # time frame is.
            for algo_portfolio_pair in self.algo_portfolio_pairs:

                algo = algo_portfolio_pair.algo
                portfolio = algo_portfolio_pair.portfolio

                # Create the day's bar generator objects
                portfolio.create_new_bar_generators(
                    self.time_frame,
                    market_day.open_time_iso,
                    market_day.close_time_iso
                )

                # Increment all of the bar generators so that they are on the first value
                # for the day. They begin as "None" and must be incremented to have an
                # initial value.
                portfolio.increment_all_bar_generators()

                # While the trading machine has not yet hit the end of the day
                while not portfolio.market_day_needs_to_be_incremented():
                    print(
                        f"{portfolio.name} -- {portfolio.time_of_last_price_gen_increment} :"
                        + f" ${round(portfolio.total_value(), 2):,}")

                    # This must be at the end of the loop
                    portfolio.increment_all_bar_generators()

            print()
