"""DOC:"""

from __future__ import annotations

from alpaca_trade_api import TimeFrame, TimeFrameUnit

import monte.asset_manager as asset_manager
import monte.machine as machine
import monte.machine_settings as machine_settings
import monte.util as util
from algorithms import test


def main():
    alpaca_api = util.AlpacaAPIBundle()

    # TODO: Create pre-defined "configs" for the most commonly used TimeFrames that auto-sets the TimeFrame
    # and data_buffer_days.
    # TODO: Add logging

    ms = machine_settings.MachineSettings(
        start_date="2016-09-09",
        end_date="2022-10-04",
        time_frame=TimeFrame(1, TimeFrameUnit.Hour),
        derived_columns={},
        max_rows_in_df=500,
        start_buffer_days=5,  # TradingDays
        data_buffer_days=500,  # TradingDays
    )

    trading_machine = machine.TradingMachine(alpaca_api, ms)

    algo1 = test.TestAlg(alpaca_api, ms)

    trading_machine.add_algo_instance(algo1)

    breakpoint()

    trading_machine.run()

    breakpoint()


if __name__ == "__main__":
    main()
