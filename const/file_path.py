from pathlib import Path

from util.is_container import IS_CONTAINER

BASE_PATH = Path('/data') if IS_CONTAINER else Path('.')
APP_PATH = Path('.')

PATH_CONFIG = BASE_PATH / 'config.json'
PATH_GEOJSON = BASE_PATH / 'geojson'
PATH_GEOJSON_MARKER = BASE_PATH / 'geojson' / 'LAST_MODIFIED'
PATH_EXCEL = BASE_PATH / 'data.xlsx'
PATH_ICON = BASE_PATH / 'icon.png'
PATH_ICON_DEFAULT = APP_PATH / 'assets' / 'icon.png'