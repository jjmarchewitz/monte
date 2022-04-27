import yfinance as yf


def get_stock_data(ticker=None, period="max"):
    tick_obj = yf.Ticker(ticker)
    data = tick_obj.history(period=period)
    return data
