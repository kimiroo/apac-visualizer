from typing import TYPE_CHECKING
import pandas as pd

if TYPE_CHECKING:
    from openpyxl.workbook.workbook import _WorksheetOrChartsheetLike

class KeyAccountData:
    def __init__(self):
        self.df: pd.DataFrame = None

    def load(self, sheet: _WorksheetOrChartsheetLike):
        key_account_list = []

        # Load key account data
        for key_account in sheet.iter_rows(2):
            key_account_list.append((
                key_account[0].value, # Country
                key_account[1].value, # Region
                key_account[2].value, # Account Name
                key_account[3].value  # Vertical
            ))

        columns = ['country', 'region', 'name', 'vertical']

        self.df = pd.DataFrame(key_account_list, columns=columns)