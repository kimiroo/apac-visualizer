import streamlit as st
import pandas as pd
import altair as alt
from millify import millify

from lib.grouped_bar_chart import grouped_bar_chart
from lib.pie_chart import pie_chart_with_percentage

class RegionPanel:
    def __init__(self, df_dealer: pd.DataFrame, config: dict):
        self._df: pd.DataFrame = df_dealer
        self._config: dict = config

    def draw(self, country: str, region: str, selected_vertical):

        data = self._df[(self._df['country'] == str(country)) & (self._df['region'] == str(region))]

        if data.empty:
            st.warning('No data found for this region.')
            return

        row = data.iloc[0]

        st.subheader(f'📍 Region: {region} ({selected_vertical})')

        ### Common
        verticals = self._config['vertical'] + ['Others', 'Total']


        ### Summary
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            total_prj_rev = row['Total_projected_dealer_revenue']
            st.metric(label='Total Market Value', value=f'${millify(total_prj_rev, precision=2)}')
        with col2:
            total_act_rev = row['Total_actual_dealer_revenue']
            st.metric(label='Potential Market Value', value=f'${millify(total_act_rev, precision=2)}')
        with col3:
            dealer_cnt_cols = self._df.columns[self._df.columns.str.endswith('_plant_cnt')]
            dealer_cnt = row[dealer_cnt_cols].sum()
            st.metric(label='Dealer Count', value=dealer_cnt)
        with col4:
            plant_cnt_cols = self._df.columns[self._df.columns.str.endswith('_dealer_cnt')]
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
        st.write('##### 📊 Market Weightage')

        verticals_no_total = self._config['vertical'] + ['Others']

        # Prepare data specifically for the pie chart
        plot_share = []

        for v in verticals_no_total:
            val = row[f'{v}_total_market_value']
            if val > 0:
                plot_share.append({'Vertical': v, 'Value': val})

        df_share = pd.DataFrame(plot_share)

        # Draw pie chart
        chart_share = pie_chart_with_percentage(df_share, '$,.2f')
        if chart_share:
            st.altair_chart(chart_share, width='stretch')
        else:
            st.warning('No data to display')
