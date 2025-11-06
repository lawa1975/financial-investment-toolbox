from typing import Optional
from ing.model import Money

class MoneyFormatter:
    decimal_places: Optional[int]

    def __init__(self, decimal_places: Optional[int] = None) -> None:
        self.decimal_places = None if decimal_places is None else abs(decimal_places)

    def format(self, money: Money) -> str:
        currency = money.currency.value
        amount = (
            f"%.{self.decimal_places}f" % money.amount
            if self.decimal_places is not None
            else str(money.amount)
        )
        return f"{amount} {currency}"
