"""Module for rendering the Priority Target Information Panel."""

import streamlit as st
import pandas as pd

from lib.get_active_verticals import GetActiveVerticalString
from lib.format_helper import format_currency, format_number

class PriorityTargetPanel:
    """Handles the rendering of the priority target details panel in the Streamlit app."""

    def __init__(self, df_dealer: pd.DataFrame, config: dict) -> None:
        """Initializes the KeyAccountPanel.

        Args:
            df_key_account (pd.DataFrame): The dataframe containing priority target information.
            config (dict): Application configuration dictionary.
        """
        self._df: pd.DataFrame = df_dealer
        self._config: dict = config
        self._active_vertical = GetActiveVerticalString(self._config)

    def draw(self, priority_target_id: str) -> None:
        """Renders the priority_target information panel for a specific priority_target ID.

        Args:
            key_account_id (str): The unique identifier of the priority target to display.
        """

        data = self._df[self._df['id'] == str(priority_target_id)]

        if data.empty:
            st.warning('Failed to load data for this priority target.')
            return

        row = data.iloc[0]

        st.subheader(f'❤️ Priority Target: {row['name']}')

        ### Information Table
        st.write('##### 📝 Priority Target Information')

        # Extract active verticals (where value is True)
        active_vertical_string = self._active_vertical.get(row)

        # Define items to show
        items = [
            ('ID', row['id']),
            ('Name', row['name']),
            ('Address', row['address']),
            ('Is Customer', str(row['is_customer'])),
            ('Value', format_currency(row['value'])),
            ('Water Consumption', format_number(row['water_consumption'], postfix=' L')),
            ('Verticals', active_vertical_string)
        ]

        keys, values = zip(*items)

        # Create a clean summary table for the UI
        info_data = {
            'Key': list(keys),
            'Value': list(values)
        }

        st.dataframe(
            pd.DataFrame(info_data),
            hide_index=True,
            on_select='ignore',
            column_config={
                'Key': st.column_config.TextColumn('Key', width='medium'),
                'Value': st.column_config.TextColumn('Value', width='large')
            }
        )

        ### Remarks
        st.write('##### 📌 Remarks')

        remarks_text = row.get('remarks', None)

        if remarks_text and str(remarks_text).strip() != 'None':
            st.info(f"{remarks_text}")
        else:
            # Placeholder when there are no remarks
            st.caption('No specific remarks available for this priority target.')