"""Module for rendering the Key Account Information Panel."""

import streamlit as st
import pandas as pd
import altair as alt

from lib.get_active_verticals import GetActiveVerticalString

class KeyAccountPanel:
    """Handles the rendering of the key account details panel in the Streamlit app."""

    def __init__(self, df_dealer: pd.DataFrame, config: dict) -> None:
        """Initializes the KeyAccountPanel.

        Args:
            df_key_account (pd.DataFrame): The dataframe containing key account information.
            config (dict): Application configuration dictionary.
        """
        self._df: pd.DataFrame = df_dealer
        self._config: dict = config
        self._active_vertical = GetActiveVerticalString(self._config)

    def draw(self, key_account_id: str) -> None:
        """Renders the key_account information panel for a specific key_account ID.

        Args:
            key_account_id (str): The unique identifier of the key account to display.
        """

        data = self._df[self._df['id'] == str(key_account_id)]

        if data.empty:
            st.warning('No data found for this key account.')
            return

        row = data.iloc[0]

        st.subheader(f'❤️ Key Account: {row['name']}')

        ### Information Table
        st.write('##### 📝 Key Account Information')

        # Extract active verticals (where value is True)
        active_vertical_string = self._active_vertical.get(row)

        # Define items to show
        items = [
            ('ID', row['id']),
            ('Name', row['name']),
            ('Address', row['address']),
            ('Is Customer', row['is_customer']),
            ('Value', row['value']),
            ('Water Consumption', row['water_consumption']),
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
            st.caption("No specific remarks available for this key account.")