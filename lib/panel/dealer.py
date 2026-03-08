"""Module for rendering the Dealer Information Panel."""

import streamlit as st
import pandas as pd
import altair as alt

from lib.get_active_verticals import GetActiveVerticalString

class DealerPanel:
    """Handles the rendering of the dealer details panel in the Streamlit app."""

    def __init__(self, df_dealer: pd.DataFrame, config: dict) -> None:
        """Initializes the DealerPanel.

        Args:
            df_dealer (pd.DataFrame): The dataframe containing dealer information.
            config (dict): Application configuration dictionary.
        """
        self._df: pd.DataFrame = df_dealer
        self._config: dict = config
        self._active_vertical = GetActiveVerticalString(self._config)

    def draw(self, dealer_id: str) -> None:
        """Renders the dealer information panel for a specific dealer ID.

        Args:
            dealer_id (str): The unique identifier of the dealer to display.
        """

        data = self._df[self._df['id'] == str(dealer_id)]

        if data.empty:
            st.warning('No data found for this dealer.')
            return

        row = data.iloc[0]

        st.subheader(f'🤝 Dealer: {row['name']}')

        performance_df = pd.DataFrame({
            'Revenue': ['Projected', 'Actual'],
            'Value': [row['projected_revenue'], row['actual_revenue']]
        })

        chart = alt.Chart(performance_df).mark_bar().encode(
            x=alt.X('Revenue:N', title='Revenue'),
            y=alt.Y('Value:Q', title='Value', axis=alt.Axis(format='$,.2f')),
            color=alt.Color('Revenue:N', scale=alt.Scale(range=['#1F77B4', '#B8B8B8'])),
            tooltip=alt.Tooltip(format='$,.2f')
        )

        st.altair_chart(chart, width='stretch')

        st.write('##### 📝 Dealer Information')

        # Extract active verticals (where value is True)
        active_vertical_string = self._active_vertical.get(row)

        # Create a clean summary table for the UI
        info_data = {
            'Key': ['ID', 'Name', 'Tier', 'Profile', 'Location', 'Verticals'],
            'Value': [row['id'], row['name'], row['tier'], row['profile'], row['location'], active_vertical_string]
        }

        st.dataframe(
            pd.DataFrame(info_data),
            hide_index=True,
            on_select='ignore',
            column_config={
                'Key': st.column_config.TextColumn('Key', width='small'),
                'Value': st.column_config.TextColumn('Value', width='large')
            }
        )