from dataclasses import dataclass
from functools import wraps

import pandas as pd


# Using eq=True and frozen=True makes the dataclass automatically hashable
@dataclass(eq=True, frozen=True)
class DFIdentifier():
    """
    Hashable Dataclass that acts as an ID for a Pandas DataFrame
    """
    symbol: str
    timestamp: str


def derived_column(func):
    """
    Wraps around a derived column function

    Args:
        func: A function that takes in a pd.DataFrame and returns a single value based on the bottom rows.

    Returns:
        A derived column function with a cache
    """
    func.cache_ = {}

    @wraps(func)
    def inner(df: pd.DataFrame, *args, **kwargs):

        current_identifier = DFIdentifier(df.iloc[-1].symbol, df.iloc[-1].timestamp)

        # Purge cache if incoming identifier's timestamp is different.
        if any(existing_identifier.timestamp != current_identifier.timestamp
               for existing_identifier in func.cache_.keys()):
            func.cache_ = {}

        # If the current identifier is not in the cache, add it to the cache
        if current_identifier not in func.cache_:
            func.cache_[current_identifier] = func(df, *args, **kwargs)

        return func.cache_[current_identifier]

    return inner
