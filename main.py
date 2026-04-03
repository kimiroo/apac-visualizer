"""Main entry point for the APAC Visualizer Streamlit application.

This script initializes the Streamlit app, loads configuration and data,
sets up the sidebar filters, and renders the interactive map and
information panels.
"""

import os
import json
from datetime import datetime
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import geopandas as gpd
import openpyxl as xl

from util.filter_by_geometry import filter_by_geometry
from util.get_divisor import get_divisor
from util.click_parser import parse_click
from load_data.geodata import GeoData
from util.filter_vertical import filter_by_vertical
from util.format_helper import format_currency
from util.get_project_root import get_project_root
from load_data.dealer import DealerData
from load_data.dealer_customer import DealerCustomerData
from load_data.key_account import KeyAccountData
from load_data.priority_target import PriorityTargetData
from load_data.region import RegionData
from panel.dealer import DealerPanel
from panel.key_account import KeyAccountPanel
from panel.priority_target import PriorityTargetPanel
from panel.region import RegionPanel
from dialog.glossary_n_credits import dialog_glossary_n_credits


# code by me
# https://github.com/kimiroo/apac-visualizer
# Author: kimiroo (Yongjun Kim)


CONFIG_PATH = 'config.json'
EXCEL_PATH = 'Dataset.xlsx'
GEODATA_MARKER_PATH = get_project_root() / 'geodata' / 'LAST_MODIFIED'


##################
### File Check ###
##################

if not os.path.exists(CONFIG_PATH):
    st.error('Failed to find config file. Check server configuration.')
    st.stop()

if not os.path.exists(EXCEL_PATH):
    st.error('No spreadsheet file has been loaded on the server. Upload spreadsheet file in the management console.')
    st.stop()


##############
### Config ###
##############

