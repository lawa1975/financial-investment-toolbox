from decimal import Decimal
from financial.model import CurrencyEnum
from ing.extract import (
  PaymentDirectionEnum,
  SecuritySettlementExtractor,
  TransactionTypeEnum
)


SECURITY_SETTLEMENT_LINES_EXAMPLE = [
    'Wertpapierabrechnung', 'Verkauf',
    'Ordernummer', '424567111.001',
    'ISIN (WKN)', 'IE000MJIXFE0 (ETF133)',
    'Wertpapierbezeichnung', 'Am.ETF-MSCI NA ESG BR.TR.U.ETF', 'Bear.Shs EUR Dis. oN',
    'Nominale', 'Stück', '13,75',
    'Kurs', 'EUR', '126,32',
    'Handelsplatz', 'Direkthandel',
    'Ausführungstag / -zeit', '26.10.2025 um 11:38:29 Uhr',
    'Kurswert', 'EUR', '1.736,90',
    'Provision', 'EUR', '9,25',
    'Endbetrag zu Ihren Gunsten', 'EUR', '1.727,65',
    'Abrechnungs-IBAN', 'DE06 5006 0400 0020 1407 18',
    'Valuta', '27.10.2025',
    'Wertpapiere zulasten Wertpapierrechnung Großbritannien.',
    'Diese Order wurde mit folgendem Limit / -typ erteilt: 126,28 EUR',
    'Auftraggeber war Max Mustermann.', 'Jahressteuerbescheinigung folgt.',
    'Weiter geht es auf Seite 2.',
    'Depotinhaber:', 'Marco Manuel Mustermann',
    'Direkt-Depot Nr.:', '8011452244',
    'Datum:', '26.10.2025',
    'Seite:', '1 von 2',
    'Herrn', 'Marco Manuel Mustermann', 'z. Hd. Fam. Mustermann', 'Hufenkamp 211', '24119 Kronshagen',
    '34WAAD8013552022_T',
    'ING-DiBa AG · 60628 Frankfurt am Main',
    'ING-DiBa AG · Theodor-Heuss-Allee 2 · 60486 Frankfurt am Main · Vorsitzende des Aufsichtsrates: Susanne Klöß-Braekler · Vorstand: Lars Stoy (Vorsitzender),',
    'Michael Clijdesdale, Eddy Henning, Nikolaus Maximilian Linaric, Dr. Ralph Müller, Nurten Spitzer-Erdogan · Sitz: Frankfurt am Main · AG Frankfurt am Main · HRB 7727',
    'Steuernummer: 014 220 2800 4 · USt-IdNr.: DE 114 103 475 · Internet: www.ing.de · BIC: INGDDEFFXXX · Mitglied im Einlagensicherungsfonds', ''
]


class TestSecuritySettlementExtractor:

    def test_extract(self):
        model = SecuritySettlementExtractor(SECURITY_SETTLEMENT_LINES_EXAMPLE).extract_to_model()

        assert model is not None
        assert model.transaction_type == TransactionTypeEnum.SELL
        assert model.execution_time.isoformat() == "2025-10-26T11:38:29"
        assert model.isin == 'IE000MJIXFE0'
        assert model.wkn == 'ETF133'
        assert model.shares == Decimal("13.75")
        assert model.price_per_share.amount == Decimal("126.32")
        assert model.price_per_share.currency == CurrencyEnum.EUR
        assert model.market_value.amount == Decimal("1736.9")
        assert model.market_value.currency == CurrencyEnum.EUR
        assert model.provision.amount == Decimal("9.25")
        assert model.provision.currency == CurrencyEnum.EUR
        assert model.payment_direction == PaymentDirectionEnum.IN_YOUR_FAVOR
        assert model.final_amount.amount == Decimal("1727.65")
        assert model.final_amount.currency == CurrencyEnum.EUR
  