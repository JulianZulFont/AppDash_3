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
                                "Analiza la relación entre el costo de la renta y el ingreso mediano mensual. Esta comparativa permite visualizar si el poder adquisitivo local mantiene el ritmo del mercado inmobiliario o si la brecha de asequibilidad se está expandiendo.",
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
                        "El gráfico de porcentaje muestra el esfuerzo financiero requerido, midiendo qué proporción del ingreso se destina al alquiler. Un valor creciente indica una mayor presión sobre el presupuesto familiar.",
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
                        "En algunas ciudades se evidencia un comportamiento en el que el porcentaje que constituye la renta en relación ingreso disminuye hasta 2021, pero luego de este año aumenta significativamente. Esto se puede deber a factores como la pandemia de COVID-19. Por otro lado, se observan ciudades en las que el porcentaje de renta sobre ingreso tiende a la baja, desmintiendo el ideal de que, de manera generalizada, las rentas han ido subiendo de manera constante en todas las ciudades a comparación del ingreso.",
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
