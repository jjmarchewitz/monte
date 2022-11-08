def print_total_value(portfolio, current_datetime):
    print(
        f"{current_datetime.date()} {current_datetime.hour:02d}:{current_datetime.minute:02d} | "
        f"${round(portfolio.total_value, 2):,.2f} | "
        f"{round(portfolio.current_return, 3):+.3f}%")
