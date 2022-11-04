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
    """DOC:"""

    func: Callable
    num_rows: int
    args: tuple
    kwargs: dict

    def __init__(self, func: Callable, num_rows: int, *args, **kwargs) -> None:
        self.func = func
        self.num_rows = num_rows
        self.args = args
        self.kwargs = kwargs

    def __call__(self, df: pd.DataFrame) -> Any:
        return self.func(df, self.num_rows, *self.args, **self.kwargs)

    def __eq__(self, __o: object) -> bool:
        # If the incoming object is not a DerivedColumn, immediately return false
        if not isinstance(__o, DerivedColumn):
            return False

        # Otherwise, check that all of the values of its attributes are the same
        if (__o.func == self.func and
                __o.num_rows == self.num_rows and
                __o.args == self.args and
                __o.kwargs == self.kwargs):
            return True
        else:
            return False


def cache_derived_column(func: Callable) -> Callable:
    """
    Wraps around a derived column function to add caching.
    """

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
        else:
            breakpoint()

        return func.cache_[current_identifier]

    return inner
