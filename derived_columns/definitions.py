from dataclasses import dataclass

import pandas as pd
from numpy.typing import ArrayLike
from scipy.fft import fft, fftfreq
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split

from derived_columns._base import derived_column


@derived_column()
def net(df: pd.DataFrame, num_rows: int, col: str) -> float:
    """
    Returns the difference in value between the bottom-most row and the nth-to-last row of the given column.
    """
    return df.iloc[-num_rows][col] - df.iloc[-1][col]


@derived_column()
def mean(df: pd.DataFrame, num_rows: int, col: str) -> float:
    """
    Returns the mean value of the bottom n-rows of the given column.
    """

    total = sum(df.iloc[-i][col] for i in range(1, num_rows + 1))

    return total / num_rows


@derived_column()
def std_dev(df: pd.DataFrame, num_rows: int, col: str) -> float:
    """
    Returns the standard deviation of the bottom n-rows of the given column.
    """
    avg = mean(df, num_rows, col)
    sum_of_squared_differences = sum(
        (df.iloc[-i][col] - avg) ** 2 for i in range(1, num_rows + 1))
    return (sum_of_squared_differences / num_rows) ** 0.5


@derived_column()
def returns(df: pd.DataFrame, num_rows: int, col: str) -> float:
    """
    Returns the percent change over the bottom n-rows of the given column.
    """
    initial = df.iloc[-num_rows][col]
    final = df.iloc[-1][col]
    return ((final - initial) / initial)


@derived_column()
def infimum(df: pd.DataFrame, num_rows: int, col: str, k: float) -> float:
    """

    Returns a lower bound for the rolling average series using the following expression:

    mean(col) - k * std_dev(col)


    """
    roll_avg = mean(df, num_rows, col)
    roll_sd = std_dev(df, num_rows, col)
    lower_bound = roll_avg - k * roll_sd

    return lower_bound


@derived_column()
def infimum_norm(df: pd.DataFrame, num_rows: int, infimum_column: str, returns_column: str) -> float:
   # breakpoint()
    rolling_avg = mean(df, num_rows, returns_column)
    bottom_rows = df.tail(num_rows)
    norm = (rolling_avg - bottom_rows[infimum_column])**2
    value = norm.values[0]

    return value


@derived_column()
def linear_regression_prediction(
        df: pd.DataFrame, num_rows: int, returns_column: str, inf_norm_column: str) -> float:

   # breakpoint()
    x_train_norm, x_test_norm, y_train_returns, y_test_returns = train_test_split(
        inf_norm_column, returns_column, test_size=0.30)
    model = LinearRegression()
    model_fit = model.fit(x_train_norm, y_train_returns)
    prediction = model_fit.predict(x_test_norm)

    return prediction


@derived_column()
def nearest_neighbor(df: pd.DataFrame, num_rows: int, infimum_column: str, returns_column: str) -> float:
    """

    Returns the predicted value of column based on similarity score using the following algorithm:

    x_1 - predictor 1
    x_2 - predictor 2

    (x_1 - x_2)^2


    """
    distances = []
    recent_rolling_avg = mean(df, num_rows, returns_column)
    bottom_rows = df.tail(num_rows)

    for _, row in bottom_rows.iterrows():
        # breakpoint()
        distance = (recent_rolling_avg - row[infimum_column])**2
        #distance = abs(recent_rolling_avg - row[infimum_column])
        distances.append(distance)

    # goal: find nearest neighbor

    # method: iterate by the row and the distance value
    # set the current distance and nearest neighbor to the first value
    # iterate by row and distance
    # match the nearest neighbor, by finding the minimum distance,
    # and then getting the returns at that row
    lowest_distance = distances[0]
    nearest_neighbor = bottom_rows.iloc[0][returns_column]
    for (_, row), distance in zip(bottom_rows.iterrows(), distances):
        if distance < lowest_distance:
            lowest_distance = distance
            nearest_neighbor = row[returns_column]

    return nearest_neighbor


@dataclass
class FFTResult:
    """
    Dataclass to store the result of an FFT of data.
    """
    fft: tuple
    fftfreq: ArrayLike


@derived_column()
def fourier_transform(df: pd.DataFrame, num_rows: int, col: str):
    """
    Returns the Fast Fourier Transform of the bottom n-rows of a given column.
    """
    np_array_of_col = df.tail(num_rows)[col].to_numpy()

    result = FFTResult(
        fft(np_array_of_col),
        fftfreq(num_rows)
    )

    return result


@derived_column()
def naive_sharpe(df: pd.DataFrame, num_rows: int, col: str) -> float:
    """
    Returns the Percent Change of a series divided by the std dev of a series
    """
    curr_returns = returns(df, num_rows, col)
    curr_std_dev = std_dev(df, num_rows, col)
    return curr_returns / curr_std_dev
