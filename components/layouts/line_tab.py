# components/layouts/line_tab.py

from dash import html, dcc
from styles import STYLES
from theme import COLORS
from data_loader import OPTIONS


def layout_line_tab():
    return html.Div(
        [
            html.Div(
                [

                    html.Div(
                        [
                            html.P(
                                "Analiza la tendencia del costo de alquiler (Índice ZORI) a lo largo del tiempo para la ciudad seleccionada. Como dimensión secundaria, se contrasta el crecimiento del precio (en miles de USD) frente al ingreso mediano mensual local.",
                                style={**STYLES["p"], "fontSize": "1rem"},
                            ),
                            html.Div(
                                [
                                    html.Label("Seleccionar Ciudad",
                                               style=STYLES["label"]),
                                    dcc.Dropdown(
                                        id="city-dropdown",
                                        options=OPTIONS,
                                        value="New York",
                                        clearable=False, searchable=True,
                                        style={
                                            "color": "black",
                                        },
                                    ),
                                ],
                                style=STYLES["dropdown"],
                            ),
                        ],
                        style={"marginBottom": "0.5rem"},
                    ),
                    dcc.Graph(
                        id="line-graph", config={"displayModeBar": False}, style={"height": "68vh"}),
                    html.Div(
                        id="line-explain", style={"marginTop": "0.75rem", "color": COLORS["on-surface-variant"]}),
                    html.P(
                        "Complementando la tendencia de las rentas observada en el gráfico principal, la siguiente visualización expone qué proporción teórica de los ingresos cubriría un alquiler típico, midiendo el esfuerzo financiero en porcentaje a través del tiempo.",
                        style={
                            **STYLES["p"], "fontSize": "1rem", "marginTop": "2.5rem"
                        },
                    ),
                    html.P(
                        "Se trazó una línea punteada en el 30% para indicar el límite de asequibilidad, de acuerdo con la regla financiera que indica que el gasto en vivienda no debe superar el 30% del ingreso mensual.",
                        style={
                            **STYLES["p"], "fontSize": "1rem",
                        },
                    ),
                    dcc.Graph(
                        id="percentage-line-graph", style={"marginTop": "1rem"}
                    ),
                    html.P(
                        "Si bien el precio de alquiler ha presentado variaciones únicas en cada ciudad (con una notable volatilidad derivada de la pandemia de COVID-19 hacia 2021), al contrastar estos valores con el ingreso local se observa que no en todas partes el esfuerzo financiero aumenta. En algunas ciudades la proporción de renta frente al ingreso se ha contraído, lo que añade una perspectiva matizada a la evolución de los precios del índice ZORI.",
                        style={
                            **STYLES["p"], "fontSize": "1rem", "marginTop": "1.5rem",
                        },
                    ),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="line-stats"),
        ]
    )
