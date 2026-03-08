"""Module for handling geographic data and operations."""

import os
from pathlib import Path

import pycountry
import geopandas as gpd
from shapely.geometry import Point

GEODATA_PATH = Path('geodata/original')

class GeoData:
    """Manages loading and retrieving of country and region geospatial data."""

    def __init__(self):
        """Initializes the GeoData instance by loading available country codes."""
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
        """Retrieves the GeoJSON data for a specific country code.

        Args:
            code (str): The ISO Alpha-3 country code.

        Returns:
            tuple: A tuple containing (geojson, is_level_1).
                geojson (gpd.GeoDataFrame): The GeoDataFrame for the country.
                is_level_1 (bool): True if Level 1 (regions) data is returned, False otherwise.
        """
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
            """Returns the best display name for a given ISO Alpha-3 code.

            Args:
                code (str): The ISO Alpha-3 country code.

            Returns:
                str: The common name of the country, or None if not found.
            """
            try:
                country = pycountry.countries.get(alpha_3=code.upper())
                if not country:
                    return None
                # Priority: common_name > name
                return getattr(country, 'common_name', country.name)
            except Exception:
                return None

def filter_by_geometry(dataframe, country_gdf, region = None):
    """Filters a DataFrame of points by a geographic boundary.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing 'lat' and 'long' columns.
        country_gdf (gpd.GeoDataFrame): The GeoDataFrame defining the boundaries.
        region (str, optional): The specific region name to filter by. Defaults to None.

    Returns:
        gpd.GeoDataFrame: The filtered GeoDataFrame containing points within the boundary.
    """
    # Convert DataFrame to GeoDataFrame
    geometry = [Point(xy) for xy in zip(dataframe['long'], dataframe['lat'])]
    gdf = gpd.GeoDataFrame(dataframe, geometry=geometry, crs="EPSG:4326")

    if region:
        # Filter the polygons first to get only the specific region
        target_boundary = country_gdf[country_gdf['NAME_1'] == region]
    else:
        target_boundary = country_gdf

    # Spatial Join
    filtered_by_geo = gpd.sjoin(gdf, target_boundary, predicate='within')

    return filtered_by_geo