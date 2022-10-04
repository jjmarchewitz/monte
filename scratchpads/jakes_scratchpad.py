from alpaca_trade_api import TimeFrame
from datetime import timedelta
from monte import machine, util


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

    breakpoint()


if __name__ == "__main__":
    main()
