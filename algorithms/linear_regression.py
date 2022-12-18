from __future__ import annotations

from datetime import datetime
from enum import Enum

import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

import derived_columns.definitions as dcolumns
from derived_columns import Column
from monte import display
from monte.algorithm import Algorithm
from monte.broker import Broker
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType


class LinearRegressionAlgo(Algorithm):

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

    def get_derived_columns(self) -> dict[str, Column]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = {
            'returns_last_2': Column(dcolumns.returns, 2, "vwap"),
            f'infimum_last_5_K{self.variability_constant}': Column(dcolumns.infimum, 5, 'returns_last_2', self.variability_constant),
            f'norm_last_2_K{self.variability_constant}': Column(dcolumns.infimum_norm, 1, f'infimum_last_5_K{self.variability_constant}', 'returns_last_2',
                                                                column_dependencies=[f'infimum_last_5_K{self.variability_constant}', 'returns_last_2']),
            # 'prediction_returns': Column(dcolumns.linear_regression_prediction, 2,
            # 'returns_last_2', 'norm_last_2')
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
       # for symbol in self.symbols:

        #  df = self.portfolio.get_training_df(symbol)

        #  X = df.norm_last_2.values
        #  y = df.returns_last_2.values

        #  x_train_norm, x_test_norm, y_train_returns, y_test_returns = train_test_split(
        #      X, y, test_size=0.30)
        #  x_train_norm = np.reshape(x_train_norm, (-1, 1))
        #   x_test_norm = np.reshape(x_test_norm, (-1, 1))
        #   y_train_returns = np.reshape(y_train_returns, (-1, 1))
        #   y_test_returns = np.reshape(y_test_returns, (-1, 1))
        #   model = LinearRegression()
        #   model_fit = model.fit(x_train_norm, y_train_returns)

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]):
        """
        Runs on every time frame during the testing phase of the simulation. This is the main body of the
        algorithm.
        """
        # Testing code, called on every time frame
        for symbol, asset in self.broker.assets.items():

            # breakpoint()
            df = asset.testing_df
    # hw

            X = df[f'norm_last_2_K{self.variability_constant}'].values
            y = df[f'infimum_last_5_K{self.variability_constant}'].values

            x_train_norm, x_test_norm, y_train_returns, y_test_returns = train_test_split(
                X, y, test_size=0.30)
            x_train_norm = np.reshape(x_train_norm, (-1, 1))
            x_test_norm = np.reshape(x_test_norm, (-1, 1))
            y_train_returns = np.reshape(y_train_returns, (-1, 1))
            y_test_returns = np.reshape(y_test_returns, (-1, 1))
            model = LinearRegression()
            model_fit = model.fit(x_train_norm, y_train_returns)
            prediction = model_fit.predict(x_test_norm)

            returns_pred = prediction.mean()
            # breakpoint()
            if returns_pred < self.lower_bound:
                self.broker.place_order(symbol, 20, OrderType.BUY)

            elif returns_pred > self.upper_bound:
                self.broker.place_order(symbol, 20, OrderType.SELL)

        display.print_total_value(self.name, self.broker, current_datetime)

    def cleanup(self):
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
