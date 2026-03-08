import streamlit as st
import pandas as pd

class RegionPanel:
    def __init__(self, df_dealer: pd.DataFrame, config: dict):
        self._df: pd.DataFrame = df_dealer
        self._config: dict = config

    def draw(self, country: str, region: str):

        st.subheader(region)
        st.write('Region')

        data = self._df[(self._df['country'] == str(country)) & (self._df['region'] == str(region))]

        if data.empty:
            st.warning('No data found for this region.')
            return