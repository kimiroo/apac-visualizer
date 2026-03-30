"""Module for loading and processing priority target data from Excel sheets."""

from typing import TYPE_CHECKING
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

if TYPE_CHECKING:
    from openpyxl.workbook.workbook import _WorksheetOrChartsheetLike

class PriorityTargetData:
    """Manages the loading and structuring of priority target information."""

    def __init__(self, config: dict) -> None:
        """Initializes the PriorityTargetData instance.

        Args:
            config (dict): Application configuration containing vertical definitions.
        """
        self.df: pd.DataFrame = None
        self._config = config

    def load(self, sheet: "_WorksheetOrChartsheetLike") -> None:
        """Loads priority target data from an Excel worksheet.

        Args:
            sheet (_WorksheetOrChartsheetLike): The Excel worksheet containing priority target data.
        """
        priority_target_list = []

        # Load priority target data
        headers = {cell.value: i for i, cell in enumerate(sheet[1])}

        for priority_target in sheet.iter_rows(2):
            # Fixed data columns
            row_data = [str(priority_target[i].value) for i in range(7)] + \
                [float(priority_target[i].value or 0) for i in range(7, 11)] + \
                [bool(priority_target[11].value)]

            # Append boolean values for vertical columns dynamically
            for vertical in self._config['vertical']:
                row_data.append(
                    bool(priority_target[headers[vertical]].value)
                )

            priority_target_list.append(tuple(row_data))

        # Dynamically set extra columns
        columns_priority_target = [
            'area', 'country', 'region',
            'id', 'name', 'address', 'remarks',
            'lat', 'long',
            'value', 'water_consumption', 'is_customer'
        ]

        for vertical in self._config['vertical']:
            columns_priority_target.append(vertical)

        # Convert to Pandas DataFrame
        df = pd.DataFrame(priority_target_list, columns=columns_priority_target)

        # Convert DataFrame data to GeoDataFrame
        geometry = [Point(xy) for xy in zip(df['long'], df['lat'])]
        self.df = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')