from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from functools import wraps
from typing import Any

import pandas as pd


# Using eq=True and frozen=True makes the dataclass automatically hashable
@dataclass(eq=True, frozen=True)
class DFIdentifier():
    """
    Hashable Dataclass that acts as an ID for a Pandas DataFrame
    """
    symbol: str
    timestamp: str
    args: tuple
    kwargs: tuple


class DerivedColumn():
    """
    Turns a function written to be a derived column into an instance of this class so it can be used in
    the trading machine.
    """

    # TODO: Derived columns that are called periodically, once every n-TimeFrames

    func: Callable
    num_rows_needed: int
    args: tuple
    kwargs: dict
    column_dependencies: list[str]

    def __init__(self, func: Callable, num_rows: int, *args, column_dependencies=[], **kwargs):
        self.func = func
        self.num_rows_needed = num_rows
        self.args = args
        self.kwargs = kwargs
        self.column_dependencies = column_dependencies

    def __call__(self, df: pd.DataFrame) -> Any:
        return self.func(df, self.num_rows_needed, *self.args, **self.kwargs)

    def __eq__(self, __o: object) -> bool:
        # If the incoming object is not a DerivedColumn, immediately return false
        if not isinstance(__o, DerivedColumn):
            return False

        # Otherwise, check that all of the values of its attributes are the same
        # Only include data that uniquely defines this DerivedColumn. func, num_rows, args, and kwargs count
        # for this, but other instance attributes don't because they don't define how the derived column
        # function is called.
        if (__o.func == self.func and
                __o.num_rows_needed == self.num_rows_needed and
                __o.args == self.args and
                __o.kwargs == self.kwargs):
            return True
        else:
            return False

    def dependencies_are_fulfilled(
            self, df: pd.DataFrame, all_derived_columns_in_simulation: dict[str, DerivedColumn]) -> bool:
        """
        Returns true if all of this derived column's dependencies have enough data to start calculating the
        derived column.
        """
        # Check all of the dependent columns to see if they have enough data to be used
        all_dependencies_fulfilled = True
        for column_name, column_obj in all_derived_columns_in_simulation.items():

            # Skip the iteration if the column obj is the same as the current instance
            if column_obj is self:
                continue

            # If the derived column is one of this column's dependencies but it hasn't been called enough
            # times to fulfil the dependency
            if column_name in self.column_dependencies and df[column_name].count() < self.num_rows_needed:
                all_dependencies_fulfilled = False
                break

        # Check that the dataframe has enough rows for this derived column
        if len(df.index) < self.num_rows_needed:
            has_num_rows_needed = False
        else:
            has_num_rows_needed = True

        fulfilled_dependencies = all_dependencies_fulfilled and has_num_rows_needed
        return fulfilled_dependencies


def derived_column():
    """
    Wraps around a derived column function to add caching in a way compatible with dataframes.
    """

    def derived_column_inner(func: Callable) -> Callable:
        func.cache_ = {}

        @wraps(func)
        def inner(df: pd.DataFrame, *args, **kwargs) -> Any:

            # TODO: Make this identifier work properly if users pass an argument in either as arg or as kwarg
            current_identifier = DFIdentifier(
                df.iloc[-1].symbol, df.iloc[-1].timestamp, args, tuple(sorted(kwargs.items())))

            # Purge cache if incoming identifier's timestamp is different.
            if any(existing_identifier.timestamp != current_identifier.timestamp
                    for existing_identifier in func.cache_.keys()):
                func.cache_ = {}

            # If the current identifier is not in the cache, add it to the cache
            if current_identifier not in func.cache_:
                func.cache_[current_identifier] = func(df, *args, **kwargs)

            return func.cache_[current_identifier]

        return inner

    return derived_column_inner
