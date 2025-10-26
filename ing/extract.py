import pymupdf

from datetime import datetime
from decimal import Decimal, getcontext
from pathlib import Path
from typing import Optional

from ing.model import (
    SecuritiesSettlement,
    CurrencyEnum,
    TransactionTypeEnum,
    Money,
)
from ing.constants import SecuritySettlementConstants


class SecuritySettlementExtractor:
    
    def __init__(self, text_lines: list[str]) -> None:
        self.__constants = SecuritySettlementConstants()
        self.__text_lines = text_lines
    
    def __extract_isin_wkn(self) -> tuple[str, str]:
        idx = self.__text_lines.index(self.__constants.ISIN_WKN_LABEL)
        str = self.__text_lines[idx + 1]
        isin, wkn = str.replace("(", "").replace(")", "").split(" ")
        return (isin, wkn)
    
    def __extract_shares(self) -> str:
        idx = self.__text_lines.index(self.__constants.SHARES_LABEL)
        str = self.__text_lines[idx + 2]
        return Decimal(str.replace(",", "."))      

    @staticmethod
    def create_from_pdf(filepath: Path) -> "SecuritySettlementExtractor":
        with pymupdf.open(filepath) as doc:
            raw_text = doc[0].get_text()
            text_lines = raw_text.split("\n")
            return SecuritySettlementExtractor(text_lines)

    def extract_to_model(self) -> SecuritiesSettlement:
        getcontext().prec = 8

        isin_val, wkn_val = self.__extract_isin_wkn()

        return SecuritiesSettlement(
            transaction_type=TransactionTypeEnum.BUY,
            execution_time=datetime.now(),
            isin=isin_val,
            wkn=wkn_val,
            shares=self.__extract_shares(),
            price_per_share=Money(Decimal(0), CurrencyEnum.EUR),
            market_value=Money(Decimal(0), CurrencyEnum.EUR),
            provision=Money(Decimal(0), CurrencyEnum.EUR),
            final_amount=Money(Decimal(0), CurrencyEnum.EUR)
        )

    def extract(self) -> dict[str, Optional[str]]:
        result: dict[str, Optional[str]] = {}

        arr = self.__text_lines
        
        kauf_verkauf_label = "Wertpapierabrechnung"
        kauf_verkauf_index = arr.index(kauf_verkauf_label)
        result["kauf_verkauf"] = arr[kauf_verkauf_index + 1] 

        isin_wkn_label = "ISIN (WKN)"
        isin_wkn_index = arr.index(isin_wkn_label)
        isin_wkn_value = arr[isin_wkn_index + 1]
        result["isin"], result["wkn"] = isin_wkn_value.replace("(", "").replace(")", "").split(" ")

        nominale_label = "Nominale"
        nominale_index = arr.index(nominale_label)
        result["nominale"] = arr[nominale_index + 2]

        kurs_label = "Kurs"
        kurs_index = arr.index(kurs_label)
        result["kurs_waehrung"] = arr[kurs_index + 1]
        result["kurs"] = arr[kurs_index + 2]
        
        kurswert_label = "Kurswert"
        kurswert_index = arr.index(kurswert_label)
        result["kurswert_waehrung"] = arr[kurswert_index + 1]
        result["kurswert"] = arr[kurswert_index + 2]        

        ausfuehrzeit_label = "Ausführungstag / -zeit"
        ausfuehrzeit_index = arr.index(ausfuehrzeit_label)
        result["ausfuehrzeit"] = arr[ausfuehrzeit_index + 1]
        
        provision_label = "Provision"
        try:
            provision_index = arr.index(provision_label)
            provision_waehrung_value = arr[provision_index + 1]
            provision_value = arr[provision_index + 2]
        except ValueError:
            provision_waehrung_value = None
            provision_value = None
        result["provision_waehrung"] = provision_waehrung_value
        result["provision"] = provision_value

        endbetrag_label = "Endbetrag zu Ihren Lasten"
        try:
            endbetrag_index = arr.index(endbetrag_label)
            endbetrag_waehrung_value = arr[endbetrag_index + 1]
            endbetrag_value = arr[endbetrag_index + 2]
        except ValueError:
            endbetrag_waehrung_value = None
            endbetrag_value = None
        result["endbetrag_lasten_waehrung"] = endbetrag_waehrung_value
        result["endbetrag_lasten"] = endbetrag_value

        endbetrag_label = "Endbetrag zu Ihren Gunsten"
        try:
            endbetrag_index = arr.index(endbetrag_label)
            endbetrag_waehrung_value = arr[endbetrag_index + 1]
            endbetrag_value = arr[endbetrag_index + 2]
        except ValueError:
            endbetrag_waehrung_value = None
            endbetrag_value = None
        result["endbetrag_gunsten_waehrung"] = endbetrag_waehrung_value
        result["endbetrag_gunsten"] = endbetrag_value

        return result
