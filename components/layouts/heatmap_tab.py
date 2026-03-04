# components/layouts/heatmap_tab.py

from dash import html, dcc
from styles import STYLES
from theme import COLORS


def layout_heatmap_tab():
    return html.Div(
        [
            html.Div(
                [

                    html.Div(
                        [
                            html.P(
                                "Este gráfico muestra el comportamiento de la renta por ciudad y por año usando colores para representar el valor",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Los tonos más intensos indican valores más altos y permiten detectar patrones de crecimiento, estabilidad o cambios bruscos a lo largo del tiempo",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Sirve para comparar muchas ciudades al mismo tiempo y ver tendencias generales del mercado de forma rápida",
                                style=STYLES["p"],
                            ),
                        ],
                        style={"marginBottom": "0.5rem"},
                    ),
                    html.P(
                        "Promedio anual de renta (Top 25 ciudades actuales). Haz clic en una celda para ver estadísticos del año",
                        style={"margin": "0 0 0.75rem 0",
                               "color": COLORS["on-surface-variant"]},
                    ),
                    dcc.Graph(
                        id="heatmap-graph", config={"displayModeBar": False}, style={"height": "75vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="heatmap-stats"),
        ]
    )
