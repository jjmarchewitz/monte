from dataclasses import dataclass
from enum import Enum


class OrderType(Enum):
    """
    An Enum holding a value for an order either being a buy or a sell order.
    """
    BUY = 1
    SELL = 2


class OrderStatus(Enum):
    """
    An Enum holding a value for the status of an order (pending, completed, failed).
    """
    PENDING = 1
    COMPLETED = 2
    FAILED = 3
    CANCELLED = 4


@dataclass
class Order():
    """
    A dataclass that represents a market order.
    """
    id_number: int
    symbol: str
    quantity: float
    order_type: OrderType
    status: OrderStatus
