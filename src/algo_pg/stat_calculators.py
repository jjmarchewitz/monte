"""
Functions that will generate summary statistics for a DataManager instance.

These functions MUST NOT rely on any columns that are not present by default
(i.e. other custom stats columns). This is a feature that may be supported in the
future.

"""


def dummy_420_69(df, last_row_index):
    """
    lol.

    Args:
        df: A dataframe of raw input data, almost straight from Alpaca.
        last_row_index: The index of the last valid row in the provided dataframe.

    Returns:
        -420.69
    """
    return -420.69


def avg_last_5(df, last_row_index):
    """
    Computes the average volume-weighted average price over the last 5 TimeFrames.

    Args:
        df: A dataframe of raw input data, almost straight from Alpaca.
        last_row_index: The index of the last valid row in the provided dataframe.

    Returns:
        The average volume-weighted average price over the last 5 TimeFrames.
    """

    total = 0

    for _, row in df.loc[last_row_index - 4:last_row_index].iterrows():
        total += row.vwap

    avg = total / 5

    return avg
