import pytest
import datetime
import json

from unittest import mock
from datetime import timedelta
from dateutil.tz import tzlocal
from app.data_querier import DataQuerier
from app.currency_exchanger import CurrencyExchanger, MissingCurrencyException

class MockDataSource(object):
    def __init__(self, target_code, valid_from, valid_to):
        self.valid_from = valid_from
        self.valid_to = valid_to
        self.target_code = target_code

    def download_rates(self, currency_code):
        return {
            "valid_from": self.valid_from,
            "valid_to": self.valid_to,
            "currency_code": currency_code,
            "entries": {
                self.target_code: {
                    "currency_code": self.target_code,
                    "rate": 2
                }
            }
        }

@pytest.fixture
def data_querier(mock_data):
    return DataQuerier(mock_data)

@pytest.fixture
def past_time(): return datetime.datetime.now(tzlocal()) - timedelta(hours=1)

@pytest.fixture
def future_time(): return datetime.datetime.now(tzlocal()) + timedelta(hours=1)

def test_convertToSelf_rateDoesNotIncludeSelf_exchangerReturnSameValue(past_time, future_time):
    """Tests that converting a currency to itself yields the same value."""
    data_source = MockDataSource("eur", past_time, future_time)
    exchanger = CurrencyExchanger("usd", data_source.download_rates("usd"))
    amount = exchanger.convert_amount_to(5, "usd")
    assert 5 == amount

def test_convertToMissingCurrency_raisesMissingCurrencyException(past_time, future_time):
    """Tests that converting a currency to itself yields the same value."""
    data_source = MockDataSource("eur", past_time, future_time)
    exchanger = CurrencyExchanger("usd", data_source.download_rates("usd"))

    with pytest.raises(MissingCurrencyException):
        exchanger.convert_amount_to(5, "mbr")

def test_convertToValidCurrency_returnsCorrectAmount(past_time, future_time):
    """Tests that converting a currency to itself yields the same value."""
    data_source = MockDataSource("eur", past_time, future_time)
    exchanger = CurrencyExchanger("usd", data_source.download_rates("usd"))

    converted_amount = exchanger.convert_amount_to(5, "eur")

    assert 10 == converted_amount

