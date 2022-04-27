import yfinance as yf


def get_stock_data(ticker=None, period="max"):
    tick_obj = yf.Ticker(ticker)
    data = tick_obj.history(period=period)
    return data


spx = yf.Ticker("SPX")
msft = yf.Ticker("MSFT")

# get stock info
# print(spx.info)

# get historical market data
# hist1 = spx.history(period="max")
hist2 = msft.history(period="max")

# # show actions (dividends, splits)
# msft.actions

# # show dividends
# msft.dividends

# # show splits
# msft.splits

# # show financials
# msft.financials
# msft.quarterly_financials

# # show major holders
# msft.major_holders

# # show institutional holders
# msft.institutional_holders

# # show balance sheet
# msft.balance_sheet
# msft.quarterly_balance_sheet

# # show cashflow
# msft.cashflow
# msft.quarterly_cashflow

# # show earnings
# msft.earnings
# msft.quarterly_earnings

# # show sustainability
# msft.sustainability

# # show analysts recommendations
# msft.recommendations

# # show next event (earnings, etc)
# msft.calendar

# # show ISIN code - *experimental*
# # ISIN = International Securities Identification Number
# msft.isin

# # show options expirations
# msft.options

# # show news
# msft.news

# # get option chain for specific expiration
# opt = msft.option_chain('YYYY-MM-DD')
# # data available via: opt.calls, opt.puts

# So Now I have the High and Low and can build and test basic algorithm


# Loading The Analyst Data
# analyst = spx.recommendations
test = msft.recommendations
# print(analyst)

# Plotting Mine Vs Actual
percent_test = .3
num_days_test = int(percent_test*len(hist2))
x_vals = [i for i in range(1, num_days_test + 1)]
y_actual = 1000*hist2.iloc[0:num_days_test, 1]

# AlGORITHM
y_algo = [1000 for i in range(1, num_days_test + 1)]
# Plotting
plt.plot(x_vals, y_actual)
plt.plot(x_vals, y_algo)
plt.show()
