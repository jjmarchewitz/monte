import pandas as pd

from derived_columns.decorator import derived_column


@derived_column
def net(df: pd.DataFrame, col: str, n: int) -> float:
    """DOC:"""
    return df.iloc[-n - 1][col] - df.iloc[-1][col]


@derived_column
def mean(df: pd.DataFrame, col: str, n: int) -> float:
    """DOC:"""
    total = 0

    for i in range(1, n + 1):
        total += df.iloc[-i][col]

    avg = total / n

    return avg


@derived_column
def std_dev(df: pd.DataFrame, col: str, n: int) -> float:
    """DOC:"""
    avg = mean(df, col, n)

    sum_of_squared_differences = sum((df.iloc[-i][col] - avg) ** 2 for i in range(1, n + 1))

    std_dev = (sum_of_squared_differences / n) ** 0.5

    return std_dev


@derived_column
def percent_change(df: pd.DataFrame, col: str, n: int) -> float:
    """DOC:"""
    initial = df.iloc[-n - 1][col]
    final = df.iloc[-1][col]

    return ((final - initial) / initial) * 100
