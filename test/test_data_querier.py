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

def test_getCountriesForINR_returnsBoth(data_querier):
    """Tests that a valid notification is given to the dispatcher for processing."""
    currencies = data_querier.get_countries("INR")
    assert ["BT", "FK"] == currencies

