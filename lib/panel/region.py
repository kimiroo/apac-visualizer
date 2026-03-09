"""Module for rendering the Region Information Panel."""

import streamlit as st
import pandas as pd
from millify import millify

from lib.get_active_verticals import GetActiveVerticalString
from lib.grouped_bar_chart import grouped_bar_chart
from lib.pie_chart import pie_chart_with_percentage

class RegionPanel:
    """Handles the rendering of the region details panel in the Streamlit app."""

    def __init__(self, df_dealer: pd.DataFrame, df_key_account: pd.DataFrame, config: dict) -> None:
        """Initializes the RegionPanel.

        Args:
            df_dealer (pd.DataFrame): The dataframe containing dealer information.
            df_key_account (pd.DataFrame): The dataframe containing key account information.
            config (dict): Application configuration dictionary.
        """
        self._df_d: pd.DataFrame = df_dealer
        self._df_k: pd.DataFrame = df_key_account
        self._config: dict = config
        self._active_vertical = GetActiveVerticalString(self._config)

    def draw(self,
             country: str,
             vertical: str,
             region: str | None = None,
             df_filtered_dealers: pd.DataFrame | None = None) -> None:
        """Renders the region information panel.

        Args:
            country (str): The name of the country.
            region (str): The name of the region.
            vertical (str): The currently selected vertical filter.
            df_filtered_dealers (pd.DataFrame, optional): Filtered dataframe of dealers. Defaults to None.
        """

        ### Data Filtering

        # Create filter mask
        mask_data = (self._df_d['country'] == str(country))

        if region:
            mask_data &= (self._df_d['region'] == str(region))

        # Filter data
        data = self._df_d[mask_data]

        if data.empty:
            st.warning('No data found for this region.')
            return

        # Select a row if it's region, or sum rows if it's country
        row = data.iloc[0] if region else data.sum(numeric_only=True)

        ### Common
        if region:
            st.subheader(f'📍 Region: {region} ({vertical})')
        else:
            st.subheader(f'📍 Country: {country} ({vertical})')

        verticals = self._config['vertical'] + ['Others', 'Total']
        show_pie_chart = True

        if vertical != 'Total':
            verticals = [vertical]
            show_pie_chart = False


        ### Summary
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_prj_rev = row['Total_projected_dealer_revenue']
            st.metric(label='Total Market Value', value=f'${millify(total_prj_rev, precision=2)}')
        with col2:
            total_act_rev = row['Total_actual_dealer_revenue']
            st.metric(label='Potential Market Value', value=f'${millify(total_act_rev, precision=2)}')
        with col3:
            dealer_cnt_cols = self._df_d.columns[self._df_d.columns.str.endswith('_plant_cnt')]
            dealer_cnt = row[dealer_cnt_cols].sum()
            st.metric(label='Dealer Count', value=dealer_cnt)
        with col4:
            plant_cnt_cols = self._df_d.columns[self._df_d.columns.str.endswith('_dealer_cnt')]
            plant_cnt = row[plant_cnt_cols].sum()
            st.metric(label='Plant Count', value=plant_cnt)


        ### Projected vs Actual Dealer Revenue
        st.write('##### 📊 Dealer Revenue')

        # Create a long-form dataframe for Altair
        plot_revenue = []
        for v in verticals:
            plot_revenue.append({'Vertical': v, 'Type': 'Projected', 'Value': row[f'{v}_projected_dealer_revenue']})
            plot_revenue.append({'Vertical': v, 'Type': 'Actual', 'Value': row[f'{v}_actual_dealer_revenue']})

        df_revenue = pd.DataFrame(plot_revenue)

        chart_revenue = grouped_bar_chart(
            df_revenue,
            ('Vertical:N', 'Verticals'), # X-Axis config
            ('Value:Q', 'Value'),        # Y-Axis config
            '$,.2f'
        )

        st.altair_chart(chart_revenue, width='stretch')


        ### Projected vs Actual Dealer Revenue
        st.write('##### 📊 Market Value')

        # Create a long-form dataframe for Altair
        plot_market_value = []
        for v in verticals:
            plot_market_value.append({'Vertical': v, 'Type': 'Potential', 'Value': row[f'{v}_potential_market_value']})
            plot_market_value.append({'Vertical': v, 'Type': 'Total', 'Value': row[f'{v}_total_market_value']})

        df_market_value = pd.DataFrame(plot_market_value)

        chart_market_value = grouped_bar_chart(
            df_market_value,
            ('Vertical:N', 'Verticals'), # X-Axis config
            ('Value:Q', 'Market Value'), # Y-Axis config
            '$,.2f'
        )

        st.altair_chart(chart_market_value, width='stretch')


        ### Vertical Weightage
        if show_pie_chart:
            st.write('##### 📊 Market Weightage')

            verticals_no_total = self._config['vertical'] + ['Others']

            # Prepare data specifically for the pie chart
            plot_share = []

            for v in verticals_no_total:
                val = row[f'{v}_total_market_value']
                if val > 0:
                    plot_share.append({'Vertical': v, 'Value': val})

            df_share = pd.DataFrame(plot_share)
            chart_share = pie_chart_with_percentage(df_share, '$,.2f')

            # Draw pie chart
            if chart_share:
                st.altair_chart(chart_share, width='stretch')
            else:
                st.warning('No data to display')


        ### Filtered Dealers
        st.write(f'##### 🤝 Dealer list (Vertical: {vertical})')

        v_cols = self._config['vertical']

        display_df = df_filtered_dealers[['id', 'name', 'tier', 'profile', 'location']].copy()
        display_df['Vertical'] = df_filtered_dealers[v_cols].apply(self._active_vertical.get, axis=1)

        display_df.columns = ['ID', 'Name', 'Tier', 'Profile', 'Location', 'Vertical']

        # Reset index and convert to human-friendly numbering
        display_df = display_df.reset_index(drop=True)
        display_df.index = display_df.index + 1

        # Draw
        st.dataframe(
            display_df,
            on_select='ignore',
            width='content',
            column_config={
                'ID': st.column_config.TextColumn('ID', width=100),
                'Name': st.column_config.TextColumn('Name', width='medium'),
                'Tier': st.column_config.TextColumn('Tier', width='small'),
                'Profile': st.column_config.TextColumn('Profile', width=150),
                'Location': st.column_config.TextColumn('Location', width='medium'),
                'Vertical': st.column_config.TextColumn('Vertical', width='large')
            }
        )

        st.caption("💡 Tip: This table is affected by 'Vertical' filter under 'Heatmap'.")


        ### Key Accounts
        st.write(f'##### ❤️ Key Account')

        # Create filter mask
        mask_k = (self._df_k['country'] == str(country))

        if region:
            mask_k &= (self._df_k['region'] == str(region))

        # Filter data
        key_account = self._df_k[mask_k]

        # Refine data
        key_account = key_account[['name', 'vertical']].copy()
        key_account.columns = ['Name', 'Vertical']

        # Reset index and convert to human-friendly numbering
        key_account = key_account.reset_index(drop=True)
        key_account.index = key_account.index + 1

        # Draw
        st.dataframe(
            key_account,
            on_select='ignore',
            width='content',
        )
