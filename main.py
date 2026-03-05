import re
import json

import yaml
import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import openpyxl as xl
import geopandas as gpd

from lib.click_parser import parse_click
from lib.geodata import GeoData, filter_by_geometry

##############
### Config ###
##############

# Load config
with open('config.yaml', 'r', encoding='utf-8') as f:
    config = yaml.full_load(f.read())

tier_color_map = {t['name']: t['color'] for t in config['tiers']}


############
### Init ###
############

# Set page to wide mode for the side panel layout
st.set_page_config(
    page_title=config['app']['title'],
    page_icon=config['app']['favicon'],
    layout='wide'
)
st.title(config['app']['title'])

# Load geodata
gd = GeoData()

# Load Excel data
doc = xl.open(config['source']['filename'])
sheet_region = doc[config['source']['sheet']['region']['name']]
sheet_partner = doc[config['source']['sheet']['partner']['name']]

partner_list = []

# Load partner data
headers_partner_sheet = {cell.value.strip(): i for i, cell in enumerate(sheet_partner[1])}

for partner in sheet_partner.iter_rows(config['source']['sheet']['partner']['rowStart']):
    # Fixed data columns (0 to 10)
    row_data = [partner[i].value for i in range(11)]

    # Append boolean values for vertical columns dynamically
    for vertical in config['vertical']:
        row_data.append(
            bool(partner[headers_partner_sheet[vertical]].value)
        )

    partner_list.append(tuple(row_data))

# Dynamically set extra columns
columns_partner = [
    'area', 'country', 'sales_org',
    'id', 'name', 'tier', 'profile',
    'location', 'lat', 'long',
    'revenue'
]

for vertical in config['vertical']:
    columns_partner.append(vertical)

# Convert to Pandas DataFrame
df_partner = pd.DataFrame(partner_list, columns=columns_partner)


###############
### Sidebar ###
###############

# Add filters
st.sidebar.header('Filters')

selected_country = st.sidebar.selectbox(
    'Country',
    options=gd.country_list,
    format_func=lambda x: x['name']
)

selected_verticals = st.sidebar.multiselect(
    'Vertical',
    options=config['vertical'] + ['None'],
    default=config['vertical'] + ['None']
)

selected_tiers = st.sidebar.multiselect(
    'Tier',
    options=[t['name'] for t in config['tiers']],
    default=[t['name'] for t in config['tiers']]
)

column_ratio_options = [
    {'name': '7:3', 'value': [7, 3]},
    {'name': '5:5', 'value': [5, 5]},
    {'name': '3:7', 'value': [3, 7]}
]

# View
st.sidebar.header('View')

selected_column_ratio = st.sidebar.selectbox(
    'Split Ratio',
    options=column_ratio_options,
    format_func=lambda x: x['name']
)


##############
### Filter ###
##############

### Get corresponding GeoJSON
geojson, is_level_1 = gd.get_geojson(selected_country['code'])

### Shallow copy DataFrames
df_filtered_partner = df_partner.copy()

### Filter country
if geojson is not None and not geojson.empty:
    df_filtered_partner = filter_by_geometry(df_filtered_partner, geojson)

### Filter vertical
actual_verticals = [i for i in selected_verticals if i != 'None']
include_none = 'None' in selected_verticals

# Mask for rows where at least one selected vertical is True
if actual_verticals:
    vertical_mask = df_filtered_partner[actual_verticals].any(axis=1)
else:
    vertical_mask = pd.Series(False, index=df_filtered_partner.index)

# Mask for rows where ALL vertical columns are False (None case)
if include_none:
    all_verticals = config['vertical']
    none_mask = ~df_filtered_partner[all_verticals].any(axis=1)
    is_in_selected_verticals = vertical_mask | none_mask
else:
    is_in_selected_verticals = vertical_mask

# Final filtering
df_filtered_partner = df_filtered_partner[is_in_selected_verticals]

### Filter tier
df_filtered_partner = df_filtered_partner[(df_filtered_partner['tier'].isin(selected_tiers))]


##############
### Render ###
##############

# Create two columns: Map (Left) and Information (Right)
col1, col2 = st.columns(selected_column_ratio['value'])

with col1:
    # 2. Initialize Folium Map
    m = folium.Map(location=[15, 110], zoom_start=4, tiles='CartoDB positron')

    if geojson is not None and not geojson.empty:
        folium.GeoJson(
            data=geojson.to_json(),
            style_function=lambda x: {
                'fillColor': '#ebf0f7',
                'color': '#3186cc',
                'weight': 1,
                'fillOpacity': 0.5
            },
            tooltip=folium.GeoJsonTooltip(fields=['NAME_1' if is_level_1 else 'GID_0'], aliases=['Region:'])
        ).add_to(m)

        bounds = geojson.total_bounds
        sw = [bounds[1], bounds[0]] # South-West (South, West)
        ne = [bounds[3], bounds[2]] # North-East (North, East)

        m.fit_bounds([sw, ne])

    # Draw partner pins
    for _, row in df_filtered_partner.iterrows():
        # Check for NaN coordinates to avoid errors
        if pd.notnull(row['lat']) and pd.notnull(row['long']):
            folium.Marker(
                location=[row['lat'], row['long']],
                tooltip=f'<b>Partner:</b> {row['name']} ({row['id']})<br>Revenue: {row['revenue']:,.2f} {config['data']['currency']}',
                icon=folium.Icon(color=tier_color_map.get(row['tier'], 'blue'), icon='briefcase', prefix='fa')
            ).add_to(m)

    # 4. Display Map and Capture User Interaction
    map_data = st_folium(m, width='100%', height=1000)

with col2:
    st.subheader('Selected Details')
    # Check if a user clicked a region or a point
    if map_data.get('last_object_clicked'):

        last_tooltip = map_data.get('last_object_clicked_tooltip')

        obj_type, obj_name = parse_click(last_tooltip)

        st.write(f'You clicked on: {obj_name} ({obj_type})')
        # You can filter your Pandas DataFrame here and show charts
    else:
        st.info('Click a region or a pin on the map to see details.')