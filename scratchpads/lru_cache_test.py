import time
from functools import cache

import numpy as np
import pandas as pd


@cache
def avg_last_n(df, n):
    total = 0

    for i in range(1, n + 1):
        total += df.iloc[-i].vwap

    avg = total / n

    time.sleep(2)

    return avg


def main():
    new_df = pd.DataFrame(np.random.randint(0, 100, size=(100, 1)), columns=['vwap'])

    breakpoint()


if __name__ == "__main__":
    main()
