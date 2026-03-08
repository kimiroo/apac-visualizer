"""Module for parsing click events from the Folium map."""

import re

filter_click_type = r'(?:^|>|\s)(Region|Dealer):'

filter_region = r'(?:\s+)(.+)'
filter_dealer = r'^Dealer: .* \((.*)\)'

def parse_click(tooltip_string: str) -> tuple[str | None, str | None]:
    """Parses the tooltip string to identify the clicked object type and name.

    Args:
        tooltip_string (str): The tooltip string returned by the map click event.

    Returns:
        tuple: A tuple containing (type, name_or_id).
            Returns (None, None) if parsing fails.
    """

    found = re.findall(filter_click_type, tooltip_string)

    if not found:
        return None, None

    if found[0] == 'Region':
        found_region = [res.strip() for res in re.findall(filter_region, tooltip_string) if res.strip()]
        region = found_region[-1]

        return 'region', region

    elif found[0] == 'Dealer':
        found_id = re.findall(filter_dealer, tooltip_string)
        dealer_id = found_id[0]

        return 'dealer', dealer_id
