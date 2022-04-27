import yfinance as yf


def get_stock_data(ticker=None, period_arg="max"):
    tick_obj = yf.Ticker(ticker)
    data = tick_obj.history(period=period_arg)
    return data


spx = yf.Ticker("SPX")
msft = yf.Ticker("MSFT")

# get stock info
# print(spx.info)

# get historical market data
# hist1 = spx.history(period="max")
hist2 = msft.history(period="max")


test = msft.recommendations
# print(analyst)

# Plotting Mine Vs Actual
# percent_test = .3
# num_days_test = int(percent_test*len(hist2))
# x_vals = [i for i in range(1, num_days_test + 1)]
# y_actual = 1000*hist2.iloc[0:num_days_test, 1]

# # AlGORITHM
# y_algo = [1000 for i in range(1, num_days_test + 1)]
# # Plotting
# plt.plot(x_vals, y_actual)
# plt.plot(x_vals, y_algo)
# plt.show()
