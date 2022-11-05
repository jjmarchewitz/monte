from dataclasses import dataclass

import pandas as pd
from numpy.typing import ArrayLike
from scipy.fft import fft, fftfreq

from derived_columns._base import cache_derived_column


@cache_derived_column
def net(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the difference in value between the bottom-most row and the nth-to-last row of the given column.
    """
    return df.iloc[-n][col] - df.iloc[-1][col]


@cache_derived_column
def mean(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the mean value of the bottom n-rows of the given column.
    """

    total = sum(df.iloc[-i][col] for i in range(1, n + 1))

    return total / n


@cache_derived_column
def std_dev(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the standard deviation of the bottom n-rows of the given column.
    """
    avg = mean(df, n, col)
    sum_of_squared_differences = sum(
        (df.iloc[-i][col] - avg) ** 2 for i in range(1, n + 1))
    return (sum_of_squared_differences / n) ** 0.5


@cache_derived_column
def returns(df: pd.DataFrame, n: int, col: str) -> float:
    """
    Returns the percent change over the bottom n-rows of the given column.
    """
    initial = df.iloc[-n][col]
    final = df.iloc[-1][col]
    return ((final - initial) / initial)


@cache_derived_column
def infimum(df: pd.DataFrame, n: int, col: str, k: float) -> float:
    """

    Returns a lower bound for the rolling average series using the following expression:

    mean(col) - k * std_dev(col)


    """
    roll_avg = mean(df, n, col)
    roll_sd = std_dev(df, n, col)
    lower_bound = roll_avg - k*roll_sd

    return lower_bound


@cache_derived_column
def nearest_neighbor(df: pd.DataFrame, n: int, infimum_column: str, returns_column: str) -> float:
    """

    Returns the predicted value of column based on similarity score using the following algorithm:

    x_1 - predictor 1
    x_2 - predictor 2

    (x_1 - x_2)^2 


    """
    distances = []
    recent_rolling_avg = mean(df, n, returns_column)
    bottom_rows = df.tail(n)

    for row in bottom_rows.iterrows():
        breakpoint()
        distance = (recent_rolling_avg - row[infimum_column]) ^ 2
        distances.append(distance)

    # goal: find nearest neighbor

    # method: iterate by the row and the distance value
    # set the current distance and nearest neighbor to the first value
    # iterate by row and distance
    # match the nearest neighbor, by finding the minimum distance,
    # and then getting the returns at that row
    lowest_distance = distances[0]
    nearest_neighbor = bottom_rows.iloc[0][returns_column]
    for row, distance in zip(bottom_rows.iterrows(), distances):
        if distance < lowest_distance:
            lowest_distance = distance
            nearest_neighbor = row[returns_column]

    return nearest_neighbor


@dataclass
class FFTResult:
    """
    DOC:
    """
    fft: tuple
    fftfreq: ArrayLike


@cache_derived_column
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
