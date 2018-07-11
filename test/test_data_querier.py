import pytest
import json
from unittest import mock

from app.data_querier import DataQuerier

@pytest.fixture
def mock_data():
    return [{
        "iso4217_currencies": "INR,BTN",
        "iso3166_country_code": "BT",
        "territory_display_name": "Bhutan"
    },
    {
        "iso4217_currencies": None,
        "iso3166_country_code": None,
        "territory_display_name": "Antarctica"
    },
    {
        "iso4217_currencies": "INR",
        "iso3166_country_code": "FK",
        "territory_display_name": "Fake Country With INR"
    }]

@pytest.fixture
def data_querier(mock_data):
    return DataQuerier(mock_data)

def test_getCurrenciesForBT_returnBoth(data_querier):
    """Tests that a valid notification is given to the dispatcher for processing."""
    currencies = data_querier.get_currencies("BT")
    assert ["INR", "BTN"] == currencies

def test_getCurrenciesForNone_returnNone(data_querier):
    """Tests that if we pass in None for the country, we get back None. None is not the same as a missing value."""
    currencies = data_querier.get_currencies(None)
    assert None == currencies

def test_getCurrenciesForUnknown_returnNone(data_querier):
    """Tests that if we pass in an unknown country, we get back None."""
    currencies = data_querier.get_currencies("UNK")
    assert None == currencies

def test_getKnownCurrencies_returnsList_noDuplicates(data_querier):
    """Tests that all the known currencies are returned as a list, without duplicates."""
    currencies = data_querier.get_known_currencies()
    assert sorted(["INR", "BTN"]) == sorted(currencies)

def test_getKnownCountries_returnsList_noDuplicates(data_querier):
    """Tests that all the known countries are returned as a list, without duplicates."""
    countries = data_querier.get_known_countries()
    assert sorted(["BT", "FK"]) == sorted(countries)

def test_getCountriesForINR_returnsBoth(data_querier):
    """Tests that a valid notification is given to the dispatcher for processing."""
    currencies = data_querier.get_countries("INR")
    assert ["BT", "FK"] == currencies

