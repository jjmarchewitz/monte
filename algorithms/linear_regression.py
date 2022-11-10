from __future__ import annotations

from datetime import datetime

import derived_columns.definitions as dcolumns
from derived_columns import DerivedColumn
from monte.algorithm import Algorithm
from monte.api import AlpacaAPIBundle
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderType
from derived_columns import DerivedColumn
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import numpy as np


class LinearRegressionAlgo(Algorithm):

    def __init__(
            self, alpaca_api: AlpacaAPIBundle, machine_settings: MachineSettings, name: str,
            starting_cash: float, symbols: list[str], decision_interval: tuple[float, float],
            variability_constant: float) -> None:

        # Sets up instance variables and instantiates a Portfolio as self.portfolio
        super().__init__(alpaca_api, machine_settings, name, starting_cash, symbols)

        self.lower_bound, self.upper_bound = decision_interval
        self.variability_constant = variability_constant

    def get_derived_columns(self) -> dict[str, DerivedColumn]:
        """
        Returns a dictionary containing the derived columns this algorithm needs to run.
        """
        # Add any derived columns to the dictionary.
        derived_columns = {'returns_last_2': DerivedColumn(dcolumns.returns, 2, "vwap"),
                           'infimum_last_5': DerivedColumn(dcolumns.infimum, 5, 'returns_last_2', self.variability_constant),
                           'norm_last_2': DerivedColumn(dcolumns.infimum_norm, 1, 'infimum_last_5', 'returns_last_2',
                                                        column_dependencies=['returns_last_2', 'infimum_last_5']),
                           # 'prediction_returns': DerivedColumn(dcolumns.linear_regression_prediction, 2,
                           # 'returns_last_2', 'norm_last_2')
                           }

        return derived_columns

    def startup(self) -> None:
        """
        Runs before the simulation starts (and before any training data is acquired).
        """
        # Watch all of your symbols from here
        for symbol in self.symbols:
            self.portfolio.watch(symbol)

    def train(self) -> None:
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

    def run_one_time_frame(self, current_datetime: datetime, processed_orders: list[Order]) -> None:
        """
        Runs on every time frame during the testing phase of the simulation. This is the main body of the
        algorithm.
        """
        # Testing code, called on every time frame
        for symbol in self.symbols:

            # breakpoint()
            df = self.portfolio.get_testing_df(symbol)
    # hw
            X = df.norm_last_2.values
            y = df.returns_last_2.values

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
                self.portfolio.place_order(symbol, 20, OrderType.BUY)

            elif returns_pred > self.upper_bound:
                self.portfolio.place_order(symbol, 20, OrderType.SELL)

        print(
            f"{current_datetime.date()} {current_datetime.hour:02d}:{current_datetime.minute:02d} | "
            f"${round(self.portfolio.total_value, 2):,.2f} | "
            f"{round(self.portfolio.current_return, 3):+.3f}%")

    def cleanup(self) -> None:
        """
        Runs after the end of the testing phase of the simulation. Run any needed post-simulation code here.
        """
        # Runs once the simulation is over and the last TimeFrame has been run.
        ...
