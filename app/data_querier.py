# -*- coding: utf-8 -*-
"""This module contains DataQuerier - a class for matching currencies with
their respective territories, and vice-versa."""

class DataQuerier(object):
    def __init__(self, data_object):
        self.data_object = data_object

    def get_currencies(self, country_code):
        for entry in self.data_object:
            if entry["iso3166_country_code"] == country_code:
                return entry["iso4217_currencies"].split(",")

    def get_countries(self, currency_code):
        results = []
        for entry in self.data_object:
            if entry["iso4217_currencies"] is not None and currency_code in entry["iso4217_currencies"]:
                results.append(entry["iso3166_country_code"])
        return results
