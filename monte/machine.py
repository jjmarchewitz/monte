from __future__ import annotations

from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.asset_manager import AssetManager
from monte.machine_settings import MachineSettings
from monte.portfolio import Portfolio


class TradingMachine():
    """DOC:"""

    alpaca_api: AlpacaAPIBundle
    machine_settings: MachineSettings
    am: AssetManager
    algo_instances: list[Algorithm]

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.am = AssetManager(alpaca_api, machine_settings)
        self.algo_instances = []

    def add_algo_instance(self, algorithm_with_portfolio: Algorithm):
        """DOC:"""

        if not isinstance(algorithm_with_portfolio, Algorithm):
            raise TypeError("You must pass an instance of a subclass of Algorithm into add_algo_instance().")

        if not isinstance(algorithm_with_portfolio.get_portfolio(), Portfolio):
            raise TypeError("The get_portfolio() method of the algorithm must be an instance of Portfolio.")

        algorithm_with_portfolio.get_portfolio().am = self.am

        self.algo_instances.append(algorithm_with_portfolio)

    def startup(self):
        """DOC:"""

        # Run startup code for algorithms
        for algo in self.algo_instances:
            algo.startup()

        # Run startup code for asset_manager. This must happen after the algos startup code so that the algos
        # can 'watch' all of the assets they need first. When am.startup() is called, the data getter process
        # is constructed and spawned with all of the assets it needs to get data for as an argument.
        self.am.startup()

    def run(self):
        """DOC:"""

        # Run Machine startup code
        self.startup()

        # Run the algorithms
        while True:

            # Update the dataframes in the asset_manager
            try:
                self.am.increment_dataframes()
            except StopIteration:
                break

            # Process any orders and run each algorithm
            for algo in self.algo_instances:
                portfolio = algo.get_portfolio()
                processed_orders = portfolio.process_pending_orders()
                portfolio.delete_empty_positions()
                current_datetime = portfolio.am._get_reference_asset().datetime()
                algo.run_one_time_frame(current_datetime, processed_orders)

        # Run Machine cleanup code
        self.cleanup()

    def cleanup(self):
        """DOC:"""

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
        print("\n")
