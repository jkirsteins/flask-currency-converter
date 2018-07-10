# Currency converter

## Data sets

The data for the territory<->country mapping is taken from https://datahub.io/core/country-codes#data.

It is processed (to remove unneeded data) by:

    cat countries.json | jq 'map({iso4217_currencies: .["ISO4217-currency_alphabetic_code"], iso3166_country_code: .["ISO3166-1-Alpha-2"], territory_display_name: .["CLDR display name"]})'

Each entry (corresponding to a territory) in the resulting JSON file will have
these keys:

    {
      "iso4217_currencies": "ZMW",
      "iso3166_country_code": "ZM",
      "territory_display_name": "Zambia"
    }

Note: no checks for 'null' are performed/filtered (e.g. for Antarctica).
