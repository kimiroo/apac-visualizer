def format_currency(value, symbol='USD'):
    """Safe currency formatting for integers, floats, and nulls."""
    try:
        return f"{float(value):,.2f} {symbol}"
    except (ValueError, TypeError):
        return value

def format_number(value, prefix='', postfix=''):
    """Safe number formatting for integers, floats, and nulls."""
    try:
        return f"{prefix}{float(value):,.2f}{postfix}"
    except (ValueError, TypeError):
        return value