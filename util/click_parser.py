"""Module for parsing click events from the Folium map."""

import re

filter_click_type = r'(?:^|>|\s)(Region|Dealer|Key Account Plant|Priority Target):'

filter_region = r'(?:\s+)(.+)'
filter_dealer = r'^Dealer: .* \((.*)\)'
filter_key_account = r'^Key Account Plant: .* \((.*)\)'
filter_priority_target = r'^Priority Target: .* \((.*)\)'

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

    elif found[0] == 'Key Account Plant':
        found_id = re.findall(filter_key_account, tooltip_string)
        key_account_id = found_id[0]

        return 'key_account', key_account_id

    elif found[0] == 'Priority Target':
        found_id = re.findall(filter_priority_target, tooltip_string)
        priority_target_id = found_id[0]

        return 'priority_target', priority_target_id
