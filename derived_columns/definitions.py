from dataclasses import dataclass

import pandas as pd
from numpy.typing import ArrayLike
from scipy.fft import fft, fftfreq

from derived_columns._base import derived_column


@derived_column()
def net(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the difference in value between the bottom-most row and the nth-to-last row of the given column.
    """
    return df.iloc[-n][col] - df.iloc[-1][col]


@derived_column()
def mean(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the mean value of the bottom n-rows of the given column.
    """
    total = sum(df.iloc[-i][col] for i in range(1, n + 1))

    return total / n


@derived_column()
def std_dev(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the standard deviation of the bottom n-rows of the given column.
    """
    avg = mean(df, n, col)
    sum_of_squared_differences = sum((df.iloc[-i][col] - avg) ** 2 for i in range(1, n + 1))
    return (sum_of_squared_differences / n) ** 0.5


@derived_column()
def returns(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the percent change over the bottom n-rows of the given column.
    """
    initial = df.iloc[-n][col]
    final = df.iloc[-1][col]
    return ((final - initial) / initial)


@dataclass
class FFTResult:
    """
    Dataclass to store the result of an FFT of data.
    """
    fft: tuple
    fftfreq: ArrayLike


@derived_column()
def fourier_transform(df: pd.DataFrame, n: int, col: str):
    """
    Returns the Fast Fourier Transform of the bottom n-rows of a given column.
    """
    np_array_of_col = df.tail(n)[col].to_numpy()

    result = FFTResult(
        fft(np_array_of_col),
        fftfreq(n)
    )

    return result
