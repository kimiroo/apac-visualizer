import geopandas as gpd
import pandas as pd
from shapely.geometry import Point


def filter_by_geometry(
        dataframe: pd.DataFrame | gpd.GeoDataFrame,
        country_gdf: gpd.GeoDataFrame,
        region: str | None = None
    ) -> gpd.GeoDataFrame:
    """Filters a DataFrame of points by a geographic boundary.

    Args:
        dataframe (pd.DataFrame): The DataFrame containing 'lat' and 'long' columns.
        country_gdf (gpd.GeoDataFrame): The GeoDataFrame defining the boundaries.
        region (str, optional): The specific region name to filter by. Defaults to None.

    Returns:
        gpd.GeoDataFrame: The filtered GeoDataFrame containing points within the boundary.
    """
    # Convert DataFrame to GeoDataFrame
    if isinstance(dataframe, gpd.GeoDataFrame):
        gdf = dataframe
    else:
        geometry = [Point(xy) for xy in zip(dataframe['long'], dataframe['lat'])]
        gdf = gpd.GeoDataFrame(dataframe, geometry=geometry, crs='EPSG:4326')

    if region:
        # Filter the polygons first to get only the specific region
        target_boundary = country_gdf[country_gdf['NAME_1'] == region]
    else:
        target_boundary = country_gdf

    # Drop 'index_right' if it already exists to prevent ValueError during sjoin
    if 'index_right' in gdf.columns:
        gdf = gdf.drop(columns=['index_right'])

    # Also ensure target_boundary does not contain 'index_right'
    if 'index_right' in target_boundary.columns:
        target_boundary = target_boundary.drop(columns=['index_right'])

    # Spatial Join
    filtered_by_geo = gpd.sjoin(gdf, target_boundary, predicate='within')

    return filtered_by_geo