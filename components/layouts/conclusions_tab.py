from dash import html
from styles import STYLES, COLORS


def layout_conclusions_tab():
    return html.Div(
        [
            html.Div(
                [
                    html.H3("Conclusiones y Hallazgos Relevantes",
                            style=STYLES.get("h3", {})),

                    html.H4("1. Incremento Generalizado de Rentas", style={
                            "marginTop": "1rem", "marginBottom": "0.5rem", "color": COLORS['primary']}),
                    html.P(
                        "Durante el periodo analizado (2015-2024), la gran mayoría de las 100 ciudades más pobladas de EE.UU. experimentaron un aumento continuo en los precios de los alquileres (Índice ZORI). El crecimiento interanual se aceleró de manera notable en el periodo posterior al inicio de la pandemia (2021-2022).",
                        style=STYLES.get("p", {})
                    ),

                    html.H4("2. Disparidad Regional Marcada", style={
                            "marginTop": "1.5rem", "marginBottom": "0.5rem", "color": COLORS['primary']}),
                    html.P(
                        "A nivel geográfico, las costas (especialmente California liderada por San Jose, San Francisco, y el área metropolitana de Nueva York) continúan agrupando a las ciudades de mayor costo. En contraposición, las ciudades del Medio Oeste (Midwest) presentan valores ZORI marcadamente más accesibles a lo largo del tiempo.",
                        style=STYLES.get("p", {})
                    ),

                    html.H4("3. Comportamiento en Crecimiento vs Precio Actual", style={
                            "marginTop": "1.5rem", "marginBottom": "0.5rem", "color": COLORS['primary']}),
                    html.P(
                        "Se observan dinámicas interesantes de convergencia: varias ciudades del Sun Belt y áreas del sur que partían de una base de renta menor registraron crecimientos porcentuales sumamente pronunciados, cerrando la brecha de precios con otras metrópolis históricamente más caras.",
                        style=STYLES.get("p", {})
                    ),

                    html.H4("4. Estacionalidad en Alquileres", style={
                            "marginTop": "1.5rem", "marginBottom": "0.5rem", "color": COLORS['primary']}),
                    html.P(
                        "El análisis temporal (heatmap y serie del tiempo) muestra los clásicos picos estacionales de la demanda de rentas, usualmente ubicados en los meses de verano medio-tardío, con una ligera distensión de precios en los meses de invierno de cada año.",
                        style=STYLES.get("p", {})
                    ),
                ],
                style=STYLES.get("card", {})
            )
        ],
        style={"marginTop": "0.5rem"}
    )
