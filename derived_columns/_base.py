import inspect
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


def derived_column(func: Callable) -> Callable:
    """
    Wraps around a derived column function to add caching and other important behaviors.
    """

    func.cache_ = {}

    @wraps(func)
    def inner(df: pd.DataFrame, *args, **kwargs) -> Any:

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
