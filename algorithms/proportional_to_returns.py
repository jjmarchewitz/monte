from __future__ import annotations

from datetime import datetime
from enum import Enum

import derived_columns.definitions as dcolumns
from derived_columns import DerivedColumn
from monte import display
from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class ProportionalToReturns(Algorithm):

    def __init__(self, machine_settings: MachineSettings, name: str, starting_cash: float,
                 symbols: list[str]) -> None:

        # TODO: Make the declaration of Portfolio more explicit. Somehow force the user to do it themselves,
        # but in a standard way

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(machine_settings, name, starting_cash, symbols)

    def get_derived_columns(self) -> dict[str, DerivedColumn]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = {
            "avg_vwap": DerivedColumn(dcolumns.mean, 100, "vwap"),
            "returns_vwap": DerivedColumn(dcolumns.returns, 100, "vwap"),
            "avg_returns": DerivedColumn(dcolumns.mean, 100, "returns_vwap", column_dependencies=["returns_vwap"]),
        }

        return derived_columns

    def startup(self) -> None:
        """
        Runs before the simulation starts (and before any training data is acquired).
        """
        # Watch all symbols
        for symbol in self.symbols:
            self.portfolio.watch(symbol)

        # Buy 10 shares of all symbols
        for _ in range(1, 10):
            for symbol in self.symbols:
                self.portfolio.place_order(symbol, 1, OrderType.BUY)

    def train(self) -> None:
        """
        Runs right before the end of the training phase of the simulation (after the training data is
        acquired). Train any models here.
        """
        # Training code, called once
        ...

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        """
        Runs on every time frame during the testing phase of the simulation. This is the main body of the
        algorithm.
        """
        # Testing code, called on every time frame
        for symbol, position in self.portfolio.positions.items():
            df = position.testing_df

            current_returns = df.iloc[-1].returns_vwap

            if current_returns < -0.01:
                self.portfolio.place_order(symbol, -int(current_returns * 100), OrderType.BUY)
            elif current_returns > 0.01:
                self.portfolio.place_order(symbol, int(current_returns * 100), OrderType.SELL)

        # Print the current datetime with the portfolio's current total value and current return
        display.print_total_value(self.name, self.portfolio, current_datetime)

    def cleanup(self) -> None:
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
