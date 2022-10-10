import pandas as pd

from derived_columns.decorator import DFIdentifier, derived_column


@derived_column
def net_over_last_n(ident: DFIdentifier, df: pd.DataFrame, col: str, n: int) -> float:
    """DOC:"""
    return df.iloc[-n - 1][col] - df.iloc[-1][col]


@derived_column
def avg_over_last_n(ident: DFIdentifier, df: pd.DataFrame, col: str, n: int) -> float:
    """DOC:"""
    total = 0

    for i in range(1, n + 1):
        total += df.iloc[-i][col]

    avg = total / n

    return avg


@derived_column
def std_dev_over_last_n(ident: DFIdentifier, df: pd.DataFrame, col: str, n: int) -> float:
    """DOC:"""

    avg = avg_over_last_n(ident, df, col, n)

    sum_of_squared_differences = sum([(df.iloc[-i][col] - avg) ** 2 for i in range(1, n + 1)])

    std_dev = (sum_of_squared_differences / n) ** 0.5

    return std_dev
