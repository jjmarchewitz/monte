from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from derived_columns import Column
from monte import display
from monte.algorithm import Algorithm
from monte.broker import Broker
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class NaiveSharpe(Algorithm):

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
        n = 30
        derived_columns = {
            "returns_n_hr": Column(dcolumns.returns, n, "vwap"),
            "std_n_hr": Column(dcolumns.std_dev, n, "vwap"),
            "naivesharpe": Column(dcolumns.naive_sharpe, n, "vwap")
        }
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

        # Unpacking position tuple to extract position and selling all positions
        for symbol, position in self.broker.portfolio.items():
            self.broker.place_order(
                symbol, position.quantity, OrderType.SELL)
        # Sorts all Symbols in terms of Sharpe Ratio
        sharpe_ratio_list = []

        for symbol, asset in self.broker.assets.items():
            sharpe_ratio = asset.testing_df.iloc[-1].naivesharpe
            sharpe_ratio_list.append((symbol, sharpe_ratio))

        sharpe_ratio_list = sorted(sharpe_ratio_list, key=lambda x: x[1], reverse=True)

        top_ten = sharpe_ratio_list[0:9]
        # Buys 10 Shares of the Top 10
        for symbol, _ in top_ten:
            self.broker.place_order(symbol, 10, OrderType.BUY)
        # THIS ALGO KINDA WORKS
        # WOOOOO FUCK YEAH WOOOOO

        # Print the current datetime with the portfolio's current total value and current return
        display.print_total_value(self.name, self.broker, current_datetime)

    def cleanup(self):
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
