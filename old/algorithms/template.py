from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from derived_columns import Column
from monte.algorithm import Algorithm
from monte.broker import Broker
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class Template(Algorithm):

    def __init__(
            self, machine_settings: MachineSettings, name: str,
            starting_cash: float, symbols: list[str]):

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

    def get_derived_columns(self) -> dict[str, Column]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = {}

        return derived_columns

    def startup(self):
        """
        Runs before the simulation starts (and before any training data is acquired).
        """
        # Watch all of your symbols from here
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
        ...

    def cleanup(self):
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
