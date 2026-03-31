"""Script to download and optimize GADM geospatial data."""

import os

import requests
from bs4 import BeautifulSoup

target = [
    'South Korea',
    'Taiwan',
    'Japan',
    'Australia',
    'New Zealand',
    'Philippines',
    'Indonesia',
    'Malaysia',
    'Singapore',
    'Thailand',
    'Vietnam'
]

if __name__ == "__main__":
    resp = requests.get('https://gadm.org/download_country.html')
    soup = BeautifulSoup(resp.text, 'html.parser')

    for choice in soup.select('#countrySelect option'):

        if choice.get('value'):
            value = choice.get('value').split('_')

            country_id = value[0]
            country = value[1]
            map_level = int(value[-1])

            level = 1 if map_level > 1 else 0

            if country not in target:
                continue

            os.makedirs('geodata/original', exist_ok=True)

            print(f'Downloading {country_id}...')
            url = f'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{country_id}_{level}.json'

            resp = requests.get(url)

            with open(f'geodata/original/{country_id}_{level}.json', 'w') as f:
                f.write(resp.text)
