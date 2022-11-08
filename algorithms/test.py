from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from derived_columns import DerivedColumn
from monte import display
from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class TestAlg(Algorithm):

    def __init__(
            self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings, name: str,
            starting_cash: float, symbols: list[str]) -> None:

        # TODO: Make the declaration of Portfolio more explicit. Somehow force the user to do it themselves,
        # but in a standard way

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(alpaca_api, machine_settings, name, starting_cash, symbols)

    def get_derived_columns(self) -> dict[str, DerivedColumn]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = {
            # "net_l10": DerivedColumn(dcolumns.net, 10, "vwap"),
            "avg_l10": DerivedColumn(dcolumns.mean, 10, "vwap"),
            # "avg_l30": DerivedColumn(dcolumns.mean, 30, "vwap"),
            # "std_dev_l10": DerivedColumn(dcolumns.std_dev, 10, "vwap"),
            "returns_l10": DerivedColumn(dcolumns.returns, 10, "vwap"),
            # "fft_l20": DerivedColumn(dcolumns.fourier_transform, 20, "vwap"),
            "avg_returns_l10": DerivedColumn(dcolumns.mean, 10, "returns_l10", column_dependencies=["returns_l10"]),
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

            # If the percent change over the last 10 rows is less than -1%, buy a share.
            if df.iloc[-1].returns_l10 < -1:
                self.portfolio.place_order(symbol, 1, OrderType.BUY)

            # If the percent change over the last 10 rows is more than 1%, sell a share.
            elif df.iloc[-1].returns_l10 > 1:
                self.portfolio.place_order(symbol, 1, OrderType.SELL)

        # Print the current datetime with the portfolio's current total value and current return
        display.print_total_value(self.portfolio, current_datetime)

    def cleanup(self) -> None:
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
