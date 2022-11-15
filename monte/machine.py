from __future__ import annotations

import time
from datetime import timedelta

import pandas as pd
from tabulate import tabulate

from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.asset_manager import AssetManager, DataDestination
from monte.broker import Broker
from monte.machine_settings import MachineSettings
from monte.portfolio import Portfolio


class TradingMachine():
    """
    The virtual embodiment of a trading simulation. It's an enigma... except for all the documentation
    explaining exactly how it works.
    """

    machine_settings: MachineSettings
    asset_manager: AssetManager
    algo_instances: list[Algorithm]
    epoch_start_time: float
    _results_df: pd.DataFrame

    def __init__(self, machine_settings: MachineSettings):
        self.machine_settings = machine_settings
        self.asset_manager = AssetManager(machine_settings)
        self.algo_instances = []

    def add_algo(self, *args: Algorithm):
        """
        Add one or more algorithms to the trading machine. The algorithms must be instances of a subclass of
        monte.Algorithm.
        """

        for algo in args:

            if not issubclass(type(algo), Algorithm):
                raise TypeError(
                    "You must pass an instance of a subclass of monte.algorithm.Algorithm into add_algos().")

            if not isinstance(algo.get_broker(), Broker):
                raise TypeError(
                    "The get_broker() method of the algorithm must return an instance of monte.broker.Broker.")

            if algo in self.algo_instances:
                continue

            algo.get_broker().set_asset_manager(self.asset_manager)

            self.algo_instances.append(algo)

    def startup(self):
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
        self.asset_manager.startup()

    def run(self):
        """
        Runs the trading machine, start to finish.
        """

        # Run Machine startup code
        self.startup()

        algos_have_been_trained = False
        first_iteration = True

        # Run the algorithms
        while True:

            # Update the dataframes in the asset_manager
            try:
                self.asset_manager.increment_dataframes()
            except StopIteration:

                # If the algorithms were never trained, train them
                if not algos_have_been_trained:
                    self._train_algos()

                break

            # Runs on the first iteration if starting from the training data phase
            if first_iteration and self.asset_manager.data_destination is DataDestination.TRAINING_DATA:
                print("Entering training phase of the simulation, downloading training data.")
                first_iteration = False

            # If the asset_manager is in the testing data phase, run all of the algorithms
            elif self.asset_manager.data_destination is DataDestination.TESTING_DATA:

                # Runs if the trading_machine just entered the testing data phase.
                if not algos_have_been_trained:
                    print("Calling train() on all algorithms.")
                    self._train_algos()
                    algos_have_been_trained = True
                    print("Entering testing phase of the simulation.")

                # Process any orders and run each algorithm
                for algo in self.algo_instances:

                    # Process pending orders
                    processed_orders = algo.get_broker().process_pending_orders()

                    # Remove any empty positions in the portfolio
                    algo.get_broker().portfolio._delete_empty_positions()

                    # Run the algorithm
                    current_datetime = self.asset_manager.latest_datetime
                    algo.run_one_time_frame(current_datetime, processed_orders)

        # Run Machine cleanup code
        self.cleanup()

    def _train_algos(self):
        """
        Calls the train() function on all algorithms
        """
        for algo in self.algo_instances:
            algo.train()

    @property
    def results_df(self):
        """
        Returns a dataframe with all of the algorithm names and their final portfolio value and returns.
        """
        return self._results_df

    def cleanup(self):
        """
        Post-simulation cleanup behaviors.
        """
        # Note the end time for the trading machine
        end_time = time.time()

        # Run cleanup code for algorithms
        for algo in self.algo_instances:
            algo.cleanup()

        # Run cleanup code for asset_manager
        self.asset_manager.cleanup()

        # Print out final returns for all algos tested
        print("\n\n -- RESULTS --\n")
        print(f"\nSimulated {len(self.algo_instances)} trading algorithms and "
              f"{len(self.asset_manager.watched_assets.keys())} assets from "
              f"{self.machine_settings.start_date.date().isoformat()} to "
              f"{self.machine_settings.end_date.date().isoformat()} using a time frame of "
              f"{self.machine_settings.time_frame.amount} {self.machine_settings.time_frame.unit}(s)\n")
        results = []
        for algo in self.algo_instances:
            results.append({
                "Name": algo.get_name(),
                "Total Value": f"${round(algo.get_broker().portfolio.total_value, 2):,.2f}",
                "Return": f"{round(algo.get_broker().portfolio.current_return, 3):+.3f}%",
            })

        self._results_df = pd.DataFrame(results)

        print(tabulate(results, headers="keys", tablefmt="outline", colalign=("center", "center", "center")))
        print("\n")

        # Print out the total runtime
        print("Total runtime was ", end="")
        total_runtime = int(end_time - self.epoch_start_time)
        hours, remainder = divmod(total_runtime, 3600)
        minutes, seconds = divmod(remainder, 60)

        if hours != 0:
            print(f"{hours}h {minutes}m {seconds}s.")
        elif minutes != 0:
            print(f"{minutes}m {seconds}s.")
        else:
            print(f"{seconds}s.")

        print("\n\n")
