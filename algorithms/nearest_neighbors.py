from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from derived_columns import DerivedColumn
from monte import display
from monte.algorithm import Algorithm
from monte.broker import Broker
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class NearestNeighbors(Algorithm):

    def __init__(
            self, machine_settings: MachineSettings, name: str,
            starting_cash: float, symbols: list[str], decision_interval: tuple[float, float],
            variability_constant: float):

        self.broker = Broker(machine_settings, starting_cash)
        self.name = name
        self.symbols = symbols

        self.lower_bound, self.upper_bound = decision_interval
        self.variability_constant = variability_constant

    def get_broker(self) -> Broker:
        """
        Returns this algorithm's broker instance.
        """
        return self.broker

    def get_name(self) -> str:
        """
        Returns the name of this instance, used to help identify this instance in print statements.
        """
        return self.name

    def get_derived_columns(self) -> dict[str, DerivedColumn]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = {
            'returns_last_2': DerivedColumn(dcolumns.returns, 2, "vwap"),
            f'infimum_last_5_K{self.variability_constant}':
                DerivedColumn(dcolumns.infimum, 5, 'returns_last_2', self.variability_constant),
            f'nearest_neighbor_last_5_K{self.variability_constant}':
                DerivedColumn(
                    dcolumns.nearest_neighbor, 5, f'infimum_last_5_K{self.variability_constant}',
                    'returns_last_2',
                    column_dependencies=['returns_last_2', f'infimum_last_5_K{self.variability_constant}']), }

        return derived_columns

    def startup(self):
        """
        Runs before the simulation starts (and before any training data is acquired).
        """
        for symbol in self.symbols:
            self.broker.watch(symbol)

    def train(self):
        """
        Runs right before the end of the training phase of the simulation (after the training data is
        acquired). Train any models here.
        """
        # Training code, called once
        ...

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]):
        """
        Runs on every time frame during the testing phase of the simulation. This is the main body of the
        algorithm.
        """

        for symbol, asset in self.broker.assets.items():

            df = asset.testing_df

            # breakpoint()
            if df.iloc[-1][f'nearest_neighbor_last_5_K{self.variability_constant}'] < self.lower_bound:
                self.broker.place_order(symbol, 20, OrderType.BUY)

            elif df.iloc[-1][f'nearest_neighbor_last_5_K{self.variability_constant}'] > self.upper_bound:
                self.broker.place_order(symbol, 20, OrderType.SELL)

        display.print_total_value(self.name, self.broker, current_datetime)
        # Testing code, called on every time frame

    def cleanup(self):
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
