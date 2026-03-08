"""Module for loading and processing region data from Excel sheets."""

from typing import TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from openpyxl.workbook.workbook import _WorksheetOrChartsheetLike

class RegionData:
    """Manages the loading and structuring of regional market data."""

    def __init__(self, config):
        """Initializes the RegionData instance.

        Args:
            config (dict): Application configuration containing vertical definitions.
        """
        self.df: pd.DataFrame = None
        self._config = config

    def load(self, sheet: _WorksheetOrChartsheetLike):
        """Loads region data from an Excel worksheet, parsing dynamic vertical columns.

        Args:
            sheet (_WorksheetOrChartsheetLike): The Excel worksheet containing region data.
        """

        ### Parse header
        headers = {}

        extra_headers = ['Others', 'Total']

        col_start_idx = 2
        col_vertical = None

        for idx, cell in enumerate(sheet[1]):

            # Discard first 2
            if idx < 2:
                continue

            # New vertical column
            if ((idx - 2) % 6 == 0) and (idx != col_start_idx):
                # Append to headers
                headers[col_vertical] = col_start_idx

                # Reset variables
                col_start_idx = idx
                col_vertical = None

            # Skip to next column if valid vertical is already set
            if col_vertical:
                continue

            # New vertical found
            if cell.value in self._config['vertical'] + extra_headers:
                col_vertical = cell.value

        if col_vertical:
            # Append to headers
            headers[col_vertical] = col_start_idx

        ### Add data
        region_list = []

        for region in sheet.iter_rows(3):
            # Fixed data columns
            row_data = [str(region[i].value) for i in range(2)]

            # Add columns for each vertical dynamically
            for vertical in self._config['vertical'] + extra_headers:
                for idx in range(6):
                    base_idx = headers[vertical]
                    row_data.append(region[base_idx + idx].value)

            region_list.append(tuple(row_data))

        ### Dynamically set columns
        columns_region = ['country', 'region']

        for vertical in self._config['vertical'] + extra_headers:
            columns = [
                f'{vertical}_plant_cnt',
                f'{vertical}_dealer_cnt',
                f'{vertical}_projected_dealer_revenue',
                f'{vertical}_actual_dealer_revenue',
                f'{vertical}_potential_market_value',
                f'{vertical}_total_market_value'
            ]

            columns_region = columns_region + columns

        ### Convert to Pandas DataFrame
        self.df = pd.DataFrame(region_list, columns=columns_region)