import pytest
import os
import json

from unittest.mock import patch, call, Mock

from app import app
from app.data_querier import DataQuerier
from app.currency_exchanger import (
    CurrencyExchanger, MissingCurrencyException, InMemoryCachedCurrencyExchangers, FloatRatesCurrencyDataSource
)

@pytest.fixture
def mock_data_querier():
    return Mock()

@pytest.fixture
def mock_currency_exchanger_source():
    return Mock()

@patch.dict(os.environ, {'SECRET_KEY':'test', 'COUNTRY_DATA_JSON':"unused"})
@patch('builtins.open')
@patch('json.load', return_value={})
@pytest.fixture
def client(mock_data_querier, mock_currency_exchanger_source):
    def bind_mocks(binder):
        binder.bind(InMemoryCachedCurrencyExchangers, to=mock_currency_exchanger_source)
        binder.bind(DataQuerier, to=mock_data_querier)

    test_app = app.create_app([bind_mocks])
    test_app.testing = True
    return test_app.test_client()

def test_getCurrencyForCountry_knownCountry_returns200(client, mock_data_querier):
    """Tests that when the call has data to return, the status is 200 and the
    response body is as-expected."""
    mock_data_querier.get_currencies.return_value=['GBP']

    rv = client.get("/api/v1/country/GB/currency")

    assert rv.status_code == 200
    assert rv.get_data(as_text=True) == "....."

