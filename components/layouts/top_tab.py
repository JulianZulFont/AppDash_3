# components/layouts/top_tab.py

from dash import html, dcc
from styles import STYLES
from theme import COLORS


def layout_top_tab():
    return html.Div(
        [
            html.Div(
                [

                    html.Div(
                        [
                            html.P(
                                "En esta sección se comparan distintas ciudades entre sí para ver cuáles tienen mayor valor de renta actualmente y cuáles han crecido más con el tiempo",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "La gráfica permite identificar rápidamente los mercados más costosos, los que están creciendo más rápido y los que se han mantenido estables",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Los valores mostrados debajo ayudan a entender mejor las diferencias entre ciudades y facilitan encontrar oportunidades o comportamientos atípicos",
                                style=STYLES["p"],
                            ),
                        ],
                        style={"marginBottom": "0.5rem"},
                    ),
                    html.P(
                        "Ranking por renta en la última fecha del dataset. Puedes hacer clic en una barra para ver detalles de esa ciudad",
                        style={
                            "margin": "0 0 0.75rem 0",
                            "color": COLORS["on-surface-variant"]
                        },
                    ),
                    dcc.Graph(
                        id="top-graph", config={"displayModeBar": False}, style={"height": "70vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="top-stats"),
        ]
    )
