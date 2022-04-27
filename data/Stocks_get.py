import yfinance as yf


def get_stock_data(ticker=None, period_arg="max"):
    tick_obj = yf.Ticker(ticker)
    data = tick_obj.history(period=period_arg)
    return data
