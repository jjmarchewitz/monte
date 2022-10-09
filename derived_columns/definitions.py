import pandas as pd

from derived_columns.decorator import DFIdentifier, derived_column


@derived_column
def net_vwap_last_n(ident: DFIdentifier, df: pd.DataFrame, n: int) -> float:
    """DOC:"""
    print("AAAAAA")
    return df.iloc[-n - 1].vwap - df.iloc[-1].vwap


@derived_column
def avg_vwap_last_n(ident: DFIdentifier, df: pd.DataFrame, n: int) -> float:
    """DOC:"""
    total = 0

    print("BBBBBB")

    for i in range(1, n + 1):
        total += df.iloc[-i].vwap

    avg = total / n

    return avg
