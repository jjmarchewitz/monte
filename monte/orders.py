from dataclasses import dataclass
from enum import Enum, auto


class OrderType(Enum):
    """
    An Enum holding a value for an order either being a buy or a sell order.
    """
    BUY = auto()
    SELL = auto()


class OrderStatus(Enum):
    """
    An Enum holding a value for the status of an order (pending, completed, failed).
    """
    PENDING = auto()
    COMPLETED = auto()
    FAILED = auto()
    CANCELLED = auto()


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
