"""Module for generating grouped bar charts using Altair."""

import pandas as pd
import altair as alt

def grouped_bar_chart(df: pd.DataFrame, x_config: tuple[str, str], y_config: tuple[str, str], format_string: str) -> alt.Chart:
    """Generates a grouped bar chart.

    Args:
        df (pd.DataFrame): The source dataframe containing the data.
        x_config (tuple): A tuple of (shorthand, title) for the X-axis configuration.
        y_config (tuple): A tuple of (shorthand, title) for the Y-axis configuration.
        format_string (str): The format string for tooltips and axis labels.

    Returns:
        alt.Chart: The generated Altair chart object.
    """
    # Group by Vertical on the X-axis, and color by Type
    chart = alt.Chart(df).mark_bar().encode(
        # Use xOffset for grouped bar alignment
        xOffset='Type:N',
        x=alt.X(x_config[0], title=x_config[1]),
        y=alt.Y(y_config[0], title=y_config[1], axis=alt.Axis(format=format_string)),
        color=alt.Color('Type:N', scale=alt.Scale(range=['#1F77B4', '#D3D3D3'])),
        tooltip=alt.Tooltip(format=format_string)
    ).properties(
        width='container', # Fit to Streamlit container width
        height=300
    ).configure_view(
        stroke='transparent' # Remove outlint
    )

    return chart