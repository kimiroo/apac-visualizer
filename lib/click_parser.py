import re

filter_click_type = r'^(?:\s*)(Region|Partner):'

filter_region = r'(?:\s+)(.+)'
filter_partner = r'^Partner: .* \((.*)\)Revenue:'
filter_plant = r'^Plant: (.*)$'

def parse_click(tooltip_string):
    """
    Returns type, name(or ID)
    """

    found = re.findall(filter_click_type, tooltip_string)

    if not found:
        return None, None

    if found[0] == 'Region':
        found_region = [res.strip() for res in re.findall(filter_region, tooltip_string) if res.strip()]
        region = found_region[-1]

        return 'region', region

    elif found[0] == 'Partner':
        found_id = re.findall(filter_partner, tooltip_string)
        partner_id = found_id[0]

        return 'partner', partner_id
