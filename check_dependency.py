"""Checks for required dependencies.

Attempts to import all necessary libraries. Exits with status code 0 if
successful, or 1 if any import fails.
"""

import sys

try:
    import bs4
    import folium
    import geopandas
    import millify
    import openpyxl
    import osmnx
    import pycountry
    import pyogrio
    import yaml
    import requests
    import streamlit
    import streamlit_folium
    import topojson
except ImportError:
    sys.exit(1)
else:
    sys.exit(0)