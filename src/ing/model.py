from enum import Enum
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Optional
from financial.model import Money


class TransactionTypeEnum(str, Enum):
    BUY = "BUY"
    SELL = "SELL"


class PaymentDirectionEnum(str, Enum):
    AT_YOUR_EXPENSE = "AT_YOUR_EXPENSE" # german: zu Ihren Lasten
    IN_YOUR_FAVOR = "IN_YOUR_FAVOR" # german: zu Ihren Gunsten


@dataclass
class SecuritiesSettlement:
    transaction_type: TransactionTypeEnum
    execution_time: datetime
    isin: str # International Securities Identification Number
    wkn: str # Wertpapierkennnummer
    shares: Decimal # Nominale
    price_per_share: Money # Kurs
    market_value: Money # Kurswert
    provision: Optional[Money]
    payment_direction: PaymentDirectionEnum
    final_amount: Money
