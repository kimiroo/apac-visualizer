"""Module for extracting active vertical strings from data rows."""

import pandas as pd

class GetActiveVerticalString:
    """Helper class to generate a string of active verticals for a data row."""

    def __init__(self, config: dict) -> None:
        """Initializes with the application configuration.

        Args:
            config (dict): The configuration dictionary containing 'vertical' keys.
        """
        self._config = config

    def get(self, row: pd.Series) -> str:
        """Generates a comma-separated string of active verticals.

        Args:
            row (pd.Series): A row from the dataframe.

        Returns:
            str: A string listing active verticals, or 'None'.
        """
        v_cols = self._config['vertical']
        active = [v for v in v_cols if row[v]]

        return ', '.join(active) if active else 'None'