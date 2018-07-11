import functools

from flask import (
    Blueprint, flash, g, redirect, render_template, request, url_for
)
from urllib.error import HTTPError
from .data_querier import DataQuerier
from .currency_exchanger import (
    CurrencyExchanger, MissingCurrencyException, InMemoryCachedCurrencyExchangers, FloatRatesCurrencyDataSource
)

bp = Blueprint('ui', __name__, url_prefix='/ui')

@bp.route('/country_lookup', methods=('GET', 'POST'))
def country_lookup(data_querier: DataQuerier):
    """View for looking up countries that use a given currency."""

    base_currency_code = request.form.get('base_currency_code')
    found_countries = None

    if request.method == 'POST':
        found_countries = data_querier.get_countries(base_currency_code)

    return render_template('country_lookup.html',
        base_currency_code=base_currency_code,
        known_currencies=data_querier.get_known_currencies(),
        found_countries=found_countries)

@bp.route('/currency_lookup', methods=('GET', 'POST'))
def currency_lookup(data_querier: DataQuerier):
    """View for looking up currencies that are in use in a given country."""

    country_code = request.form.get('country_code')
    found_currencies = None

    if request.method == 'POST':
        found_currencies = data_querier.get_currencies(country_code)

    return render_template('currency_lookup.html',
        country_code=country_code,
        known_countries=data_querier.get_known_countries(),
        found_currencies=found_currencies)

@bp.route('/convert', methods=('GET', 'POST'))
def convert(currency_exchanger_source: InMemoryCachedCurrencyExchangers, data_querier: DataQuerier):
    """View for converting between currencies."""

    base_currency_code = request.form.get('base_currency_code')
    target_currency_code = request.form.get('target_currency_code')
    base_amount = request.form.get('base_amount')
    base_amount = int(base_amount) if base_amount else 0
    converted_amount = None

    if request.method == 'POST':
        try:
            exchanger = currency_exchanger_source.get_exchanger_for_currency(base_currency_code)
            converted_amount = exchanger.convert_amount_to(base_amount, target_currency_code)
        except MissingCurrencyException as error:
            flash("An invalid currency was specified: %s" % error)
        except HTTPError as error:
            flash("Sorry, we can not perform currency conversion at this time.")

    return render_template('convert.html',
        known_currencies=data_querier.get_known_currencies(),
        base_currency_code=base_currency_code,
        base_amount=base_amount,
        target_currency_code=target_currency_code,
        converted_amount=converted_amount)
