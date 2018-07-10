# -*- coding: utf-8 -*-
"""Configuration."""

import os
import json

COUNTRY_DATA_JSON = os.environ.get("COUNTRY_DATA_JSON", default=None)
if not COUNTRY_DATA_JSON:
    raise ValueError("Please set the COUNTRY_DATA_JSON environment variable")

with open(COUNTRY_DATA_JSON) as f:
    COUNTRY_DATA = json.load(f)
