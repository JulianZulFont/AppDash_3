# components/layouts/line_tab.py

from dash import html, dcc
from styles import STYLES
from theme import COLORS


def layout_line_tab():
    return html.Div(
        [
            html.Div(
                [

                    html.Div(
                        [
                            html.P(
                                "Aquí se muestra cómo ha cambiado el valor de la renta en el tiempo según la ciudad que se seleccione. La idea es ver la tendencia, si ha subido, bajado o se ha mantenido estable a lo largo de los años",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Debajo del gráfico aparecen algunos números clave como el valor actual, el cambio acumulado y los valores mínimo y máximo, esto ayuda a entender rápido el comportamiento sin tener que analizar toda la gráfica",
                                style=STYLES["p"],
                            ),
                            html.P(
                                "Este panel sirve principalmente para ver la evolución del mercado y detectar ciudades con crecimiento sostenido o cambios importantes",
                                style=STYLES["p"],
                            ),
                        ],
                        style={"marginBottom": "0.5rem"},
                    ),
                    dcc.Graph(
                        id="line-graph", config={"displayModeBar": False}, style={"height": "68vh"}),
                    html.Div(
                        id="line-explain", style={"marginTop": "0.75rem", "color": COLORS["on-surface-variant"]}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="line-stats"),
        ]
    )
