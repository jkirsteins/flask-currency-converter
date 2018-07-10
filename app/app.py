# -*- coding: utf-8 -*-

import json
import logging

from flask import Flask
from flask import request
from flask import jsonify
from flask_injector import FlaskInjector

from .data_querier import DataQuerier

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
            scope=request
        )

    return [configure_logger, configure_data_querier]

def create_app(additional_modules=None):
    """Initializes the Flask app."""
    app = Flask(__name__)
    app.config.from_object('app.config')

    @app.route('/api/v1/country/<country_code>/currency')
    def api_v1_currencies_for_country(country_code, data_querier: DataQuerier):
        #pylint: disable=unused-variable
        """API v1 method for returning the 3-char currency codes associated with a given 2 char territory code."""
        return jsonify(data_querier.get_currencies(country_code))

    @app.route('/api/v1/currency/<currency_code>/country')
    def api_v1_countries_for_currency(currency_code, data_querier: DataQuerier):
        #pylint: disable=unused-variable
        """API v1 method for returning the 2-char territory codes that use a given currency (identified by a 3 char code)."""
        return jsonify(data_querier.get_countries(currency_code))

    injector_modules = create_injector_modules(app.logger, app.config.get("COUNTRY_DATA"))
    if isinstance(additional_modules, list):
        injector_modules = injector_modules + additional_modules

    FlaskInjector(app=app, modules=injector_modules)

    return app
