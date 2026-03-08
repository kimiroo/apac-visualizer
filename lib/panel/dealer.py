import streamlit as st
import pandas as pd

class DealerPanel:
    def __init__(self, df_dealer: pd.DataFrame, config: dict):
        self._df: pd.DataFrame = df_dealer
        self._config: dict = config

    def draw(self, dealer_id: str):

        data = self._df[self._df['id'] == str(dealer_id)]

        if data.empty:
            st.warning('No data found for this dealer.')
            return

        row = data.iloc[0]

        st.subheader(f'🤝 Dealer: {row['name']}')

        revenue_header = f'Revenue ({self._config['data']['currency']})'

        performance_df = pd.DataFrame({
            'Category': ['Projected', 'Actual'],
            revenue_header: [row['projected_revenue'], row['actual_revenue']]
        })

        st.bar_chart(
            data=performance_df,
            x='Category',
            y=revenue_header,
            color='Category' # Different color for projected and actual revenue
        )

        st.divider()

        st.write('##### 📝 Dealer Information')

        # Extract active verticals (where value is True)
        active_verticals = [v for v in self._config['vertical'] if row[v]]
        vertical_display = ', '.join(active_verticals) if active_verticals else 'None'

        # Create a clean summary table for the UI
        info_data = {
            'Field': ['ID', 'Name', 'Tier', 'Verticals'],
            'Value': [row['id'], row['name'], row['tier'], vertical_display]
        }

        st.dataframe(
            pd.DataFrame(info_data),
            hide_index=True,
            on_select='ignore',
            column_config={
                'Field': st.column_config.TextColumn('Key', width='small'),
                'Value': st.column_config.TextColumn('Value', width='large')
            }
        )