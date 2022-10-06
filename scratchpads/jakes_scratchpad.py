from alpaca_trade_api import TimeFrame
from datetime import timedelta
from algorithms import test
from monte import asset_manager, machine, util


def main():
    alpaca_api = util.AlpacaAPIBundle()

    derived_columns = {}

    machine_settings = machine.MachineSettings(
        start_date="2021-09-09",
        end_date="2021-10-20",
        time_frame=TimeFrame.Hour,
        derived_columns=derived_columns,
        max_rows_in_df=10_000,
        start_buffer_time_delta=timedelta(days=5),
    )

    am = asset_manager.AssetManager(alpaca_api, machine_settings)

    symbols = ["AAPL", "GOOG", "IVV", "AMD", "NVDA", "INTC", "QQQ", "DIA", "AMZN", "TSLA",
               "UNH", "JNJ", "XOM", "V", "TSM", "META", "WMT", "JPM", "LLY", "SUN", "CVX", "PG"]

    breakpoint()


if __name__ == "__main__":
    main()
