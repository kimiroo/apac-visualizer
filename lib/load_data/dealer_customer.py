"""Module for loading and processing dealer customer data from Excel sheets."""

from typing import TYPE_CHECKING
from datetime import datetime, date
import pandas as pd

if TYPE_CHECKING:
    from openpyxl.workbook.workbook import _WorksheetOrChartsheetLike

class DealerCustomerData:
    """Manages the loading and structuring of dealer customer information."""

    def __init__(self, config: dict) -> None:
        """Initializes the DealerCustomerData instance.

        Args:
            config (dict): Application configuration containing vertical definitions.
        """
        self.df: pd.DataFrame = None
        self._config = config

    def load(self, sheet: "_WorksheetOrChartsheetLike") -> None:
        """Loads dealer customer data from an Excel worksheet.

        Args:
            sheet (_WorksheetOrChartsheetLike): The Excel worksheet containing dealer customer data.
        """
        dealer_customer_list = []

        # Load dealer customer data
        for dealer_customer in sheet.iter_rows(2):

            row_data = [
                str(dealer_customer[0].value),   # Dealer ID
                str(dealer_customer[2].value),   # Customer Name
                float(dealer_customer[3].value or 0), # Sale Value
                dealer_customer[4].value.date(), # Sale Date
                str(dealer_customer[5].value),   # Sale Model
            ]

            dealer_customer_list.append(tuple(row_data))

        # Dynamically set extra columns
        columns_dealer_customer = [
            'dealer_id',
            'name',
            'sale_value',
            'sale_date',
            'sale_model'
        ]

        # Convert to Pandas DataFrame
        self.df = pd.DataFrame(dealer_customer_list, columns=columns_dealer_customer)