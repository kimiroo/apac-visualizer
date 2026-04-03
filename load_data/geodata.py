"""Module for handling geographic data and operations."""

import pycountry
import geopandas as gpd

from const.file_path import PATH_GEOJSON

class GeoData:
    """Manages loading and retrieving of country and region geospatial data."""

    def __init__(self):
        """Initializes the GeoData instance by loading all available GeoJSON data."""
        geojson_path_list = [f for f in PATH_GEOJSON.glob("*.json") if f.is_file()]

        self.geojson_dict = {}
        self.country_list = [{'name': 'All', 'code': None}]

        for geojson_path in geojson_path_list:
            country_code = geojson_path.stem.split('_')[0]
            country_name = self.get_name(country_code)
            is_level_1 = bool(geojson_path.stem.split('_')[1])
            geojson = gpd.read_file(geojson_path)

            self.geojson_dict[country_code] = {
                'code': country_code,
                'name': country_name,
                'is_level_1': is_level_1,
                'geojson': geojson
            }

            self.country_list.append({
                'code': country_code,
                'name': country_name
            })

    def get_geojson(self, code: str) -> tuple[gpd.GeoDataFrame | None, bool]:
        """Retrieves the GeoJSON data for a specific country code.

        Args:
            code (str): The ISO Alpha-3 country code.

        Returns:
            tuple: A tuple containing (geojson, is_level_1).
                geojson (gpd.GeoDataFrame): The GeoDataFrame for the country.
                is_level_1 (bool): True if Level 1 (regions) data is returned, False otherwise.
        """

        geo_obj = self.geojson_dict.get(code, {})
        is_level_1 = geo_obj.get('is_level_1', False)
        geojson = geo_obj.get('geojson', None)

        return geojson, is_level_1

    def get_name(self, code: str) -> str | None:
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
