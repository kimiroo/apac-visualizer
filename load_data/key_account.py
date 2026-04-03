"""Module for loading and processing key account data from Excel sheets."""

from typing import TYPE_CHECKING
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

if TYPE_CHECKING:
    from openpyxl.workbook.workbook import _WorksheetOrChartsheetLike

class KeyAccountData:
    """Manages the loading and structuring of key account information."""

    def __init__(self, config: dict) -> None:
        """Initializes the DealerCustomerData instance.

        Args:
            config (dict): Application configuration containing vertical definitions.
        """
        self.df: pd.DataFrame = None
        self._config = config

    def load(self, sheet: "_WorksheetOrChartsheetLike") -> None:
        """Loads key account data from an Excel worksheet.

        Args:
            sheet (_WorksheetOrChartsheetLike): The Excel worksheet containing key account data.
        """
        key_account_list = []

        # Load key account data
        headers = {cell.value: i for i, cell in enumerate(sheet[1])}

        for key_account in sheet.iter_rows(2):
            # Fixed data columns
            row_data = [str(key_account[i].value) for i in range(5)] + \
                [float(key_account[i].value or 0) for i in range(5, 9)] + \
                [bool(key_account[9].value)]

            # Append boolean values for vertical columns dynamically
            for vertical in self._config['vertical']:
                row_data.append(
                    bool(key_account[headers[vertical]].value)
                )

            key_account_list.append(tuple(row_data))

        # Dynamically set extra columns
        columns_key_account = [
            'id', 'account_name', 'name', 'address', 'remarks',
            'lat', 'long',
            'value', 'water_consumption', 'is_customer'
        ]

        for vertical in self._config['vertical']:
            columns_key_account.append(vertical)

        # Convert to Pandas DataFrame
        df = pd.DataFrame(key_account_list, columns=columns_key_account)

        # Convert DataFrame data to GeoDataFrame
        geometry = [Point(xy) for xy in zip(df['long'], df['lat'])]
        self.df = gpd.GeoDataFrame(df, geometry=geometry, crs='EPSG:4326')