import os
from pathlib import Path

import pycountry
import geopandas as gpd
from shapely.geometry import Point

GEODATA_PATH = Path('geodata/original')

class GeoData:
    def __init__(self):
        # Load country list
        country_codes = [f.stem.split('_')[0] for f in GEODATA_PATH.glob("*.json") if f.is_file()]
        country_dict = {}

        for country_code in country_codes:
            country_name = self.get_name(country_code)
            if country_name:
                country_dict[country_name] = country_code

        self.country_list = sorted([
            {'name': name, 'code': code}
            for name, code in country_dict.items()
        ], key=lambda x: x['name'])

        # All 'All' option
        self.country_list = [{'name': 'All', 'code': None}] + self.country_list

    def get_geojson(self, code):
        if code:
            is_level_1 = True
            file_path = GEODATA_PATH / f'{code}_1.json'

            if not os.path.exists(file_path):
                is_level_1 = False
                file_path = GEODATA_PATH / f'{code}_0.json'

            geojson = gpd.read_file(file_path)

            return geojson, is_level_1

        return None, False

    def get_name(self, code):
            """Returns the best display name for a given ISO Alpha-3 code."""
            try:
                country = pycountry.countries.get(alpha_3=code.upper())
                if not country:
                    return None
                # Priority: common_name > name
                return getattr(country, 'common_name', country.name)
            except Exception:
                return None

def filter_by_geometry(dataframe, country_gdf):
    # Convert DataFrame to GeoDataFrame
    geometry = [Point(xy) for xy in zip(dataframe['long'], dataframe['lat'])]
    gdf = gpd.GeoDataFrame(dataframe, geometry=geometry, crs="EPSG:4326")

    # Spatial Join
    filtered_by_geo = gpd.sjoin(gdf, country_gdf, predicate='within')

    return filtered_by_geo