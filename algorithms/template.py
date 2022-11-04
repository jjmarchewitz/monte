from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from derived_columns import DerivedColumn
from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order


class Template(Algorithm):

    def __init__(self, alpaca_api: AlpacaAPIBundle,
                 machine_settings: MachineSettings, name: str, starting_cash: float) -> None:

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(alpaca_api, machine_settings, name, starting_cash)

    def get_derived_columns(self) -> dict[str, DerivedColumn]:
        # Add any derived columns to the dictionary.
        derived_columns = {}

        return derived_columns

    def startup(self) -> None:
        # Watch all of your symbols from here
        # self.portfolio.watch("SYMBOL")
        ...

    def train(self) -> None:
        # Run any training code here. This function gets called after all of the training data is assembled
        # into the training_df of every Position.
        ...

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        # Runs on every time frame (time step). This is the main body of your algorithm
        ...

    def cleanup(self) -> None:
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
