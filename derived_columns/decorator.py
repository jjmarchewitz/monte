import inspect
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
    args: tuple
    kwargs: tuple


def derived_column(num_rows_arg_name: str | None = None):
    """
    Wraps around a derived column function to add caching and other important behaviors.
    """

    def derived_column_inner(func):
        """
        Bruh wtf is this decorator nest.
        """
        func.cache_ = {}

        # Parse args of the passed in function to validate them
        argspec = inspect.getfullargspec(func)

        if len(argspec.args) > 1 or 'df' not in argspec.args:
            raise TypeError("All arguments in a derived column other than df must be keyword-only arguments.")

        # Check if num_rows_var_name is the name of an argument of the function
        if num_rows_arg_name in argspec.kwonlyargs:
            # If so, set it as a function variable
            func.num_rows_arg_name = num_rows_arg_name

        @wraps(func)
        def inner(df: pd.DataFrame, *args, **kwargs):

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
