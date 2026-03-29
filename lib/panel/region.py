"""Module for rendering the Region Information Panel."""

import streamlit as st
import pandas as pd
from millify import millify

from lib.get_active_verticals import GetActiveVerticalString
from lib.grouped_bar_chart import grouped_bar_chart
from lib.pie_chart import pie_chart_with_percentage

class RegionPanel:
    """Handles the rendering of the region details panel in the Streamlit app."""

    def __init__(self, config: dict) -> None:
        """Initializes the RegionPanel.

        Args:
            df_dealer (pd.DataFrame): The dataframe containing dealer information.
            df_key_account (pd.DataFrame): The dataframe containing key account information.
            config (dict): Application configuration dictionary.
        """
        self._config: dict = config
        self._active_vertical = GetActiveVerticalString(self._config)

    def draw(self,
             df_region: pd.DataFrame,
             df_dealers: pd.DataFrame,
             df_key_accounts: pd.DataFrame,
             country: str,
             vertical: str,
             region: str | None = None) -> None:
        """Renders the region information panel.

        Args:
            country (str): The name of the country.
            region (str): The name of the region.
            vertical (str): The currently selected vertical filter.
            df_filtered_dealers (pd.DataFrame, optional): Filtered dataframe of dealers. Defaults to None.
        """

        data = df_region
        if region:
            data = data[data['region'] == region]

        # Select a row if it's region, or sum rows if it's country
        row = data.iloc[0] if region else data.sum(numeric_only=True)

        ### Common
        if region:
            st.subheader(f'📍 Region: {region} ({vertical})')
        else:
            st.subheader(f'📍 Country: {country} ({vertical})')

        verticals = self._config['vertical'] + ['Total']
        v_cols = self._config['vertical']
        show_pie_chart = True

        if vertical != 'Total':
            verticals = [vertical]
            show_pie_chart = False


        ### Summary
        col1, col2 = st.columns(2)

        with col1:
            total_prj_rev = row[f'{vertical}_total_market_value']
            dealer_cnt = len(df_dealers)

            st.metric(label='Total Market Value', value=f'${millify(total_prj_rev, precision=1).upper()}')
            st.metric(label='Dealer Count', value=dealer_cnt)

        with col2:
            total_act_rev = row[f'{vertical}_potential_market_value']
            plant_cnt = row[f'{vertical}_plant_cnt']

            st.metric(label='Potential Market Value', value=f'${millify(total_act_rev, precision=1).upper()}')
            st.metric(label='Plant Count', value=plant_cnt)


        ### Actual (vs Projected) Dealer Revenue
        if vertical == 'Total' or self._config['showOptionalData']['projectedRevenue']:
            st.write('##### 📊 Dealer Revenue')

            # Create a long-form dataframe for Altair
            plot_revenue = []
            for v in verticals:

                if self._config['showOptionalData']['projectedRevenue']:
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


        ### Potential vs Actual Market Value
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

            verticals_no_total = self._config['vertical']

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


        ### Dealers
        st.write(f'##### 🤝 Dealer list (Vertical: {vertical})')

        df_dealers_display = df_dealers[['id', 'name', 'tier', 'profile', 'address']].copy()
        df_dealers_display['vertical'] = df_dealers[v_cols].apply(self._active_vertical.get, axis=1)

        df_dealers_display.columns = ['ID', 'Name', 'Tier', 'Profile', 'Address', 'Vertical']

        # Reset index and convert to human-friendly numbering
        df_dealers_display = df_dealers_display.reset_index(drop=True)
        df_dealers_display.index = df_dealers_display.index + 1

        # Draw
        st.dataframe(
            df_dealers_display,
            on_select='ignore',
            width='content',
            column_config={
                'ID': st.column_config.TextColumn('ID', width=100),
                'Name': st.column_config.TextColumn('Name', width='medium'),
                'Tier': st.column_config.TextColumn('Tier', width='small'),
                'Profile': st.column_config.TextColumn('Profile', width=150),
                'Address': st.column_config.TextColumn('Address', width='medium'),
                'Vertical': st.column_config.TextColumn('Vertical', width='large')
            }
        )

        st.caption("💡 Tip: This table is affected by 'Vertical' filter under 'Heatmap'.")


        ### Key Accounts
        st.write(f'##### ❤️ Key Account list (Vertical: {vertical})')

        df_key_account_display = df_key_accounts[['id', 'name', 'address']].copy()
        df_key_account_display['vertical'] = df_key_accounts[v_cols].apply(self._active_vertical.get, axis=1)

        df_key_account_display.columns = ['ID', 'Name', 'Address', 'Vertical']

        # Reset index and convert to human-friendly numbering
        df_key_account_display = df_key_account_display.reset_index(drop=True)
        df_key_account_display.index = df_key_account_display.index + 1

        # Draw
        st.dataframe(
            df_key_account_display,
            on_select='ignore',
            width='content',
            column_config={
                'ID': st.column_config.TextColumn('ID', width=100),
                'Name': st.column_config.TextColumn('Name', width='medium'),
                'Address': st.column_config.TextColumn('Address', width='medium'),
                'Vertical': st.column_config.TextColumn('Vertical', width='large')
            }
        )

        st.caption("💡 Tip: This table is affected by 'Vertical' filter under 'Heatmap'.")

        ### Remarks
        if region:
            st.write('##### 📌 Remarks')

            remarks_text = row.get('remarks', None)

            if remarks_text and str(remarks_text).strip() != 'None':
                st.info(f"{remarks_text}")
            else:
                # Placeholder when there are no remarks
                st.caption("No specific remarks available for this region.")
