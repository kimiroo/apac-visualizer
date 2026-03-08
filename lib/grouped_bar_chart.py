import altair as alt

def grouped_bar_chart(df, x_config, y_config, format_string):
    """
    x/y config: tuple (shorthand, title)
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