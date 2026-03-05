import re

filter_click_type = r'^(?:\s*)(Region|Dealer):'

filter_region = r'(?:\s+)(.+)'
filter_dealer = r'^Dealer: .* \((.*)\)'

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

    elif found[0] == 'Dealer':
        found_id = re.findall(filter_dealer, tooltip_string)
        dealer_id = found_id[0]

        return 'dealer', dealer_id
