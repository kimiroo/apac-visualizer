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

        ### Revenue Chart
        if self._config['showOptionalData']['projectedRevenue']:
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

        ### Information Table
        st.write('##### 📝 Dealer Information')

        # Extract active verticals (where value is True)
        active_vertical_string = self._active_vertical.get(row)

        # Define items to show
        items = [
            ('ID', row['id']),
            ('Name', row['name']),
            ('Tier', row['tier']),
            ('Profile', row['profile']),
            ('Address', row['address']),
            ('Actual Revenue', row['actual_revenue']),
            ('Projected Revenue', row['projected_revenue']),
            ('Verticals', active_vertical_string)
        ]

        # Handle optional keys
        exclude_keys = []

        if not self._config['showOptionalData']['projectedRevenue']:
            exclude_keys.append('Projected Revenue')

        filtered_items = [item for item in items if item[0] not in exclude_keys]

        keys, values = zip(*filtered_items)

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
            st.caption("No specific remarks available for this dealer.")