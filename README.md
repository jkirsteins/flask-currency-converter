# Currency converter

## Running the project

Run it by using the provided ./rundev.sh script (it will enable the 
development environment, and save some typing)

## Testing the project

Please use the provided ./test.sh script, and execute it from the root folder.

If you try to test without it, some of the test
files will be unable to find and import modules from 'app'.

## Conventions / Glossary

- the terms "territory" and "country" are used interchangeably (e.g. Åland Islands are not a country,
  but they have their own entry with their own territory code)
- currency codes are always 3-characters long (**ISO4217**)
- country codes are always 2-characters long (**ISO3166**)

## Notes on configuration

Configuration is done via environment variables. The project supports .env files. 

The required configuration keys are:

- SECRET_KEY (for Flask sessions)
- COUNTRY_DATA_JSON - a filename which contains country/currency data (see below for more details)

### Example .env file

    $ cat .env 
    SECRET_KEY=secret_stuff
    COUNTRY_DATA_JSON=countries_processed.json


## Notes for Future Revisions

- the list of known currencies comes from a different source than the actual exchange rates,
  so it is possible that an exchange rate for X is unavailable, even though we display it as an
  option for the user.

  For example, converting from BMD is an option, but the exchange rate source does not recognize this.

## Endpoints

### HTML / User-facing

- the address `/ui/convert` will allow a user to convert between two currencies
- the address `/ui/country_lookup` will allow a user to lookup countries based on a currency
- the address `/ui/currency_lookup` will allow a user to lookup currencies for a given country

### API

The current API is versioned simply via path, under "/api/v1". There are two endpoints:

- the endpoint `GET /api/v1/country/<code>/currency` will return a JSON array of currency codes
  in-use in the given territory (identified by a 2-character **ISO3166** code, e.g. `US` or `GB`)
- the endpoint `GET /api/v1/currency/<code>/country` will return a JSON array of country codes
  that use the given currency (identified by a 3-character **ISO4217** code, e.g. `USD`, `GBP`, `EUR`)
- the endpoint `GET /api/v1/currency/<code>/amount/<amount>` can be used to convert a value between currencies.
  By default, this endpoint will return the specified amount in the specified currency, but it also accepts
  a `?display_currency_code=...` query parameter.

  Semantically, it is the same value, so the `?display_currency_code` parameter is a query parameter,
  and not included in the URL.

  This endpoint will set the Cache-Control response header to match the time the currency information is
  expected to remain unchanged.

## Data sets

### Currency exchange rates

Exchange rates are downloaded from http://www.floatrates.com/json-feeds.html.

The exchange rates are downloaded on first-request. No initialization is needed.

### Countries and currency use

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
