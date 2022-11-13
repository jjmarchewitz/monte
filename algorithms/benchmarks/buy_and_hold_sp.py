from __future__ import annotations

from monte.machine_settings import MachineSettings

from .buy_and_hold import BuyAndHold


class BuyAndHoldSP500(BuyAndHold):

    def __init__(
            self, machine_settings: MachineSettings, name: str,
            starting_cash: float):

        # Create an instance of buy and hold with just SPY
        super().__init__(machine_settings, name, starting_cash, ["SPY"])
