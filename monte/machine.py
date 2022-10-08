"""DOC:"""
from __future__ import annotations

import monte.algorithm as algorithm
import monte.asset_manager as asset_manager
import monte.machine_settings as machine_settings
import monte.portfolio as portfolio
import monte.util as util


class TradingMachine():
    """DOC:"""

    alpaca_api: util.AlpacaAPIBundle
    machine_settings: machine_settings.MachineSettings
    am: asset_manager.AssetManager
    algo_instances: list[algorithm.Algorithm]

    def __init__(self, alpaca_api: util.AlpacaAPIBundle,
                 machine_settings: machine_settings.MachineSettings) -> None:
        self.alpaca_api = alpaca_api
        self.machine_settings = machine_settings
        self.am = asset_manager.AssetManager(alpaca_api, machine_settings)
        self.algo_instances = []

    def add_algo_instance(self, algorithm_with_portfolio: algorithm.Algorithm):
        """DOC:"""

        algorithm_with_portfolio.get_portfolio().am = self.am

        if (isinstance(algorithm_with_portfolio, algorithm.Algorithm) and
                isinstance(algorithm_with_portfolio.get_portfolio(), portfolio.Portfolio)):
            self.algo_instances.append(algorithm_with_portfolio)

    def run(self):
        """DOC:"""

        for algo in self.algo_instances:
            algo.startup()

        while True:

            # TODO: Test the order of these blocks

            print(self.am['AAPL'].iloc[-1].datetime.isoformat())

            # A
            for algo in self.algo_instances:
                portfolio = algo.get_portfolio()
                processed_orders = portfolio.process_pending_orders()
                portfolio.delete_empty_positions()
                algo.run_one_time_frame(processed_orders)

            # B
            try:
                self.am.increment_dataframes()
            except StopIteration:
                break


# Increment dataframes, then run algo