# Load config
@st.cache_resource
def load_config(mtime: float) -> dict:
    with open(CONFIG_PATH, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config

mtime_config_float = os.path.getmtime(CONFIG_PATH)
mtime_config_datetime = datetime.fromtimestamp(mtime_config_float)

config: dict = load_config(mtime_config_float)

tier_color_map = {t['name']: t['color'] for t in config['tiers']}
is_customer_color_map = {x['value']: x['color'] for x in config['isCustomer']}


############
### Init ###
############

# Set page to wide mode for the side panel layout
st.set_page_config(
    page_title=config['app']['title'],
    page_icon='assets/plana.png',
    layout='wide'
)

# Load geodata
@st.cache_resource
def load_geodata(mtime: float) -> GeoData:
    """Loads and caches the GeoData instance.

    Returns:
        GeoData: An instance of the GeoData class containing geographic information.
    """
    return GeoData()

mtime_geojson_float = os.path.getmtime(GEODATA_MARKER_PATH)
mtime_geojson_datetime = datetime.fromtimestamp(mtime_geojson_float)

gd = load_geodata(mtime_geojson_float)

# Load Excel data
@st.cache_resource
def load_data(filename: str, config: dict, mtime: float) -> dict:
    """
    Loads Excel, parses sheets, and returns initialized data objects.
    The 'mtime' argument ensures the cache invalidates when the file changes.
    """

    doc = xl.load_workbook(filename, data_only=True, read_only=True)

    try:
        sheet_region = doc[config['source']['sheet']['region']['name']]
        sheet_dealer = doc[config['source']['sheet']['dealer']['name']]
        sheet_dealer_customer = doc[config['source']['sheet']['dealerCustomer']['name']]
        sheet_key_account = doc[config['source']['sheet']['keyAccount']['name']]
        sheet_priority_target = doc[config['source']['sheet']['priorityTarget']['name']]

        # Initialize and load data objects
        data_region = RegionData(config)
        data_dealer = DealerData(config)
        data_dealer_customer = DealerCustomerData(config)
        data_key_account = KeyAccountData(config)
        data_priority_target = PriorityTargetData(config)

        data_region.load(sheet_region)
        data_dealer.load(sheet_dealer)
        data_dealer_customer.load(sheet_dealer_customer)
        data_key_account.load(sheet_key_account)
        data_priority_target.load(sheet_priority_target)

        return {
            'region': data_region,
            'dealer': data_dealer,
            'dealer_customer': data_dealer_customer,
            'key_account': data_key_account,
            'priority_target': data_priority_target
        }

    finally:
        doc.close()

# Get last modified time to trigger cache refresh
mtime_excel_float = os.path.getmtime(EXCEL_PATH)
mtime_excel_datetime = datetime.fromtimestamp(mtime_excel_float)

# This will only run once unless the file or config changes
data = load_data(EXCEL_PATH, config, mtime_excel_float)

data_region: RegionData = data['region']
data_dealer: DealerData = data['dealer']
data_dealer_customer: DealerCustomerData = data['dealer_customer']
data_key_account: KeyAccountData = data['key_account']
data_priority_target: PriorityTargetData = data['priority_target']

panel_dealer = DealerPanel(data_dealer.df, data_dealer_customer.df, config)
panel_key_account = KeyAccountPanel(data_key_account.df, config)
panel_priority_target = PriorityTargetPanel(data_priority_target.df, config)
panel_region = RegionPanel(config)


###################
### Click State ###
###################

# Initialize State
if 'map_click_type' not in st.session_state:
    st.session_state.map_click_type = None

if 'selected_dealer' not in st.session_state:
    st.session_state.selected_dealer = None

if 'selected_key_account' not in st.session_state:
    st.session_state.selected_key_account = None

if 'selected_priority_target' not in st.session_state:
    st.session_state.selected_priority_target = None

if 'selected_region' not in st.session_state:
    st.session_state.selected_region = None

if 'is_nested_view' not in st.session_state:
    st.session_state.is_nested_view = False

if 'nested_selected_data' not in st.session_state:
    st.session_state.nested_selected_data = None

# State updater
def sync_map_click_state(map_data):

    # No click data
    if not map_data or not map_data.get('last_object_clicked'):
        return

    last_tooltip = map_data.get('last_object_clicked_tooltip')
    click_type, obj_name = parse_click(last_tooltip)

    is_same_dealer = (click_type == 'dealer' and st.session_state.get('selected_dealer') == obj_name)
    is_same_priority_target = (click_type == 'priority_target' and st.session_state.get('selected_priority_target') == obj_name)
    is_same_region = (click_type == 'region' and st.session_state.get('selected_region') == obj_name)

    if st.session_state.get('map_click_type') == click_type and (is_same_dealer or is_same_region or is_same_priority_target):
        return

    # Store states to session state
    st.session_state.map_click_type = click_type

    if click_type == 'dealer':
        go_up_panel()
        st.session_state.selected_dealer = obj_name

    elif click_type == 'key_account':
        go_up_panel()
        st.session_state.selected_key_account = obj_name

    elif click_type == 'priority_target':
        go_up_panel()
        st.session_state.selected_priority_target = obj_name

    elif click_type == 'region':
        go_up_panel()
        st.session_state.selected_region = obj_name
        st.rerun()

def go_up_panel():
    st.session_state.is_nested_view = False
    st.session_state.nested_selected_data = None


###############
### Sidebar ###
###############

# Common
st.sidebar.header('Common')

selected_country = st.sidebar.selectbox(
    'Country',
    key='selected_country',
    options=gd.country_list,
    format_func=lambda x: x['name']
)

if st.sidebar.button('Clear selection'):
    st.session_state.map_click_type = None
    st.session_state.selected_dealer = None
    st.session_state.selected_priority_target = None
    st.session_state.selected_region = None
    st.rerun()

st.sidebar.caption("💡 Tip: 'Clear selection' button only clears the region/pin selection on the map.")

# Heatmap
st.sidebar.header('Heatmap')

selected_heatmap_vertical = st.sidebar.selectbox(
    'Vertical',
    key='selected_heatmap_vertical',
    options=['Total'] + config['vertical']
)

st.sidebar.caption("💡 Tip: 'Vertical' filter also applies to the Dealer list in the right info panel.")

heatmap_value_options = [
    {'name': 'Total Market Value', 'value': 'total_market_value'},
    {'name': 'Potential Market Value', 'value': 'potential_market_value'},
    {'name': 'Actual Dealer Revenue', 'value': 'actual_dealer_revenue'},
    {'name': 'Projected Dealer Revenue', 'value': 'projected_dealer_revenue'}
]

# Handle optional options
excluded_heatmap_options = []

if not config['showOptionalData']['projectedRevenue']:
    excluded_heatmap_options.append('projected_dealer_revenue')

heatmap_value_options = [
    opt for opt in heatmap_value_options
    if opt['value'] not in excluded_heatmap_options
]

selected_heatmap_value = st.sidebar.selectbox(
    'Value',
    key='selected_heatmap_value',
    options=heatmap_value_options,
    format_func=lambda x: x['name']
)

st.sidebar.caption("💡 Tip: 'Value' filter doesn't apply to the Dealer list in the right info panel.")

# Pins
st.sidebar.header('Pins')

draw_dealer_pin = st.sidebar.checkbox('Dealers', value=True)
draw_priority_target_pin = st.sidebar.checkbox('Priority Targets', value=True)
draw_key_account_pin = st.sidebar.checkbox('Key Account Plants', value=True)

# Dealer
st.sidebar.header('Dealers')

selected_verticals_dealer = st.sidebar.multiselect(
    'Vertical',
    key='selected_verticals_dealer',
    options=config['vertical'] + ['None'],
    default=config['vertical'] + ['None']
)

selected_tiers_dealer = st.sidebar.multiselect(
    'Tier',
    key='selected_tiers_dealer',
    options=[t['name'] for t in config['tiers']],
    default=[t['name'] for t in config['tiers']]
)

# Priority Targets
st.sidebar.header('Priority Targets')

selected_verticals_priority_target = st.sidebar.multiselect(
    'Vertical',
    key='selected_verticals_priority_target',
    options=config['vertical'] + ['None'],
    default=config['vertical'] + ['None']
)

is_customer_options = [
    {'name': 'Customer', 'value': True},
    {'name': 'Non-Customer', 'value': False}
]

selected_is_customer_priority_target = st.sidebar.multiselect(
    'Customer',
    key='selected_is_customer_priority_target',
    options=is_customer_options,
    default=is_customer_options,
    format_func=lambda x: x['name']
)

# Key Account Plants
st.sidebar.header('Key Account Plants')

unique_key_account_list = [{'name': 'All', 'value': None}] + \
    [
        {'name': val, 'value': val}
        for val in data_key_account.df['account_name'].unique().tolist()
    ]

selected_key_account_name = st.sidebar.selectbox(
    'Key Account Name',
    key='selected_key_account_name',
    options=unique_key_account_list,
    format_func=lambda x: x['name']
)

# View
st.sidebar.header('View')

selected_map_width = st.sidebar.slider(
    'Map Width',
    key='selected_map_width',
    min_value=1,
    max_value=9,
    step=1,
    value=7,
    help='Adjust the width balance between the left and right columns (Total scale of 10).'
)

selected_view_height = st.sidebar.slider(
    'View Height',
    key='selected_view_height',
    min_value=300,
    max_value=2000,
    step=100,
    value=700,
    help='Set the vertical height of the content container in pixels.'
)

st.sidebar.caption("💡 Tip: Adjust 'View Height' to resize the map and info panel.")

# App Memo & Glossary
memo = config.get('appMemo', '')
glossary = config.get('glossary', '')

st.sidebar.divider()

if st.sidebar.button(
    'Glossary & Credits',
    key='btn_glossary'
):
    dialog_glossary_n_credits(glossary)

if memo:
    st.sidebar.write(memo)


##############
### Filter ###
##############

### Get corresponding GeoJSON
geojson, is_level_1 = gd.get_geojson(selected_country['code'])

# Determine the key column based on zoom level (Region vs Country)
# If level 1 (provinces) exists, use NAME_1; otherwise, use GID_0 (Country level)
geo_key_col = 'NAME_1' if is_level_1 else 'GID_0'

### Shallow copy DataFrames
df_filtered_dealer_map_pins = data_dealer.df.copy()
df_filtered_key_account_map_pins = data_key_account.df.copy()
df_filtered_priority_target_map_pins = data_priority_target.df.copy()
df_filtered_dealer_heatmap = data_dealer.df.copy()
df_filtered_priority_target_heatmap = data_priority_target.df.copy()

### Filter country
if geojson is not None and not geojson.empty:
    df_filtered_dealer_map_pins = filter_by_geometry(df_filtered_dealer_map_pins, geojson)
    df_filtered_key_account_map_pins = filter_by_geometry(df_filtered_key_account_map_pins, geojson)
    df_filtered_priority_target_map_pins = filter_by_geometry(df_filtered_priority_target_map_pins, geojson)
    df_filtered_dealer_heatmap = df_filtered_dealer_map_pins.copy()
    df_filtered_priority_target_heatmap = df_filtered_priority_target_map_pins.copy()

### Filter vertical
df_filtered_dealer_map_pins = filter_by_vertical(
    df_filtered_dealer_map_pins,
    selected_verticals_dealer,
    config['vertical']
)
df_filtered_priority_target_map_pins = filter_by_vertical(
    df_filtered_priority_target_map_pins,
    selected_verticals_priority_target,
    config['vertical']
)
if selected_heatmap_vertical != 'Total':
    df_filtered_dealer_heatmap = df_filtered_dealer_heatmap[
        df_filtered_dealer_heatmap[selected_heatmap_vertical]
    ]
    df_filtered_priority_target_heatmap = df_filtered_priority_target_heatmap[
        df_filtered_priority_target_heatmap[selected_heatmap_vertical]
    ]

### Filter tier (Dealer)
df_filtered_dealer_map_pins = df_filtered_dealer_map_pins[df_filtered_dealer_map_pins['tier'].isin(selected_tiers_dealer)]

### Filter customer status (Plant)
selected_is_customer_priority_target_values = [obj['value'] for obj in selected_is_customer_priority_target]
df_filtered_priority_target_map_pins = df_filtered_priority_target_map_pins[df_filtered_priority_target_map_pins['is_customer'].isin(selected_is_customer_priority_target_values)]

### Filter key account plants by account name
if selected_key_account_name['value']:
    df_filtered_key_account_map_pins = df_filtered_key_account_map_pins[
        df_filtered_key_account_map_pins['account_name'] == selected_key_account_name['value']
    ]

### Filter dealer, priority target pin if region is selected
if st.session_state.get('selected_region'):
    # Workaround for 'index_right' cannot be a column name in the frames being joined
    df_filtered_dealer_map_pins = df_filtered_dealer_map_pins.drop(['index_right'], axis=1)
    df_filtered_key_account_map_pins = df_filtered_key_account_map_pins.drop(['index_right'], axis=1)
    df_filtered_priority_target_map_pins = df_filtered_priority_target_map_pins.drop(['index_right'], axis=1)

    df_filtered_dealer_map_pins = filter_by_geometry(df_filtered_dealer_map_pins,
                                                     geojson,
                                                     st.session_state.selected_region)
    df_filtered_key_account_map_pins = filter_by_geometry(df_filtered_key_account_map_pins,
                                                          geojson,
                                                          st.session_state.selected_region)
    df_filtered_priority_target_map_pins = filter_by_geometry(df_filtered_priority_target_map_pins,
                                                              geojson,
                                                              st.session_state.selected_region)


########################
### Number Crunching ###
########################

if geojson is not None and not geojson.empty:

    ### Automatic Actual Dealer Revenue calculation

    # 1. Convert to GeoDataFrame
    gdf_dealer_heatmap = df_filtered_dealer_heatmap.copy()

    # 2. Drop existing region-related columns from dealer data to avoid suffixing
    cols_to_drop = ['NAME_1', 'GID_1', 'GID_0', 'COUNTRY']
    gdf_dealer_heatmap = gdf_dealer_heatmap.drop(columns=[c for c in cols_to_drop if c in gdf_dealer_heatmap.columns])

    # 3. Spatial Join to find which region each dealer belongs to
    # We only need 'NAME_1' and 'geometry' from the region data

    # Drop 'index_right' if it already exists to prevent ValueError during sjoin
    if 'index_right' in gdf_dealer_heatmap.columns:
        gdf_dealer_heatmap = gdf_dealer_heatmap.drop(columns=['index_right'])

    df_joined = gpd.sjoin(
        gdf_dealer_heatmap,
        geojson[[geo_key_col, 'geometry']],
        how='left',
        predicate='within'
    )

    # 4. Calculate statistics per region
    # Group by region name and sum the revenue

    # Dictionary to store results before merging
    stats_list = []

    # A. Calculate Total (All dealers regardless of vertical)
    total_stats = df_joined.groupby(geo_key_col)['actual_revenue'].sum().reset_index()
    total_stats.columns = [geo_key_col, 'Total_actual_dealer_revenue']
    stats_list.append(total_stats)

    # B. Calculate per Vertical
    for vertical in config['vertical']:
        # Filter dealers where this specific vertical is True
        v_mask = df_joined[vertical] == True
        v_stats = df_joined[v_mask].groupby(geo_key_col)['actual_revenue'].sum().reset_index()

        # Rename column to match your target_col format: f'{selected_vertical}_actual_dealer_revenue'
        v_stats.columns = [geo_key_col, f'{vertical}_actual_dealer_revenue']
        stats_list.append(v_stats)

    # 5. Merge results to the region dataframe
    # This adds the calculated revenue as a new column in gdf_region

    # Copy and filter region dataframe
    df_region = data_region.df.copy()
    df_region = df_region[df_region['country'] == str(selected_country['name'])]

    # Merge results
    for stat in stats_list:
        left_key = 'region'

        df_region = df_region.merge(
            stat,
            left_on=left_key,
            right_on=geo_key_col,
            how='left'
        )

        # IMPORTANT: Drop the redundant key column from the right side immediately
        # to prevent 'NAME_1_x' or 'NAME_1_y' conflicts in the next iteration
        if left_key != geo_key_col and geo_key_col in df_region.columns:
            df_region = df_region.drop(columns=[geo_key_col])

    # 6. Fill missing values for regions with no dealers
    revenue_cols = [col for col in df_region.columns if 'actual_dealer_revenue' in col]
    df_region[revenue_cols] = df_region[revenue_cols].fillna(0)

    ### Additional filtering for region panel
    df_dealers_info_panel = df_filtered_dealer_heatmap.copy()
    df_priority_target_info_panel = df_filtered_priority_target_heatmap.copy()

    if st.session_state.get('map_click_type') == 'region':
        df_dealers_info_panel = filter_by_geometry(
            df_dealers_info_panel,
            geojson,
            st.session_state.selected_region
        )
        df_priority_target_info_panel = filter_by_geometry(
            df_priority_target_info_panel,
            geojson,
            st.session_state.selected_region
        )


##############
### Render ###
##############

# Header
st.html(f'''
    <style>
        .title {{
            font-size: 2.75rem;
            font-weight: 700;
        }}
        .info {{
            color: #666;
            font-size: 1rem;
            padding-left: 1rem;
        }}
    </style>
    <span class="title">{config['app']['title']}</span>
    <span class="info">Upload: {mtime_excel_datetime.strftime('%Y-%m-%d %H:%M:%S')}</span>
''')

# Create two columns: Map (Left) and Information (Right)
total_weight = 10
col1_weight = selected_map_width
col2_weight = total_weight - selected_map_width

col1, col2 = st.columns([col1_weight, col2_weight])

with col1:
    # Initialize Folium Map
    m = folium.Map(location=[15, 110], zoom_start=4, tiles='CartoDB positron')

    if geojson is not None and not geojson.empty:

        ### Dynamic scaling
        target_col = f'{selected_heatmap_vertical}_{selected_heatmap_value["value"]}'

        # Get divisor
        max_value = df_region[target_col].max()
        divisor, unit = get_divisor(max_value)

        # Copy dataframe
        df_region_heatmap = df_region.copy()

        # Scale data
        df_region_heatmap[target_col] = df_region_heatmap[target_col] / divisor

        # Generate legend
        dynamic_legend_name = f"{selected_heatmap_value['name']} ({selected_heatmap_vertical}) (Unit: {unit}$)"

        # Draw heatmap
        target_col = f'{selected_heatmap_vertical}_{selected_heatmap_value["value"]}'

        choropleth = folium.Choropleth(
            geo_data=geojson.to_json(),
            data=df_region_heatmap,
            columns=['region', target_col],
            key_on=f'feature.properties.{geo_key_col}',
            fill_color='YlOrRd', # Yellow-Orange-Red
            fill_opacity=0.6,
            line_opacity=0.2,
            legend_name=dynamic_legend_name,
            highlight=True # Hover effect
        ).add_to(m)

        choropleth.geojson.add_child(
            folium.GeoJsonTooltip(fields=[geo_key_col], aliases=['Region:'])
        )

        # Center map to fit region
        bounds = geojson.total_bounds
        sw = [bounds[1], bounds[0]] # South-West (South, West)
        ne = [bounds[3], bounds[2]] # North-East (North, East)

        m.fit_bounds([sw, ne])

    # Draw dealer pins
    if draw_dealer_pin:
        for _, row in df_filtered_dealer_map_pins.iterrows():
            tooltip = f'''<b>Dealer:</b> {row['name']} ({row['id']})<br>
                          Actual Revenue: {format_currency(row['actual_revenue'])}'''

            if config['showOptionalData']['projectedRevenue']:
                tooltip += f'<br>Projected Revenue: {format_currency(row['projected_revenue'])}'

            # Check for NaN coordinates to avoid errors
            if pd.notnull(row['lat']) and pd.notnull(row['long']):
                folium.Marker(
                    location=[row['lat'], row['long']],
                    tooltip=tooltip,
                    icon=folium.Icon(color=tier_color_map.get(row['tier'], 'blue'), icon='briefcase', prefix='fa')
                ).add_to(m)

    # Draw key account pins
    if draw_key_account_pin:
        for _, row in df_filtered_key_account_map_pins.iterrows():
            # Check for NaN coordinates to avoid errors
            if pd.notnull(row['lat']) and pd.notnull(row['long']):
                folium.Marker(
                    location=[row['lat'], row['long']],
                    tooltip=f'''<b>Key Account Plant:</b> {row['name']} ({row['id']})<br>
                                Key Account Name: {row['account_name']}''',
                    icon=folium.Icon(color=config.get('keyAccountColor', 'darkblue'), icon='city', prefix='fa')
                ).add_to(m)

    # Draw priority target pins
    if draw_priority_target_pin:
        for _, row in df_filtered_priority_target_map_pins.iterrows():
            # Check for NaN coordinates to avoid errors
            if pd.notnull(row['lat']) and pd.notnull(row['long']):
                folium.Marker(
                    location=[row['lat'], row['long']],
                    tooltip=f'''<b>Priority Target:</b> {row['name']} ({row['id']})<br>
                                Value: {format_currency(row['value'])}''',
                    icon=folium.Icon(color=is_customer_color_map.get(row['is_customer'], 'red'), icon='industry', prefix='fa')
                ).add_to(m)

    # Display Map and Capture User Interaction
    map_data = st_folium(
        m,
        width='100%',
        height=selected_view_height,
        key=f'_dummy_map_height_{selected_view_height}' # Workaround: Use 'key' to force-refresh
    )

    # Sync click state
    sync_map_click_state(map_data)

with col2:
    # Make column scrollable
    with st.container(height=selected_view_height):

        if st.session_state.is_nested_view:
            if st.button("⬅️ Go Back"):
                go_up_panel()
                st.rerun()

            selected_data = st.session_state.nested_selected_data
            if selected_data['type'] == 'dealer':
                panel_dealer.draw(selected_data['id'])
            else:
                panel_priority_target.draw(selected_data['id'])

        else:
            # Check if a user clicked a region or a point
            if st.session_state.get('map_click_type'):

                if st.session_state.get('map_click_type') == 'dealer':
                    panel_dealer.draw(st.session_state.selected_dealer)

                elif st.session_state.get('map_click_type') == 'key_account':
                    panel_key_account.draw(st.session_state.selected_key_account)

                elif st.session_state.get('map_click_type') == 'priority_target':
                    panel_priority_target.draw(st.session_state.selected_priority_target)

                elif st.session_state.get('map_click_type') == 'region':
                    panel_region.draw(
                        df_region,
                        df_dealers_info_panel,
                        df_priority_target_info_panel,
                        vertical = selected_heatmap_vertical,
                        country = selected_country['name'],
                        region = st.session_state.selected_region
                    )

            else:
                if selected_country['name'] != 'All':
                    panel_region.draw(
                        df_region,
                        df_dealers_info_panel,
                        df_priority_target_info_panel,
                        vertical = selected_heatmap_vertical,
                        country = selected_country['name']
                    )
                else:
                    st.info('Click a pin on the map to see details.')