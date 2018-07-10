# -*- coding: utf-8 -*-

import json
import logging

from flask import Flask
from flask import request
from flask_injector import FlaskInjector

def create_injector_modules(logger):
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

    return [configure_logger]

def create_app(additional_modules=None):
    """Initializes the Flask app."""
    app = Flask(__name__)
    app.config.from_object('app.config')

    @app.route('/')
    def empty_root():
        #pylint: disable=unused-variable
        """Empty root page (for submitting requests that Sqreen can intercept)."""
        return 'Hello World'

    injector_modules = create_injector_modules(app.logger)
    if isinstance(additional_modules, list):
        injector_modules = injector_modules + additional_modules

    FlaskInjector(app=app, modules=injector_modules)

    return app
