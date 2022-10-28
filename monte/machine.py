from __future__ import annotations

import time
from datetime import timedelta

from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.asset_manager import AssetManager, DataDestination
from monte.machine_settings import MachineSettings
from monte.portfolio import Portfolio


class TradingMachine():
    """
    The virtual embodiment of a trading simulation. It's an enigma... except for all the documentation
    explaining exactly how it works.
    """

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    am: AssetManager
    algo_instances: list[Algorithm]
    epoch_start_time: float

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.am = AssetManager(alpaca_api, machine_settings)
        self.algo_instances = []

    def add_algo_instance(self, algorithm_with_portfolio: Algorithm) -> None:
        """
        Add a new algorithm to the trading machine. The algorithm must be an instance of a subclass of
        Algorithm.
        """

        if not issubclass(type(algorithm_with_portfolio), Algorithm):
            raise TypeError(
                "You must pass an instance of a subclass of Algorithm into add_algo_instance().")

        if not isinstance(algorithm_with_portfolio.get_portfolio(), Portfolio):
            raise TypeError(
                "The get_portfolio() method of the algorithm must be an instance of Portfolio.")

        algorithm_with_portfolio.get_portfolio().am = self.am

        self.algo_instances.append(algorithm_with_portfolio)

    def startup(self) -> None:
        """
        Pre-simulation startup behaviors.
        """
        # Note the start time of the trading machine
        self.epoch_start_time = time.time()

        # Run startup code for algorithms
        for algo in self.algo_instances:
            algo.startup()

        # Add all of the derived columns from each algo to the main derived column dict in
        # self.machine_settings
        for algo in self.algo_instances:
            new_columns = algo.get_derived_columns()
            self.machine_settings.add_derived_columns(new_columns)

        # Run startup code for asset_manager. This must happen after the algos startup code so that the algos
        # can 'watch' all of the assets they need first. When am.startup() is called, the data getter process
        # is constructed and spawned with all of the assets it needs to get data for as an argument.
        self.am.startup()

    def run(self) -> None:
        """
        Runs the trading machine, start to finish.
        """

        # Run Machine startup code
        self.startup()

        algos_have_been_trained = False

        # Run the algorithms
        while True:

            # Update the dataframes in the asset_manager
            try:
                self.am.increment_dataframes()
            except StopIteration:

                # If the algorithms were never trained, train them
                if not algos_have_been_trained:
                    self._train_algos()

                break

            # If the asset_manager is in the testing data phase, run all of the algorithms
            if self.am.data_destination is DataDestination.TESTING_DATA:

                # Runs if the trading_machine just entered the testing data phase.
                if not algos_have_been_trained:
                    self._train_algos()
                    algos_have_been_trained = True

                # Process any orders and run each algorithm
                for algo in self.algo_instances:
                    portfolio = algo.get_portfolio()

                    # Process orders
                    processed_orders = portfolio.process_pending_orders()

                    # Clean up the portfolio
                    portfolio._delete_empty_positions()

                    # Run the algorithm
                    current_datetime = portfolio.am._get_reference_asset().datetime()
                    algo.run_one_time_frame(current_datetime, processed_orders)

        # Run Machine cleanup code
        self.cleanup()

    def _train_algos(self) -> None:
        """
        Calls the train() function on all algorithms
        """
        for algo in self.algo_instances:
            algo.train()

    def cleanup(self) -> None:
        """
        Post-simulation cleanup behaviors.
        """
        # Note the end time for the trading machine
        end_time = time.time()

        # Run cleanup code for algorithms
        for algo in self.algo_instances:
            algo.cleanup()

        # Run cleanup code for asset_manager
        self.am.cleanup()

        # Print out final returns for all algos tested
        print("\n\n -- RESULTS -- \n")
        for algo in self.algo_instances:
            print(f"{algo.name} | ${round(algo.get_portfolio().total_value(), 2):,} | "
                  f"{round(algo.get_portfolio().current_return(), 3):+}%")
        print("\n\n")

        # Print out the total runtime
        print(" -- RUNTIME -- \n")
        total_runtime = int(end_time - self.epoch_start_time)
        hours, remainder = divmod(total_runtime, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours != 0:
            print(f"{hours}h {minutes}m {seconds}s")
        elif minutes != 0:
            print(f"{minutes}m {seconds}s")
        else:
            print(f"{seconds}s")

        print("\n\n")
