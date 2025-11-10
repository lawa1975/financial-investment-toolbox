from enum import Enum
from dataclasses import dataclass
from decimal import Decimal


class CurrencyEnum(str, Enum):
    EUR = "EUR"
    USD = "USD"


@dataclass
class Money:
    amount: Decimal
    currency: CurrencyEnum