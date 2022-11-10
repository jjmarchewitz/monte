from typing import Union

from monte.asset_manager import AssetManager, CommonAssetData
from monte.machine_settings import MachineSettings
from monte.orders import Order, OrderStatus, OrderType
from monte.portfolio import Portfolio


class Asset():

    am: AssetManager

    def __init__(self, asset_manager: AssetManager, symbol: str) -> None:
        self.am = asset_manager


class Broker():

    am: AssetManager
    machine_settings: MachineSettings
    portfolio: Portfolio
    _order_queue: list[Order]
    _current_order_id_number: int

    def __init__(self, machine_settings: MachineSettings, starting_cash: float = 10_000) -> None:
        self.machine_settings = machine_settings
        self.portfolio = Portfolio(machine_settings, starting_cash)
        self.watched_assets = {}
        self._order_queue = []
        self._current_order_id_number = 0

    def set_asset_manager(self, asset_manager: AssetManager) -> None:
        """
        DOC:
        """
        if not isinstance(asset_manager, AssetManager):
            raise TypeError("Must pass an instance of AssetManager into set_asset_manager()")

        self.am = asset_manager

    def watch(self, symbol) -> None:
        """
        DOC:
        """
        ...

    def is_watching(self, symbol) -> bool:
        """
        DOC:
        """
        ...

    def unwatch(self, symbol) -> bool:
        """
        DOC:
        """
        ...

    def place_order(self, symbol: str, quantity: float, order_type: OrderType) -> Order:
        """
        DOC:
        """
        ...

    def get_order(self, order_id: int) -> Union[Order, None]:
        """
        DOC:
        """
        ...

    def cancel_order(self, order_id: int) -> tuple[bool, Union[Order, None]]:
        """
        DOC:
        """
        ...

    def process_pending_orders(self) -> list[Order]:
        """
        DOC:
        """
        ...

    def _execute_buy_order(self, order: Order) -> None:
        """
        DOC:
        """
        ...

    def _execute_sell_order(self, order: Order) -> None:
        """
        DOC:
        """
        ...
