import pytest

from financial.format import MoneyFormatter
from financial.model import CurrencyEnum, Money 


class TestMoneyFormatter:
    
    @pytest.mark.parametrize(
        "money, expected",
        [
            (Money(1.52, CurrencyEnum.EUR), "1.52 EUR"),
            (Money(1.52, CurrencyEnum.USD), "1.52 USD"),            
            (Money(-1.52, CurrencyEnum.EUR), "-1.52 EUR"),
            (Money(9999.999999, CurrencyEnum.EUR), "9999.999999 EUR"),
        ]            
    )
    def test_format(self, money, expected):
        assert MoneyFormatter().format(money) == expected

    @pytest.mark.parametrize(
        "money, fixed_decimal_places, expected",
        [
            (Money(1.52, CurrencyEnum.EUR), 2, "1.52 EUR"),
            (Money(1.52, CurrencyEnum.EUR), 0, "2 EUR"),
            (Money(1.52, CurrencyEnum.EUR), 4, "1.5200 EUR"),
            (Money(1.52, CurrencyEnum.EUR), -4, "1.5200 EUR"),              
            (Money(-1.52, CurrencyEnum.EUR), 4, "-1.5200 EUR"),
            (Money(9999.999999, CurrencyEnum.EUR), 5, "10000.00000 EUR"),
            (Money(9999.999999, CurrencyEnum.EUR), 6, "9999.999999 EUR"),
        ]        
    )
    def test_format_with_fixed_decimal_places(self, money, fixed_decimal_places, expected):
        assert MoneyFormatter(fixed_decimal_places).format(money) == expected

