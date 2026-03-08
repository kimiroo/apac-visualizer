def get_divisor(value):
    divisor = 1
    unit = ''

    if value >= 1_000_000_000:
        divisor = 1_000_000_000
        unit = 'B'
    elif value >= 1_000_000:
        divisor = 1_000_000
        unit = 'M'
    elif value >= 1_000:
        divisor = 1_000
        unit = 'K'

    return divisor, unit