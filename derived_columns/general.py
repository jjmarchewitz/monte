def avg_last_n(df, n):
    total = 0

    for i in range(1, n + 1):
        total += df.iloc[-i].vwap

    avg = total / n

    return avg


def returns(df, num_samples_difference=1, final_sample=-1):
    return (df.iloc[final_sample].vwap - df.iloc[final_sample-num_samples_difference]) / df.iloc[final_sample-num_samples_difference]


def volatility_returns(df, BUFFER_SIZE):
    # you need ravg and rt
    # NEED BUFFER SIZE
    # you'll somehow need to find the returns for all of the buffer first
    # you'll have just calculated rt so should be able to iloc into that column but confirm with Jake
    # Ask Jake where the df columns also populate. Like do I have to write extra code to enter the stat i calculated to df?
    # Ask Jake where is the best place constants per iteration?

    # I probably will need to compute r_avg here because it's a sliding window
    r_avg = 0
    for i in range(1, BUFFER_SIZE):
        df.iloc[i].returns = returns(df, 1, i)
        r_avg += df.iloc[i].returns
    r_avg = r_avg / (BUFFER_SIZE-2)
    return (df.iloc[-1].returns - r_avg)


def sharpe_ratio(df):
    return df.iloc[-1].returns / df.iloc[-1].volatility_returns
