# components/layouts/scatter_tab.py

from dash import html, dcc
from styles import STYLES
from theme import COLORS


def layout_scatter_tab():
    return html.Div(
        [
            html.Div(
                [

                    html.Div(
                        [
                            html.P(
                                "Aquí se relaciona el precio actual de la renta con el crecimiento que ha tenido cada ciudad en el tiempo",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Cada punto representa una ciudad y permite ver qué mercados tienen precios altos, cuáles están creciendo rápido y cuáles muestran menor dinamismo",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Este análisis ayuda a identificar ciudades con alto potencial de crecimiento, mercados consolidados o zonas con menor valorización",
                                style=STYLES["p"],
                            ),
                        ],
                        style={"marginBottom": "0.5rem"},
                    ),
                    html.P(
                        "Haz clic en un punto para ver el resumen. Líneas guía = medianas (dividen en 4 cuadrantes)",
                        style={"margin": "0 0 0.75rem 0",
                               "color": COLORS["on-surface-variant"]},
                    ),
                    dcc.Graph(
                        id="scatter-graph", config={"displayModeBar": False}, style={"height": "70vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="scatter-stats"),
        ]
    )
