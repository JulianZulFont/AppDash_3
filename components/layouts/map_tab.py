# components/layouts/map_tab.py

from dash import html, dcc
from styles import STYLES
from theme import COLORS


def layout_map_tab():
    return html.Div(
        [
            html.Div(
                [

                    html.Div(
                        [
                            html.P(
                                "El mapa muestra el valor promedio de la renta por estado usando colores para indicar las diferencias entre regiones",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Al seleccionar un estado se muestran estadísticas adicionales que permiten entender mejor su comportamiento frente al promedio nacional",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Este panel ayuda a identificar zonas más costosas, regiones con mayor crecimiento y diferencias geográficas del mercado inmobiliario",
                                style=STYLES["p"],
                            ),
                        ],
                        style={"marginBottom": "0.5rem"},
                    ),
                    html.P(
                        "Renta promedio por estado (última fecha). Haz clic en un estado para ver el resumen",
                        style={"margin": "0 0 0.75rem 0",
                               "color": COLORS["on-surface-variant"]},
                    ),
                    dcc.Graph(
                        id="map-graph", config={"displayModeBar": False}, style={"height": "78vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="map-stats"),
        ]
    )
