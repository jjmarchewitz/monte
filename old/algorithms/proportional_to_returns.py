from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from monte import display
from monte.algorithm import Algorithm
from monte.broker import Broker
from monte.column import Column
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class ProportionalToReturns(Algorithm):

    def __init__(self, machine_settings: MachineSettings, name: str, starting_cash: float,
                 symbols: list[str]):

        self.broker = Broker(machine_settings, starting_cash)
        self.name = name
        self.symbols = symbols

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

    def get_derived_columns(self) -> list[Column]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = [
            Column("avg_vwap", dcolumns.mean, 100, "vwap"),
            Column("returns_vwap", dcolumns.returns, 100, "vwap"),
            Column("avg_returns", dcolumns.mean, 100, "returns_vwap", column_dependencies=["returns_vwap"]),
        ]

        return derived_columns

    def startup(self):
        """
        Runs before the simulation starts (and before any training data is acquired).
        """
        # Watch all symbols
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
        # Testing code, called on every time frame
        for symbol, asset in self.broker.assets.items():
            df = asset.testing_df

            current_returns = df.iloc[-1].returns_vwap

            if current_returns < -0.01:
                self.broker.place_order(symbol, -int(current_returns * 100), OrderType.BUY)
            elif current_returns > 0.01:
                self.broker.place_order(symbol, int(current_returns * 100), OrderType.SELL)

        # Print the current datetime with the portfolio's current total value and current return
        display.print_total_value(self.name, self.broker, current_datetime)

    def cleanup(self):
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
