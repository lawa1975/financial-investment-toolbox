import pymupdf

from datetime import datetime
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Optional

from financial.model import CurrencyEnum, Money
from ing.model import (
    SecuritiesSettlement,
    TransactionTypeEnum,
    PaymentDirectionEnum,
)
from ing.constants import SecuritySettlementConstants


class SecuritySettlementExtractor:
    """Extracts data from ING security settlement document."""
    
    def __init__(self, text_lines: list[str]) -> None:
        self.__constants = SecuritySettlementConstants()
        self.__text_lines = text_lines

    @staticmethod
    def __convert_to_decimal(input: str) -> Decimal:
        return Decimal(input.replace(".", "").replace(",", "."))         
    
    @staticmethod
    def __convert_to_currency(input: str) -> CurrencyEnum:
        if input.upper() == "EUR":
            return CurrencyEnum.EUR
        elif input.upper() == "USD":
            return CurrencyEnum.USD
        else:
            raise ValueError("unknown currency")
        
    @staticmethod
    def __convert_to_money(input_amount: str, input_currency: str) -> Money:
        amount = SecuritySettlementExtractor.__convert_to_decimal(input_amount)
        currency = SecuritySettlementExtractor.__convert_to_currency(input_currency)
        return Money(amount, currency)

    def __extract_transaction_type(self) -> TransactionTypeEnum:
        idx = self.__text_lines.index(self.__constants.SECURITY_SETTLEMENT_LABEL)        
        str = self.__text_lines[idx + 1].lower()
        if str.startswith("kauf"):
            return TransactionTypeEnum.BUY
        elif str.startswith("verkauf"):
            return TransactionTypeEnum.SELL
        else:
            raise ValueError("unknown transaction type")
    
    def __extract_isin_wkn(self) -> tuple[str, str]:
        idx = self.__text_lines.index(self.__constants.ISIN_WKN_LABEL)
        str = self.__text_lines[idx + 1]
        isin, wkn = str.replace("(", "").replace(")", "").split(" ")
        return (isin, wkn)
    
    def __extract_shares(self) -> Decimal:
        idx = self.__text_lines.index(self.__constants.SHARES_LABEL)
        return SecuritySettlementExtractor.__convert_to_decimal(
            self.__text_lines[idx + 2]
        )

    def __extract_price_per_share(self) -> Money:
        idx = self.__text_lines.index(self.__constants.PRICE_PER_SHARE_LABEL)
        return SecuritySettlementExtractor.__convert_to_money(
            self.__text_lines[idx + 2],
            self.__text_lines[idx + 1]
        )
    
    def __extract_market_value(self) -> Money:
        idx = self.__text_lines.index(self.__constants.MARKET_VALUE_LABEL)
        return SecuritySettlementExtractor.__convert_to_money(
            self.__text_lines[idx + 2],
            self.__text_lines[idx + 1]
        )
    
    def __extract_provision(self) -> Optional[Money]:
        try:
            idx = self.__text_lines.index(self.__constants.PROVISION_LABEL)
        except ValueError:
            return None
        
        return SecuritySettlementExtractor.__convert_to_money(
            self.__text_lines[idx + 2],
            self.__text_lines[idx + 1]
        )

    def __extract_execution_time(self) -> datetime:
        idx = self.__text_lines.index(self.__constants.EXECUTION_TIME_LABEL)
        str = self.__text_lines[idx + 1]
        iso = f"{str[6:10]}-{str[3:5]}-{str[0:2]}T{str[14:16]}:{str[17:19]}:{str[20:22]}"
        return datetime.fromisoformat(iso)
    
    def __extract_final_amount(self) -> tuple[Money, PaymentDirectionEnum]:
        payment_direction = None

        for entry in [
            (self.__constants.FINAL_AMOUNT_EXPENSE_LABEL, PaymentDirectionEnum.AT_YOUR_EXPENSE),
            (self.__constants.FINAL_AMOUNT_FAVOR_LABEL, PaymentDirectionEnum.IN_YOUR_FAVOR)
        ]:
            try:
                idx = self.__text_lines.index(entry[0])
                payment_direction = entry[1]
                break
            except ValueError:
                pass

        if not payment_direction:
            raise ValueError("no payment direction for total amount")
        
        total_amount = SecuritySettlementExtractor.__convert_to_money(
            self.__text_lines[idx + 2],
            self.__text_lines[idx + 1]
        )

        return total_amount, payment_direction

    @staticmethod
    def create_from_pdf(filepath: Path) -> "SecuritySettlementExtractor":
        with pymupdf.open(filepath) as doc:
            raw_text = doc[0].get_text()
            text_lines = raw_text.split("\n")
            return SecuritySettlementExtractor(text_lines)

    def extract_to_model(self) -> SecuritiesSettlement:
        getcontext().prec = 8
        
        isin_val, wkn_val = self.__extract_isin_wkn()
        final_amount, payment_direction = self.__extract_final_amount()

        return SecuritiesSettlement(
            transaction_type=self.__extract_transaction_type(),
            execution_time=self.__extract_execution_time(),
            isin=isin_val,
            wkn=wkn_val,
            shares=self.__extract_shares(),
            price_per_share=self.__extract_price_per_share(),
            market_value=self.__extract_market_value(),
            provision=self.__extract_provision(),
            payment_direction=payment_direction,
            final_amount=final_amount
        )
