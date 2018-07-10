import json
from urllib.request import urlopen

class CurrencyExchanger(object):
    """An in-memory currency exchanger that downloads data from http://www.floatrates.com/json-feeds.html.
    If no exchange rate information is found, it is downloaded and cached in-memory, and not re-downloaded.
    """

    URL_TEMPLATE = "http://www.floatrates.com/daily/%s.json"

    def __init__(self):
        self.cached_rates = {}

    def ensure_rates_available(self, currency_code):
        """Downloads JSON from floatrates.com (it expects lowercase currency codes)."""
        lowercase_code = currency_code.lower()

        if lowercase_code in self.cached_rates: return

        url = self.URL_TEMPLATE % lowercase_code
        raw_rate_json = urlopen(url).read().decode("utf-8")
        json_data = json.loads(raw_rate_json)

        self.cached_rates[lowercase_code] = json_data

    def convert(self, from_currency, to_currency, amount):
        """Converts the given amount from from_currency to to_currency, and returns the result."""
        lowercase_base_code = from_currency.lower()
        lowercase_target_code = to_currency.lower()

        self.ensure_rates_available(lowercase_base_code)

        rate = self.cached_rates[lowercase_base_code][lowercase_target_code]["rate"]

        return amount * rate



