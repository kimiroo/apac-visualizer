"""Script to download and optimize GADM geospatial data."""

import os

import requests
from bs4 import BeautifulSoup
import geopandas as gpd


def optimize_gadm_data(input_path: str, output_path: str, tolerance: float = 0.01) -> None:
    """Optimizes GADM geospatial data by simplifying geometry.

    Args:
        input_path (str): Path to the original GADM file (GeoJSON, GPKG, etc.).
        output_path (str): Path to save the optimized file (GeoJSON recommended).
        tolerance (float, optional): Degree of simplification. Higher values reduce file size
            but make boundaries smoother/blockier. Defaults to 0.01.
    """
    # 1. Load Data
    # Use pyogrio engine for faster reading if installed
    gdf = gpd.read_file(input_path)

    # 2. Extract necessary columns (Based on GADM Level 1)
    # GID_0: Country Code (e.g., KOR), NAME_0: Country Name, NAME_1: Region Name (e.g., Seoul)
    keep_cols = ['GID_0', 'NAME_0', 'NAME_1', 'geometry']

    # Check if columns exist before filtering to avoid errors
    existing_cols = [col for col in keep_cols if col in gdf.columns]
    gdf = gdf[existing_cols]

    # 3. Simplify Geometry (Key to reducing file size)
    # preserve_topology=True prevents polygons from breaking or creating gaps
    gdf['geometry'] = gdf['geometry'].simplify(tolerance=tolerance, preserve_topology=True)

    # 4. Check Coordinate Reference System (Ensure WGS84 - EPSG:4326 for Folium)
    if gdf.crs != "EPSG:4326":
        gdf = gdf.to_crs("EPSG:4326")

    # 5. Save Result (Saving as a lightweight GeoJSON)
    gdf.to_file(output_path, driver='GeoJSON')

    # Output the results for verification
    print(f"Optimization Complete: {input_path} -> {output_path}")
    print(f"Original Size: {os.path.getsize(input_path) / 1024 / 1024:.2f} MB")
    print(f"Optimized Size: {os.path.getsize(output_path) / 1024 / 1024:.2f} MB")

if __name__ == "__main__":
    resp = requests.get('https://gadm.org/download_country.html')
    soup = BeautifulSoup(resp.text, 'html.parser')

    for choice in soup.select('#countrySelect option'):

        if choice.get('value'):
            value = choice.get('value').split('_')

            country_id = value[0]
            map_level = int(value[-1])

            level = 1 if map_level > 1 else 0

            os.makedirs('geodata/original', exist_ok=True)
            os.makedirs('geodata/optimized', exist_ok=True)

            print(f'Downloading {country_id}...')
            url = f'https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{country_id}_{level}.json'

            resp = requests.get(url)

            with open(f'geodata/original/{country_id}_{level}.json', 'w') as f:
                f.write(resp.text)

            #print(f'Optimizing {country_id}...')
            #optimize_gadm_data(f'geodata/original/{country_id}_{level}.json', f'geodata/optimized/{country_id}_{level}.json', 0.02)
