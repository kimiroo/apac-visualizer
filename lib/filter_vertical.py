import pandas as pd

def filter_by_vertical(
        df: pd.DataFrame,
        selected_verticals: list,
        vertical_list: list
) -> pd.DataFrame:

    # Check if the selection is empty
    if not selected_verticals:
        return df.iloc[0:0]

    actual_verticals = [i for i in selected_verticals if i != 'None']
    include_none = 'None' in selected_verticals

    # Mask for rows where at least one selected vertical is True
    if actual_verticals:
        vertical_mask = df[actual_verticals].any(axis=1)
    else:
        vertical_mask = pd.Series(False, index=actual_verticals.index)

    # Mask for rows where ALL vertical columns are False (None case)
    if include_none:
        none_mask = ~df[vertical_list].any(axis=1)
        is_in_selected_verticals = vertical_mask | none_mask
    else:
        is_in_selected_verticals = vertical_mask

    # Final filtering
    df = df[is_in_selected_verticals]

    return df