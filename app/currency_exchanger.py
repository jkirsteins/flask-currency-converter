import json
import datetime

from datetime import timedelta
from dateutil.tz import tzlocal
from dateutil.parser import parse
from urllib.request import urlopen

class MissingCurrencyException(Exception):
    def __init__(self, currency_code):
        self.currency_code = currency_code

    def http_status(self): return 400

    def to_dict(self):
        return {
            "message": "Unrecognized currency: %s" % self.currency_code,
            "status": self.http_status()
        }

class FloatRatesCurrencyDataSource(object):
    """Fetches currency data from floatrates.com.

    Returns all available rate information for a given source currency."""

    URL_TEMPLATE = "http://www.floatrates.com/daily/%s.json"

    def download_rates(self, currency_code):
        """Download rate information. Returns an object with 'valid_from'/'valid_to' datetime keys, 'currency_code' and 'rates' keys.
        Rates are a dict where target currency codes are (lowercase) keys and the values are an object with 'valid_from'/'valid_to' and 'rate' keys.
        The final 'rate' key is a number that you can use to multiply with the root currency code to get the converted value."""
        lowercase_code = currency_code.lower()
        url = self.URL_TEMPLATE % lowercase_code

        raw_rate_json = urlopen(url).read().decode("utf-8")

        unprocessed_rates = json.loads(raw_rate_json)
        processed_rates = {}

        bundle_valid_from = None
        bundle_valid_to = None

        for entry_key in unprocessed_rates:
            entry = unprocessed_rates[entry_key]

            valid_from = parse(entry["date"])
            valid_to = valid_from + timedelta(hours=12)

            # floatrates.com claims the whole bundle is valid in 12-hour chunks,
            # even though the data supports more granular (per-currency) validity periods
            if bundle_valid_from is None:
                bundle_valid_from = valid_from
                bundle_valid_to = valid_to

            rate = entry["rate"]

            processed_rates[entry_key] = {
                "valid_from": valid_from,
                "valid_to": valid_to,
                "currency_code": entry_key,
                "rate": rate
            }

        return {
            "valid_from": bundle_valid_from,
            "valid_to": bundle_valid_to,
            "currency_code": currency_code,
            "entries": processed_rates
        }


class InMemoryCachedCurrencyExchangers(object):
    """Creates and caches currency exchange rates.

    The caching and data source functionality could be further decoupled."""

    def __init__(self, data_source):
        self.cached_exchangers = {}
        self.data_source = data_source

    def get_exchanger_for_currency(self, currency_code):
        """Gets a currency exchanger from the in-memory cache (if it exists and is valid). If a valid
        exchanger is not found, one is created, and cached, using data downloaded from floatrates.com"""

        candidate = None
        lowercase_code = currency_code.lower()

        if lowercase_code in self.cached_exchangers: candidate = self.cached_exchangers[lowercase_code]
        if candidate is not None and candidate.is_valid(): return candidate

        rates = self.data_source.download_rates(currency_code)
        candidate = CurrencyExchanger(currency_code, rates)

        self.cached_exchangers[lowercase_code] = candidate
        return candidate

class CurrencyExchanger(object):
    """An in-memory currency exchanger that downloads data from http://www.floatrates.com/json-feeds.html.
    If no exchange rate information is found, it is downloaded and cached in-memory, and not re-downloaded.
    """

    def __init__(self, base_currency_code, rate_information):
        self.base_currency_code = base_currency_code
        self.rate_information = rate_information

    def is_valid(self):
        return self.remaining_validity_period_in_seconds() > 0

    def remaining_validity_period_in_seconds(self):
        now = datetime.datetime.now(tzlocal())
        return (self.rate_information["valid_to"] - now).total_seconds()

    def convert_amount_to(self, amount_in_base_currency, target_currency_code):
        """Converts the given amount from from_currency to to_currency, and returns the result."""
        lowercase_target_code = target_currency_code.lower()

        # The exchange rate data might not include the base currency, but
        # converting to self is a supported action
        if lowercase_target_code == self.base_currency_code.lower(): return amount_in_base_currency

        try:
            rate = self.rate_information["entries"][lowercase_target_code]["rate"]
            return amount_in_base_currency * rate
        except KeyError:
            raise MissingCurrencyException(target_currency_code)



