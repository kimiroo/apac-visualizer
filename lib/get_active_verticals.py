class GetActiveVerticalString:
    def __init__(self, config):
        self._config = config

    def get(self, row):
        v_cols = self._config['vertical']
        active = [v for v in v_cols if row[v]]

        return ', '.join(active) if active else 'None'