"""Module for loading and processing dealer data from Excel sheets."""

from typing import TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from openpyxl.workbook.workbook import _WorksheetOrChartsheetLike

class DealerData:
    """Manages the loading and structuring of dealer information."""

    def __init__(self, config):
        """Initializes the DealerData instance.

        Args:
            config (dict): Application configuration containing vertical definitions.
        """
        self.df: pd.DataFrame = None
        self._config = config

    def load(self, sheet: _WorksheetOrChartsheetLike):
        """Loads dealer data from an Excel worksheet.

        Args:
            sheet (_WorksheetOrChartsheetLike): The Excel worksheet containing dealer data.
        """
        partner_list = []

        # Load partner data
        headers = {cell.value: i for i, cell in enumerate(sheet[1])}

        for partner in sheet.iter_rows(2):
            # Fixed data columns
            row_data = [str(partner[i].value) for i in range(7)] + [partner[i].value for i in range(7, 12)]

            # Append boolean values for vertical columns dynamically
            for vertical in self._config['vertical']:
                row_data.append(
                    bool(partner[headers[vertical]].value)
                )

            partner_list.append(tuple(row_data))

        # Dynamically set extra columns
        columns_partner = [
            'area', 'country', 'sales_org',
            'id', 'name', 'tier', 'profile',
            'location', 'lat', 'long',
            'projected_revenue', 'actual_revenue'
        ]

        for vertical in self._config['vertical']:
            columns_partner.append(vertical)

        # Convert to Pandas DataFrame
        self.df = pd.DataFrame(partner_list, columns=columns_partner)