# components/layouts/tables_tab.py

from dash import html, dcc, dash_table
from styles import STYLES
from theme import COLORS
from components.common import tab_block, card, stat_box
from data_loader import df, OPTIONS
import pandas as pd


def layout_tables_tab():
    states = sorted(df["State"].dropna().unique().tolist())
    city_default = df["RegionName"].dropna().unique()[0]

    return tab_block(
        title="Tablas y modelos",
        subtitle="Tablas de resumen, distribución de rentas y un modelo lineal simple (por ciudad). Haz clic en gráficos o cambia filtros para actualizar los estadísticos.",
        children=[
            card(
                html.Div(
                    [
                        html.P(
                            "En esta sección se muestran análisis complementarios del conjunto de datos incluyendo distribuciones, resúmenes estadísticos y un modelo simple de regresión",
                            style=STYLES["p"],
                        ),
                        html.P(
                            "Las tablas permiten ver valores agregados por estado y ciudad mientras que los gráficos ayudan a entender la distribución general de los precios",
                            style=STYLES["p"],
                        ),
                        html.P(
                            "El modelo de regresión muestra la tendencia estimada del comportamiento de la renta en el tiempo y permite evaluar la dirección del crecimiento",
                            style=STYLES["p"],
                        ),
                    ]
                )
            ),
            html.Div(
                [
                    html.Div(
                        [
                            html.Label("Filtrar por Estado (opcional)",
                                       style=STYLES["label"]),
                            dcc.Dropdown(
                                id="tables-state",
                                options=[
                                    {"label": "Todos", "value": "__ALL__"}]
                                + [{"label": s, "value": s} for s in states],
                                value="__ALL__",
                                clearable=False,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Ciudad para modelo",
                                       style=STYLES["label"]),
                            dcc.Dropdown(
                                id="tables-city",
                                options=OPTIONS,
                                value=city_default,
                                clearable=False,
                            ),
                        ],
                        style={"flex": "2"},
                    ),
                ],
                style={"display": "flex", "gap": "1rem", "flexWrap": "wrap"},
            ),

            card(
                html.Div(
                    [
                        html.H3("Distribución de renta (última fecha)",
                                style=STYLES["h3"]),
                        dcc.Graph(
                            id="hist-graph", config={"displayModeBar": False}, style={"height": "45vh"}),
                        html.Div(id="hist-stats",
                                 style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3(
                            "Participación por estado (Top 10 + Otros)", style=STYLES["h3"]),
                        dcc.Graph(
                            id="pie-graph", config={"displayModeBar": False}, style={"height": "45vh"}),
                        html.Div(id="pie-stats",
                                 style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3("Modelo lineal simple por ciudad",
                                style=STYLES["h3"]),
                        html.P(
                            "Ajusta una recta a la renta vs tiempo para estimar tendencia promedio. Es un modelo básico para describir dirección general, no para pronóstico fino.",
                            style=STYLES["p"],
                        ),
                        dcc.Graph(
                            id="reg-graph", config={"displayModeBar": False}, style={"height": "45vh"}),
                        html.Div(id="reg-stats",
                                 style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3("Tabla: resumen por estado (última fecha)",
                                style=STYLES["h3"]),
                        html.Div(id="state-table-wrap"),
                        html.Div(id="state-table-note",
                                 style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3(
                            "Tabla: Top ciudades por crecimiento (desde inicio)", style=STYLES["h3"]),
                        html.Div(id="growth-table-wrap"),
                        html.Div(id="growth-table-note",
                                 style={"marginTop": "0.75rem"}),
                    ]
                )
            ),
        ],
    )
