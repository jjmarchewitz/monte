"""DOC:"""

from datetime import timedelta

from alpaca_trade_api import TimeFrame, TimeFrameUnit

from monte import asset_manager, machine, util


def main():
    alpaca_api = util.AlpacaAPIBundle()

    machine_settings = machine.MachineSettings(
        start_date="2016-09-09",
        end_date="2016-10-04",
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
        derived_columns={},
        max_rows_in_df=500,
        start_buffer_size=timedelta(days=5),
        data_buffer_size=timedelta(weeks=200),
    )

    am = asset_manager.AssetManager(alpaca_api, machine_settings)

    # symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA", "UNH", "JNJ",
    #            "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG", "HD", "MA", "BAC", "ABBV",
    #            "PFE", "KO", "NVO", "PEP", "MRK", "BABA", "COST", "AVGO", "TM", "ASML", "DIS", "ABT",
    #            "ORCL", "TMUS", "MCD", "AZN", "CSCO", "VZ", "WFC", "CRM", "TXN", "UPS", "NKE", "ROK"]

    symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA"]

    for symbol in symbols:
        am.watch_asset(symbol)

    breakpoint()

    # bb = alpaca_api.market_data.get_bars(
    #     'AMZN', machine_settings.time_frame, machine_settings.start_date, machine_settings.end_date,
    #     adjustment='all')

    while True:
        # breakpoint()
        try:
            am.increment_dataframes()
        except StopIteration:
            break
        finally:
            print(f"{am['AAPL'].iloc[-1].timestamp} - ${round(am['AAPL'].iloc[-1].vwap, 2):.2f}")

    # am.watched_assets['AAPL'].increment_dataframe()

    breakpoint()


if __name__ == "__main__":
    main()
