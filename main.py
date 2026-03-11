# main.py - App Entry Point

from dash import html, dcc, Input, Output
from app import app, server
from data_loader import OPTIONS, latest_date, earliest_date
from styles import STYLES
import os

# Import layouts
from components.layouts.line_tab import layout_line_tab
from components.layouts.top_tab import layout_top_tab
from components.layouts.scatter_tab import layout_scatter_tab
from components.layouts.heatmap_tab import layout_heatmap_tab
from components.layouts.map_tab import layout_map_tab
from components.layouts.tables_tab import layout_tables_tab

# Import callbacks to register them
import callbacks.line_callbacks
import callbacks.top_callbacks
import callbacks.scatter_callbacks
import callbacks.heatmap_callbacks
import callbacks.map_callbacks
import callbacks.tables_callbacks

app.layout = html.Div(
    [
        html.H1(
            f"Evolución de Rentas en EE.UU. (Índice ZORI): {earliest_date.year} - {latest_date.year}",
            style=STYLES["title"],
        ),
        html.P(
            f"El ZORI (Zillow Observed Rent Index) refleja el precio típico de los alquileres anunciados en el mercado. "
            f"Este dashboard analiza su evolución entre {earliest_date.year} y {latest_date.year} "
            f"para las 100 ciudades más pobladas de Estados Unidos (valores en miles de USD).",
            style=STYLES["subtitle"],
        ),
        dcc.Tabs(
            id="tabs",
            value="tab-line",
            children=[
                dcc.Tab(label="Serie histórica", value="tab-line"),
                dcc.Tab(label="Top ciudades (última fecha)", value="tab-top"),
                dcc.Tab(label="Precio vs crecimiento", value="tab-scatter"),
                dcc.Tab(label="Heatmap (Ciudad x Año)", value="tab-heatmap"),
                dcc.Tab(label="Mapa por estado", value="tab-map"),
                dcc.Tab(label="Tablas y modelos", value="tab-tables"),
            ],
        ),
        html.Div(id="tab-content", style={"marginTop": "1rem"}),
    ],
    style=STYLES["container"],
)


@app.callback(Output("tab-content", "children"), Input("tabs", "value"))
def render_tab(tab):
    if tab == "tab-line":
        return layout_line_tab()
    if tab == "tab-top":
        return layout_top_tab()
    if tab == "tab-scatter":
        return layout_scatter_tab()
    if tab == "tab-heatmap":
        return layout_heatmap_tab()
    if tab == "tab-map":
        return layout_map_tab()
    if tab == "tab-tables":
        return layout_tables_tab()
    return html.Div("Tab no reconocida", style=STYLES["card"])


if __name__ == "__main__":
    debug = os.getenv("DEBUG") == 'True'
    port = int(os.getenv("PORT", "8050"))
    app.run(debug=debug, port=port)
