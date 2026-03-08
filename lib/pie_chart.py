"""Module for generating pie charts using Altair."""

import pandas as pd
import altair as alt

def pie_chart_with_percentage(df: pd.DataFrame, format_string: str) -> alt.Chart | None:
    """Generates a pie chart with percentage labels.

    Args:
        df (pd.DataFrame): The source dataframe containing 'Value' and 'Vertical' columns.
        format_string (str): The format string for tooltips.

    Returns:
        alt.Chart: The generated Altair chart object, or None if total value is 0.
    """

    # Calculate percentage and generate percentage string
    total_value = df['Value'].sum()

    if total_value == 0:
        return None

    df['Percentage'] = (df['Value'] / total_value * 100).round(1)
    df['Percentage String'] = df['Percentage'].astype(str) + '%'

    # Base chart with arcs
    base = alt.Chart(df).encode(
        theta=alt.Theta(field='Value', type='quantitative', stack=True),
        color=alt.Color(field='Vertical', type='nominal'),
        tooltip=[
            alt.Tooltip('Vertical'),
            alt.Tooltip('Value', format=format_string),
            alt.Tooltip('Percentage', format='.1f')
        ]
    )

    # Layer arcs and text labels for percentages
    pie = base.mark_arc(innerRadius=50, outerRadius=100)

    text = base.mark_text(radius=120, size=12, fontWeight='bold').encode(
        text=alt.Text(field='Percentage String', type='nominal')
    )

    # Combine 2 layers
    chart = (pie + text).properties(
        width='container',
        height=300,
    )

    return chart