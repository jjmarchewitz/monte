def avg_last_n(df, n):
    total = 0

    for i in range(1, n + 1):
        total += df.iloc[-i].vwap

    avg = total / n

    return avg
