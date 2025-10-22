from dataclasses import dataclass


@dataclass
class SecuritiesSettlementModel:
    kauf_verkauf: str
    isin: str
    wkn: str
    nominale: str
    kurs: str
    kurswert: str
    ausfuehrzeit: str
    provision: str
    endbetrag_lasten: str
    endbetrag_gunsten: str
