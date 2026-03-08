"""Module for calculating number divisors and units."""

def get_divisor(value: float) -> tuple[int, str]:
    """Determines the divisor and unit suffix for large numbers.

    Args:
        value (float): The numeric value to format.

    Returns:
        tuple: A tuple containing (divisor, unit).
            divisor (int): The divisor to scale the value (1, 1000, 1M, 1B).
            unit (str): The unit suffix ('', 'K', 'M', 'B').
    """
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