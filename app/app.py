# -*- coding: utf-8 -*-

import json
import logging

from flask import Flask
from flask import request
from flask import jsonify
from flask_injector import FlaskInjector
from flask_injector import singleton

from .data_querier import DataQuerier
from .currency_exchanger import CurrencyExchanger
from .currency_exchanger import MissingCurrencyException
from .currency_exchanger import InMemoryCachedCurrencyExchangers
from .currency_exchanger import FloatRatesCurrencyDataSource

def create_injector_modules(logger, country_data_object):
    """Generate modules for the 'injector' dependency injection.

    In this example, it only injects the logger dependency.

    When running tests, they can generate their own modules, and append to these (to
    overwrite some dependencies with different ones that are tailored for testing).
    """
    def configure_logger(binder):
        """Binds a specific logger implementation to logging.Logger dependencies."""
        binder.bind(
            logging.Logger,
            to=logger,
            scope=request
        )

    def configure_data_querier(binder):
        data_querier = DataQuerier(country_data_object)
        binder.bind(
            DataQuerier,
            to=data_querier,
            scope=singleton
        )

    def configure_currency_exchanger(binder):
        data_source = FloatRatesCurrencyDataSource()
        exchanger_cache = InMemoryCachedCurrencyExchangers(data_source)

        binder.bind(
            InMemoryCachedCurrencyExchangers,
            to=exchanger_cache,
            scope=singleton
        )

    return [configure_logger, configure_data_querier, configure_currency_exchanger]

def create_app(additional_modules=None):
    """Initializes the Flask app."""
    app = Flask(__name__)
    app.config.from_object('app.config')

    @app.errorhandler(MissingCurrencyException)
    def handle_invalid_usage(error):
        response = jsonify(error.to_dict())
        response.status_code = error.http_status()
        return response

    @app.route('/api/v1/country/<country_code>/currency')
    def api_v1_currencies_for_country(country_code, data_querier: DataQuerier):
        """API v1 method for returning the 3-char currency codes associated with a given 2 char territory code."""
        return jsonify(data_querier.get_currencies(country_code))

    @app.route('/api/v1/currency/<base_currency_code>/amount/<int:base_amount>')
    def api_v1_currency_amount(base_currency_code, base_amount, currency_exchanger_source: InMemoryCachedCurrencyExchangers):
        """API v1 method for returning the 3-char currency codes associated with a given 2 char territory code."""
        requested_display_currency_code = request.args.get('display_currency_code')

        exchanger = currency_exchanger_source.get_exchanger_for_currency(base_currency_code)

        display_currency_code = requested_display_currency_code if requested_display_currency_code else base_currency_code
        display_amount = exchanger.convert_amount_to(
            amount_in_base_currency=base_amount,
            target_currency_code=display_currency_code)

        valid_for = int(exchanger.remaining_validity_period_in_seconds())

        resp = jsonify({
            "valid_for": valid_for,
            "base_currency_code": base_currency_code,
            "display_currency_code": display_currency_code,
            "base_amount": base_amount,
            "display_amount": display_amount
        })
        resp.cache_control.max_age = valid_for

        return resp

    @app.route('/api/v1/currency/<currency_code>/country')
    def api_v1_countries_for_currency(currency_code, data_querier: DataQuerier):
        """API v1 method for returning the 2-char territory codes that use a given currency (identified by a 3 char code)."""
        return jsonify(data_querier.get_countries(currency_code))

    injector_modules = create_injector_modules(app.logger, app.config.get("COUNTRY_DATA"))
    if isinstance(additional_modules, list):
        injector_modules = injector_modules + additional_modules

    FlaskInjector(app=app, modules=injector_modules)

    return app
