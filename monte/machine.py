from __future__ import annotations

from monte.algorithm import Algorithm
from monte.asset_manager import AssetManager
from monte.machine_settings import MachineSettings
from monte.portfolio import Portfolio
from monte.util import AlpacaAPIBundle


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

        algorithm_with_portfolio.get_portfolio().am = self.am

        if (isinstance(algorithm_with_portfolio, Algorithm) and
                isinstance(algorithm_with_portfolio.get_portfolio(), Portfolio)):
            self.algo_instances.append(algorithm_with_portfolio)

    def run(self):
        """DOC:"""

        # Run startup code for algorithms
        for algo in self.algo_instances:
            algo.startup()

        # Run the algorithms
        while True:

            # Process any orders and run each algorithm
            for algo in self.algo_instances:
                portfolio = algo.get_portfolio()
                processed_orders = portfolio.process_pending_orders()
                portfolio.delete_empty_positions()
                algo.run_one_time_frame(processed_orders)

            # Update the dataframes in the asset_manager
            try:
                self.am.increment_dataframes()
            except StopIteration:
                break

        # Run cleanup code for algorithms
        for algo in self.algo_instances:
            algo.cleanup()

        # Run cleanup code for asset_manager
        self.am.cleanup()
