from __future__ import annotations

from datetime import datetime

from monte.broker import Broker


def print_total_value(name: str, broker: Broker, current_datetime: datetime):
    print(
        f"{current_datetime.date()} {current_datetime.hour:02d}:{current_datetime.minute:02d} | "
        f"{name} | "
        f"${round(broker.portfolio.total_value, 2):,.2f} | "
        f"{round(broker.portfolio.current_return, 3):+.3f}%")
