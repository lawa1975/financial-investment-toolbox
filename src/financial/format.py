from typing import Optional
from financial.model import Money

class MoneyFormatter:
    fixed_decimal_places: Optional[int]

    def __init__(self, fixed_decimal_places: Optional[int] = None) -> None:
        self.fixed_decimal_places = (
            None
            if fixed_decimal_places is None
            else abs(fixed_decimal_places)
        )

    def format(self, money: Money) -> str:
        currency = money.currency.value
        amount = (
            f"%.{self.fixed_decimal_places}f" % money.amount
            if self.fixed_decimal_places is not None
            else str(money.amount)
        )
        return f"{amount} {currency}"
