"""DOC:"""

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from monte import asset_manager, machine, util


def main():
    alpaca_api = util.AlpacaAPIBundle()

    machine_settings = machine.MachineSettings(
        start_date="2016-09-09",
        end_date="2022-10-04",
        time_frame=TimeFrame(1, TimeFrameUnit.Minute),
        derived_columns={},
        max_rows_in_df=500,
        start_buffer_days=5,  # TradingDays
        data_buffer_days=10,  # TradingDays
    )

    am = asset_manager.AssetManager(alpaca_api, machine_settings)

    symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
               "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC", "ABBV",
               "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS", "ABT",
               "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE", "ROK"]

    # symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA"]

    # symbols = ["AAPL"]

    for symbol in symbols:
        am.watch_asset(symbol)

    breakpoint()

    count = 0

    while True:

        # if count < len(symbols):
        #     am.watch_asset(symbols[count])

        try:
            am.increment_dataframes()
        except StopIteration:
            break
        finally:
            print(f"{am['AAPL'].iloc[-1].timestamp} - ${round(am['AAPL'].iloc[-1].vwap, 2):.2f}")

        count += 1

    breakpoint()


if __name__ == "__main__":
    main()
