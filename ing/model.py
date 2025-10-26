from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal


class TransactionTypeEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class CurrencyEnum(str, Enum):
    EUR = "EUR"
    USD = "USD"


@dataclass
class Money:
    amount: Decimal
    currency: CurrencyEnum


@dataclass
class SecuritiesSettlement:
    transaction_type: TransactionTypeEnum
    execution_time: datetime
    isin: str # International Securities Identification Number
    wkn: str # Wertpapierkennnummer
    shares: str # Nominale
    price_per_share: Money # Kurs
    market_value: Money # Kurswert
    provision: Money
    final_amount: Money # negative: to be charged / positive: in favor of
