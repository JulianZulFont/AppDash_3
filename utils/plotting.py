# utils/plotting.py - Plotting helpers

import plotly.express as px
from theme import COLORS


def apply_dark_layout(fig, title: str):
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, family="Montserrat")),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["on-background"],
        margin=dict(t=60, b=50, l=50, r=50),
        xaxis=dict(showgrid=False, linecolor=COLORS["outline-variant"]),
        yaxis=dict(gridcolor=COLORS["grid"],
                   linecolor=COLORS["outline-variant"]),
        legend_title_text="",
    )
    return fig
