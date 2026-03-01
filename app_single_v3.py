"""
Dash app (single-file) - Rent Index Dashboard (ZORI city dataset)

What you get (tabs):
1) Línea histórica por ciudad (con selector)
2) Top N ciudades más caras (última fecha disponible)
3) Scatter: Renta actual vs Crecimiento acumulado (cuadrantes)
4) Heatmap: Ciudad vs Año (Top N ciudades)
5) Mapa USA por estado (promedio de renta, última fecha)

Dataset esperado: city-zori-long.csv en el mismo folder que este archivo
Columnas esperadas: RegionName, State, SizeRank, Date, RentIndex, (opcional: Metro, CountyName)
RentIndex se asume en "miles de USD" (como dijiste). Si no, solo cambia etiquetas.
"""

from dash import Dash, html, dcc, Input, Output, dash_table
import plotly.express as px
import pandas as pd
import numpy as np
from dotenv import load_dotenv
import os

# -----------------------------
# Tema / estilos (reemplaza styles.py + theme.py)
# -----------------------------
COLORS = {
    "primary": "rgb(157, 203, 252)",
    "background": "rgb(16, 20, 24)",
    "on-background": "rgb(224, 226, 232)",
    "on-surface-variant": "rgb(194, 199, 207)",
    "outline-variant": "rgb(66, 71, 78)",
    "card": "rgba(255, 255, 255, 0.05)",
    "grid": "rgba(255, 255, 255, 0.06)",
}

STYLES = {
    "container": {
        "backgroundColor": COLORS["background"],
        "color": COLORS["on-background"],
        "minHeight": "100vh",
        "padding": "2rem",
        "fontFamily": "'Inter', sans-serif",
    },
    "card": {
        "backgroundColor": COLORS["card"],
        "backdropFilter": "blur(10px)",
        "borderRadius": "16px",
        "padding": "1.25rem",
        "border": "1px solid rgba(255, 255, 255, 0.1)",
        "boxShadow": "0 8px 32px 0 rgba(0, 0, 0, 0.37)",
        "marginBottom": "1.25rem",
    },
    "title": {
        "fontFamily": "Montserrat",
        "fontWeight": "800",
        "color": COLORS["primary"],
        "marginBottom": "0.25rem",
        "fontSize": "2.2rem",
        "letterSpacing": "-1px",
    },
    "subtitle": {
        "color": COLORS["on-surface-variant"],
        "marginBottom": "1.25rem",
        "fontSize": "1.05rem",
        "fontWeight": "400",
        "maxWidth": "980px",
    },
    "label": {
        "color": COLORS["on-background"],
        "marginBottom": "0.6rem",
        "display": "block",
        "fontWeight": "600",
        "fontSize": "0.85rem",
        "textTransform": "uppercase",
        "letterSpacing": "1px",
    },
    "h3": {
    "margin": "0 0 10px 0",
    "fontFamily": "Montserrat",
    "fontSize": "18px",
    "fontWeight": "700",
    },
    "p": {
    "margin": "0 0 12px 0",
    "opacity": 0.9,
    "lineHeight": "1.5",
    "fontSize": "14px",
    },
    "note":{
    "marginTop": "8px",
    "fontSize": "12px",
    "opacity": 0.8,
    "lineHeight": "1.4"
    }
}

FONT_URL = "https://fonts.googleapis.com/css2?family=Inter:wght@400;500&family=Montserrat:wght@700;800&display=swap"

# -----------------------------
# Carga de datos
# -----------------------------
def resolve_data_path(filename: str) -> str:
    """
    1) Busca el archivo al lado de este script
    2) Si no existe, intenta en /mnt/data (útil en notebooks / sandbox)
    3) Permite override con env DATA_PATH
    """
    env_path = os.getenv("DATA_PATH")
    if env_path and os.path.exists(env_path):
        return env_path

    here = os.path.dirname(os.path.abspath(__file__))
    local = os.path.join(here, filename)
    if os.path.exists(local):
        return local

    sandbox = os.path.join("/mnt/data", filename)
    if os.path.exists(sandbox):
        return sandbox

    raise FileNotFoundError(
        f"No encontré {filename}. Ponlo junto a este .py o define DATA_PATH en .env"
    )

DATA_FILE = resolve_data_path("city-zori-long.csv")
df = pd.read_csv(DATA_FILE)

# Normalización mínima
df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
df = df.dropna(subset=["Date", "RegionName", "State", "RentIndex"]).copy()

# Top 100 por SizeRank (como tu back.py)
if "SizeRank" in df.columns:
    df = df[df["SizeRank"] < 100].copy()

# Fecha en español (para hover)
MESES_ES = {1: "Ene", 2: "Feb", 3: "Mar", 4: "Abr", 5: "May", 6: "Jun",
            7: "Jul", 8: "Ago", 9: "Sep", 10: "Oct", 11: "Nov", 12: "Dic"}
df["Fecha_ES"] = df["Date"].dt.month.map(MESES_ES) + " " + df["Date"].dt.year.astype(str)
df["Year"] = df["Date"].dt.year

# Opciones dropdown (City, State)
city_options = (
    df[["RegionName", "State"]]
    .drop_duplicates()
    .sort_values(["RegionName", "State"])
)
OPTIONS = [
    {"label": f"{r.RegionName}, {r.State}", "value": r.RegionName}
    for r in city_options.itertuples(index=False)
]

# Pre-cálculos para últimas métricas
latest_date = df["Date"].max()
df_latest = df[df["Date"] == latest_date].copy()

# Primera fecha por ciudad (para crecimiento)
first_by_city = (
    df.sort_values("Date")
      .groupby("RegionName", as_index=False)
      .first()[["RegionName", "Date", "RentIndex"]]
      .rename(columns={"RentIndex": "RentIndex_first", "Date": "Date_first"})
)

last_by_city = (
    df.sort_values("Date")
      .groupby("RegionName", as_index=False)
      .last()[["RegionName", "Date", "RentIndex", "State"]]
      .rename(columns={"RentIndex": "RentIndex_last", "Date": "Date_last"})
)

growth = last_by_city.merge(first_by_city, on="RegionName", how="left")
growth["Growth_abs"] = growth["RentIndex_last"] - growth["RentIndex_first"]
growth["Growth_pct"] = (growth["Growth_abs"] / growth["RentIndex_first"]) * 100.0
growth["Label"] = growth["RegionName"] + ", " + growth["State"]

# Promedio por estado (última fecha)
state_latest = (
    df_latest.groupby("State", as_index=False)
             .agg(RentIndex=("RentIndex", "mean"))
)


# -----------------------------
# App
# -----------------------------
app = Dash(__name__, external_stylesheets=[FONT_URL], suppress_callback_exceptions=True)
server = app.server  # para despliegue

def stat_card(title, rows, note=None):
    """rows: list of (label, value)"""
    return html.Div(
        [
            html.Div(title, style={"fontWeight": "700", "marginBottom": "0.6rem"}),
            html.Table(
                [html.Tbody([html.Tr([html.Td(k, style={"paddingRight": "1rem", "color": COLORS["on-surface-variant"]}),
                                      html.Td(v)]) for k, v in rows])],
                style={"width": "100%", "borderCollapse": "collapse", "fontSize": "0.95rem"},
            ),
            html.Div(note, style={"marginTop": "0.6rem", "color": COLORS["on-surface-variant"], "fontSize": "0.9rem"})
            if note else None,
        ],
        style={
            **STYLES["card"],
            "marginTop": "1rem",
            "padding": "1rem 1.1rem",
        },
    )



def tab_block(title: str, subtitle: str, children):
    """Bloque estándar para cada pestaña: encabezado + contenido.
    children: lista de componentes Dash
    """
    return html.Div(
        [
            html.Div(
                [
                    html.H2(title, style={"margin": "0 0 0.25rem 0", "fontFamily": "'Montserrat', sans-serif"}),
                    html.P(subtitle, style={"margin": "0 0 1rem 0", "color": COLORS["on-surface-variant"]}),
                ],
                style={"marginBottom": "0.5rem"},
            ),
            *children,
        ]
    )

def card(children, style=None):
    base_style = {
        "backgroundColor": "#1e1e1e",
        "padding": "20px",
        "borderRadius": "12px",
        "marginBottom": "20px",
        "boxShadow": "0 2px 10px rgba(0,0,0,0.2)"
    }
    
    if style:
        base_style.update(style)
    
    return html.Div(children, style=base_style)      


def stat_box(title, stats, columns=2):
    """
    stats puede ser:
    - dict: {"Etiqueta": "Valor"}
    - list: [("Etiqueta","Valor"), ...]  o [{"label":..,"value":..}, ...]
    """
    # Normalizar stats a lista de pares (k,v)
    pairs = []

    if isinstance(stats, dict):
        pairs = list(stats.items())

    elif isinstance(stats, list):
        # Caso 1: [("A","B"), ("C","D")]
        if len(stats) > 0 and isinstance(stats[0], (list, tuple)) and len(stats[0]) == 2:
            pairs = [(str(k), v) for k, v in stats]
        # Caso 2: [{"label":"A","value":"B"}, ...]
        elif len(stats) > 0 and isinstance(stats[0], dict):
            for d in stats:
                k = d.get("label") or d.get("k") or d.get("name") or "Dato"
                v = d.get("value") or d.get("v") or d.get("val") or ""
                pairs.append((str(k), v))
        else:
            # Caso 3: lista simple [1,2,3] -> etiqueta genérica
            pairs = [(f"Dato {i+1}", v) for i, v in enumerate(stats)]

    else:
        # Si llega algo raro, lo mostramos como texto
        pairs = [("Valor", stats)]

    items = []
    for k, v in pairs:
        items.append(
            html.Div(
                [
                    html.Div(k, style=STYLES.get("stat_label", {"fontSize": "12px", "opacity": 0.75})),
                    html.Div(str(v), style=STYLES.get("stat_value", {"fontSize": "18px", "fontWeight": "700"})),
                ],
                style={"padding": "8px 10px"}
            )
        )

    grid_style = {
        "display": "grid",
        "gridTemplateColumns": f"repeat({columns}, minmax(0, 1fr))",
        "gap": "6px",
        "marginTop": "10px"
    }

    return card(
        [
            html.Div(title, style=STYLES.get("h3", {"fontSize": "16px", "fontWeight": "700"})),
            html.Div(items, style=grid_style)
        ],
        style=STYLES.get("stat_card", {})
    )

def fmt_k(x):
    try:
        return f"{float(x):,.2f}k"
    except Exception:
        return "—"

def fmt_pct(x):
    try:
        return f"{float(x):,.1f}%"
    except Exception:
        return "—"

def apply_dark_layout(fig, title: str):
    fig.update_layout(
        title=dict(text=title, font=dict(size=20, family="Montserrat")),
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["on-background"],
        margin=dict(t=60, b=50, l=50, r=50),
        xaxis=dict(showgrid=False, linecolor=COLORS["outline-variant"]),
        yaxis=dict(gridcolor=COLORS["grid"], linecolor=COLORS["outline-variant"]),
        legend_title_text="",
    )
    return fig

# -------- Layout helpers (tabs) --------
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
                    dcc.Graph(id="line-graph", config={"displayModeBar": False}, style={"height": "68vh"}),
                    html.Div(id="line-explain", style={"marginTop": "0.75rem", "color": COLORS["on-surface-variant"]}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="line-stats"),
        ]
    )

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
                        style={"margin": "0 0 0.75rem 0", "color": COLORS["on-surface-variant"]},
                    ),
                    dcc.Graph(id="top-graph", config={"displayModeBar": False}, style={"height": "70vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="top-stats"),
        ]
    )

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
                        style={"margin": "0 0 0.75rem 0", "color": COLORS["on-surface-variant"]},
                    ),
                    dcc.Graph(id="scatter-graph", config={"displayModeBar": False}, style={"height": "70vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="scatter-stats"),
        ]
    )

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
                        style={"margin": "0 0 0.75rem 0", "color": COLORS["on-surface-variant"]},
                    ),
                    dcc.Graph(id="heatmap-graph", config={"displayModeBar": False}, style={"height": "75vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="heatmap-stats"),
        ]
    )

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
                        style={"margin": "0 0 0.75rem 0", "color": COLORS["on-surface-variant"]},
                    ),
                    dcc.Graph(id="map-graph", config={"displayModeBar": False}, style={"height": "78vh"}),
                ],
                style=STYLES["card"],
            ),
            html.Div(id="map-stats"),
        ]
    )

app.layout = html.Div(
    [
        html.H1("Rentas (ZORI) - Dashboard", style=STYLES["title"]),
        html.P(
            f"Datos por ciudad (Top 100 SizeRank). Última fecha disponible: {latest_date.date()} "
            f"• RentIndex mostrado como miles de USD",
            style=STYLES["subtitle"],
        ),

        html.Div(
            [
                html.Label("Seleccionar Ciudad (para serie histórica)", style=STYLES["label"]),
                dcc.Dropdown(
                    id="city-dropdown",
                    options=OPTIONS,
                    value=OPTIONS[0]["value"] if OPTIONS else None,
                    clearable=False,
                    searchable=True,
                ),
            ],
            style={"maxWidth": "520px", "marginBottom": "1rem"},
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

# -----------------------------
# Tab switch (solo estructura)
# -----------------------------
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

# -----------------------------
# 1) Serie histórica
# -----------------------------
@app.callback(Output("line-graph", "figure"), Input("city-dropdown", "value"))
def update_line_fig(selected_city):
    dff = df[df["RegionName"] == selected_city].copy()
    fig = px.line(
        dff,
        x="Date",
        y="RentIndex",
        hover_data=["Fecha_ES"],
        labels={"RentIndex": "Renta (miles USD)", "Date": "Fecha"},
    )
    fig.update_traces(
        line=dict(width=3, color=COLORS["primary"]),
        hovertemplate="<b>%{customdata[0]}</b><br>Renta: %{y:,.2f}k<extra></extra>",
    )
    fig = apply_dark_layout(fig, f"Índice de Renta Histórico: {selected_city}")
    fig.update_layout(hovermode="x unified")
    return fig

@app.callback(
    Output("line-stats", "children"),
    Output("line-explain", "children"),
    Input("city-dropdown", "value"),
)
def update_line_stats(selected_city):
    dff = df[df["RegionName"] == selected_city].sort_values("Date").copy()
    if dff.empty:
        return stat_card("Resumen", [("Ciudad", "—")]), "No hay datos para esta ciudad"

    first = dff.iloc[0]
    last = dff.iloc[-1]
    v_first = float(first["RentIndex"])
    v_last = float(last["RentIndex"])
    abs_change = v_last - v_first
    pct_change = (abs_change / v_first) * 100 if v_first else float("nan")
    v_min = float(dff["RentIndex"].min())
    v_max = float(dff["RentIndex"].max())

    # YoY aproximado (mismo mes del año anterior)
    yoy_txt = "—"
    try:
        last_date = pd.to_datetime(last["Date"])
        prev = dff[dff["Date"] <= (last_date - pd.DateOffset(years=1))].tail(1)
        if not prev.empty:
            v_prev = float(prev.iloc[0]["RentIndex"])
            yoy = ((v_last - v_prev) / v_prev) * 100 if v_prev else float("nan")
            yoy_txt = fmt_pct(yoy)
    except Exception:
        pass

    card = stat_card(
        "Estadísticos (ciudad seleccionada)",
        [
            ("Ciudad", f"{selected_city}" ),
            ("Primera fecha", str(pd.to_datetime(first["Date"]).date())),
            ("Última fecha", str(pd.to_datetime(last["Date"]).date())),
            ("Renta inicial", fmt_k(v_first)),
            ("Renta actual", fmt_k(v_last)),
            ("Cambio acumulado", f"{fmt_k(abs_change)} ({fmt_pct(pct_change)})"),
            ("Mín / Máx", f"{fmt_k(v_min)} / {fmt_k(v_max)}"),
            ("YoY (aprox)", yoy_txt),
        ],
        note="Lectura sugerida: mira el nivel (renta actual) y la pendiente (ritmo de crecimiento). Un cambio YoY alto sugiere aceleración reciente.",
    )

    explain = (
        f"En {selected_city}, la renta pasó de {fmt_k(v_first)} a {fmt_k(v_last)} entre "
        f"{pd.to_datetime(first['Date']).date()} y {pd.to_datetime(last['Date']).date()}. "
        f"Eso equivale a {fmt_pct(pct_change)} de crecimiento acumulado."
    )
    return card, explain

# -----------------------------
# 2) Top ciudades (última fecha)
# -----------------------------
@app.callback(Output("top-graph", "figure"), Input("tabs", "value"))
def update_top_fig(_):
    topn = df_latest.sort_values("RentIndex", ascending=False).head(15).copy()
    topn["Label"] = topn["RegionName"] + ", " + topn["State"]

    fig = px.bar(
        topn.sort_values("RentIndex"),
        x="RentIndex",
        y="Label",
        orientation="h",
        labels={"RentIndex": "Renta (miles USD)", "Label": "Ciudad"},
    )
    fig.update_traces(
        marker_line_width=0,
        hovertemplate="<b>%{y}</b><br>Renta: %{x:,.2f}k<extra></extra>",
    )
    fig = apply_dark_layout(fig, "Top 15 ciudades más caras (última fecha)")
    fig.update_layout(hovermode="y")
    return fig

@app.callback(
    Output("top-stats", "children"),
    Input("top-graph", "clickData"),
)
def update_top_stats(clickData):
    topn = df_latest.sort_values("RentIndex", ascending=False).head(15).copy()
    topn["Label"] = topn["RegionName"] + ", " + topn["State"]

    if clickData and clickData.get("points"):
        label = clickData["points"][0].get("y")
        row = topn[topn["Label"] == label].head(1)
    else:
        row = topn.head(1)

    if row.empty:
        return stat_card("Resumen", [("Selección", "—")])

    r = row.iloc[0]
    city = r["RegionName"]
    state = r["State"]
    rent = float(r["RentIndex"])

    # crecimiento para esa ciudad
    g = growth[growth["RegionName"] == city].head(1)
    g_pct = float(g.iloc[0]["Growth_pct"]) if not g.empty else float("nan")
    g_abs = float(g.iloc[0]["Growth_abs"]) if not g.empty else float("nan")

    return stat_card(
        "Detalle (ciudad seleccionada)",
        [
            ("Ciudad", f"{city}, {state}"),
            ("Fecha", str(latest_date.date())),
            ("Renta actual", fmt_k(rent)),
            ("Crecimiento acumulado", f"{fmt_k(g_abs)} ({fmt_pct(g_pct)})"),
        ],
        note="Tip: este ranking muestra nivel de renta, no necesariamente crecimiento. Usa el scatter para ver 'caro vs creciendo'.",
    )

# -----------------------------
# 3) Scatter: precio vs crecimiento
# -----------------------------
@app.callback(Output("scatter-graph", "figure"), Input("tabs", "value"))
def update_scatter_fig(_):
    g = growth.dropna(subset=["RentIndex_last", "Growth_pct"]).copy()

    fig = px.scatter(
        g,
        x="RentIndex_last",
        y="Growth_pct",
        hover_name="Label",
        labels={
            "RentIndex_last": "Renta actual (miles USD)",
            "Growth_pct": "Crecimiento acumulado (%)",
        },
    )
    fig.update_traces(
        marker=dict(size=10, opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>%{hovertext}</b><br>Renta: %{x:,.2f}k<br>Crecimiento: %{y:,.1f}%<extra></extra>",
    )
    fig = apply_dark_layout(fig, "Precio vs crecimiento (primera fecha → última fecha)")
    fig.update_layout(hovermode="closest")

    x_med = float(g["RentIndex_last"].median())
    y_med = float(g["Growth_pct"].median())
    fig.add_vline(x=x_med, line_width=1)
    fig.add_hline(y=y_med, line_width=1)
    return fig

@app.callback(Output("scatter-stats", "children"), Input("scatter-graph", "clickData"))
def update_scatter_stats(clickData):
    g = growth.dropna(subset=["RentIndex_last", "Growth_pct"]).copy()
    x_med = float(g["RentIndex_last"].median())
    y_med = float(g["Growth_pct"].median())

    if clickData and clickData.get("points"):
        label = clickData["points"][0].get("hovertext") or clickData["points"][0].get("text")
        row = g[g["Label"] == label].head(1)
    else:
        row = pd.DataFrame()

    if row.empty:
        return stat_card(
            "Cómo leer este gráfico",
            [
                ("Arriba-derecha", "Caro y creciendo (premium dinámico)" ),
                ("Abajo-derecha", "Caro pero maduro" ),
                ("Arriba-izquierda", "Oportunidad (más barato y creciendo)" ),
                ("Abajo-izquierda", "Más barato y lento" ),
                ("Cortes", f"Medianas: renta={fmt_k(x_med)} • crecimiento={fmt_pct(y_med)}" ),
            ],
            note="Haz clic en un punto para ver el detalle de una ciudad.",
        )

    r = row.iloc[0]
    quadrant = (
        "Arriba-derecha" if (r["RentIndex_last"] >= x_med and r["Growth_pct"] >= y_med)
        else "Abajo-derecha" if (r["RentIndex_last"] >= x_med and r["Growth_pct"] < y_med)
        else "Arriba-izquierda" if (r["RentIndex_last"] < x_med and r["Growth_pct"] >= y_med)
        else "Abajo-izquierda"
    )

    return stat_card(
        "Detalle (ciudad seleccionada)",
        [
            ("Ciudad", r["Label"]),
            ("Renta actual", fmt_k(r["RentIndex_last"])),
            ("Crecimiento acumulado", fmt_pct(r["Growth_pct"])),
            ("Cambio absoluto", fmt_k(r["Growth_abs"])),
            ("Cuadrante", quadrant),
            ("Primera fecha", str(pd.to_datetime(r["Date_first"]).date())),
            ("Última fecha", str(pd.to_datetime(r["Date_last"]).date())),
        ],
        note="Interpretación: combina nivel (renta) y dinámica (crecimiento). Un mercado 'oportunidad' suele estar arriba-izquierda.",
    )

# -----------------------------
# 4) Heatmap: Ciudad x Año
# -----------------------------
@app.callback(Output("heatmap-graph", "figure"), Input("tabs", "value"))
def update_heatmap_fig(_):
    top_cities = df_latest.sort_values("RentIndex", ascending=False).head(25)["RegionName"].tolist()
    dff = df[df["RegionName"].isin(top_cities)].copy()

    pivot = (
        dff.groupby(["RegionName", "Year"], as_index=False)
           .agg(RentIndex=("RentIndex", "mean"))
    )

    fig = px.density_heatmap(
        pivot,
        x="Year",
        y="RegionName",
        z="RentIndex",
        labels={"RentIndex": "Renta (miles USD)", "Year": "Año", "RegionName": "Ciudad"},
    )
    fig.update_traces(hovertemplate="<b>%{y}</b><br>Año: %{x}<br>Renta: %{z:,.2f}k<extra></extra>")
    fig = apply_dark_layout(fig, "Heatmap: renta promedio anual (Top 25 ciudades actuales)")
    fig.update_layout(hovermode="closest")
    return fig

@app.callback(Output("heatmap-stats", "children"), Input("heatmap-graph", "clickData"))
def update_heatmap_stats(clickData):
    top_cities = df_latest.sort_values("RentIndex", ascending=False).head(25)["RegionName"].tolist()
    dff = df[df["RegionName"].isin(top_cities)].copy()
    annual = (
        dff.groupby(["RegionName", "Year"], as_index=False)
           .agg(RentIndex=("RentIndex", "mean"))
    )

    if not (clickData and clickData.get("points")):
        return stat_card(
            "Cómo leer el heatmap",
            [
                ("Color", "Más claro = mayor renta" ),
                ("Filas", "Ciudades" ),
                ("Columnas", "Años" ),
            ],
            note="Haz clic en una celda para ver la renta promedio de esa ciudad en ese año y su variación vs el año anterior.",
        )

    pt = clickData["points"][0]
    city = pt.get("y")
    year = int(pt.get("x"))
    row = annual[(annual["RegionName"] == city) & (annual["Year"] == year)].head(1)
    if row.empty:
        return stat_card("Resumen", [("Selección", "—")])

    val = float(row.iloc[0]["RentIndex"])
    prev_row = annual[(annual["RegionName"] == city) & (annual["Year"] == year - 1)].head(1)
    yoy = "—"
    if not prev_row.empty:
        prev_val = float(prev_row.iloc[0]["RentIndex"])
        yoy = fmt_pct(((val - prev_val) / prev_val) * 100) if prev_val else "—"

    # stats del año para esa ciudad (min/max mensual)
    monthly = dff[(dff["RegionName"] == city) & (dff["Year"] == year)].copy()
    vmin = float(monthly["RentIndex"].min()) if not monthly.empty else float("nan")
    vmax = float(monthly["RentIndex"].max()) if not monthly.empty else float("nan")

    return stat_card(
        "Detalle (celda seleccionada)",
        [
            ("Ciudad", city),
            ("Año", str(year)),
            ("Promedio anual", fmt_k(val)),
            ("Var vs año anterior", yoy),
            ("Mín / Máx mensual", f"{fmt_k(vmin)} / {fmt_k(vmax)}"),
        ],
        note="Este panel usa promedios anuales para compactar la vista. La variación vs año anterior es una señal rápida de aceleración o enfriamiento.",
    )

# -----------------------------
# 5) Mapa por estado (choropleth)
# -----------------------------
@app.callback(Output("map-graph", "figure"), Input("tabs", "value"))
def update_map_fig(_):
    fig = px.choropleth(
        state_latest,
        locations="State",
        locationmode="USA-states",
        color="RentIndex",
        scope="usa",
        labels={"RentIndex": "Renta promedio (miles USD)"},
    )
    fig.update_traces(hovertemplate="<b>%{location}</b><br>Renta promedio: %{z:,.2f}k<extra></extra>")
    fig = apply_dark_layout(fig, "Mapa: renta promedio por estado (última fecha)")
    fig.update_layout(margin=dict(t=60, b=0, l=0, r=0), hovermode="closest")
    return fig

@app.callback(Output("map-stats", "children"), Input("map-graph", "clickData"))
def update_map_stats(clickData):
    nat_mean = float(state_latest["RentIndex"].mean()) if not state_latest.empty else float("nan")
    nat_min = float(state_latest["RentIndex"].min()) if not state_latest.empty else float("nan")
    nat_max = float(state_latest["RentIndex"].max()) if not state_latest.empty else float("nan")

    if not (clickData and clickData.get("points")):
        return stat_card(
            "Resumen nacional (última fecha)",
            [
                ("Renta promedio", fmt_k(nat_mean)),
                ("Mín / Máx (estados)", f"{fmt_k(nat_min)} / {fmt_k(nat_max)}"),
                ("Estados incluidos", str(state_latest.shape[0])),
            ],
            note="Haz clic en un estado del mapa para ver su detalle (promedio estatal y top 5 ciudades dentro del estado).",
        )

    state = clickData["points"][0].get("location")
    row = state_latest[state_latest["State"] == state].head(1)
    val = float(row.iloc[0]["RentIndex"]) if not row.empty else float("nan")

    # top ciudades en ese estado (última fecha)
    top_state = (
        df_latest[df_latest["State"] == state]
        .sort_values("RentIndex", ascending=False)
        .head(5)
    )
    city_list = [f"{r.RegionName} ({fmt_k(r.RentIndex)})" for r in top_state.itertuples(index=False)] if not top_state.empty else []
    cities_txt = "; ".join(city_list) if city_list else "—"

    vs_nat = fmt_pct(((val - nat_mean) / nat_mean) * 100) if nat_mean else "—"

    return stat_card(
        f"Detalle del estado: {state}",
        [
            ("Fecha", str(latest_date.date())),
            ("Renta promedio estatal", fmt_k(val)),
            ("Vs promedio nacional", vs_nat),
            ("Top 5 ciudades", cities_txt),
        ],
        note="El promedio estatal agrega todas las ciudades disponibles del estado (en el Top 100 por SizeRank). Si quieres, podemos ponderarlo por población si tuvieras esa variable.",
    )



# -----------------------------
# 6) Tablas, distribuciones y modelo simple
# -----------------------------
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
                            html.Label("Filtrar por Estado (opcional)", style=STYLES["label"]),
                            dcc.Dropdown(
                                id="tables-state",
                                options=[{"label": "Todos", "value": "__ALL__"}]
                                + [{"label": s, "value": s} for s in states],
                                value="__ALL__",
                                clearable=False,
                            ),
                        ],
                        style={"flex": "1"},
                    ),
                    html.Div(
                        [
                            html.Label("Ciudad para modelo", style=STYLES["label"]),
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
                        html.H3("Distribución de renta (última fecha)", style=STYLES["h3"]),
                        dcc.Graph(id="hist-graph", config={"displayModeBar": False}, style={"height": "45vh"}),
                        html.Div(id="hist-stats", style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3("Participación por estado (Top 10 + Otros)", style=STYLES["h3"]),
                        dcc.Graph(id="pie-graph", config={"displayModeBar": False}, style={"height": "45vh"}),
                        html.Div(id="pie-stats", style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3("Modelo lineal simple por ciudad", style=STYLES["h3"]),
                        html.P(
                            "Ajusta una recta a la renta vs tiempo para estimar tendencia promedio. Es un modelo básico para describir dirección general, no para pronóstico fino.",
                            style=STYLES["p"],
                        ),
                        dcc.Graph(id="reg-graph", config={"displayModeBar": False}, style={"height": "45vh"}),
                        html.Div(id="reg-stats", style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3("Tabla: resumen por estado (última fecha)", style=STYLES["h3"]),
                        html.Div(id="state-table-wrap"),
                        html.Div(id="state-table-note", style={"marginTop": "0.75rem"}),
                    ]
                )
            ),

            card(
                html.Div(
                    [
                        html.H3("Tabla: Top ciudades por crecimiento (desde inicio)", style=STYLES["h3"]),
                        html.Div(id="growth-table-wrap"),
                        html.Div(id="growth-table-note", style={"marginTop": "0.75rem"}),
                    ]
                )
            ),
        ],
    )


def _filtered_last_snapshot(state_value: str):
    dfl = df_latest.copy()
    if state_value and state_value != "__ALL__":
        dfl = dfl[dfl["State"] == state_value]
    return dfl


def _dash_table(dataframe: pd.DataFrame, page_size: int = 15, sort_action: str = "native"):
    return dash_table.DataTable(
        data=dataframe.to_dict("records"),
        columns=[{"name": c, "id": c} for c in dataframe.columns],
        page_size=page_size,
        sort_action=sort_action,
        style_as_list_view=True,
        style_cell={
            "backgroundColor": COLORS["card"],
            "color": COLORS["on-background"],
            "border": f"1px solid {COLORS['outline-variant']}",
            "fontFamily": "'Inter', sans-serif",
            "fontSize": "13px",
            "padding": "8px",
            "whiteSpace": "normal",
            "height": "auto",
        },
        style_header={
            "backgroundColor": "rgba(255,255,255,0.04)",
            "color": COLORS["on-background"],
            "fontWeight": "600",
            "border": f"1px solid {COLORS['outline-variant']}",
        },
        style_table={"overflowX": "auto"},
    )


def _fmt_money(x):
    try:
        return f"{float(x):,.2f}"
    except Exception:
        return ""


def _r2(y_true, y_pred):
    y_true = np.asarray(y_true)
    y_pred = np.asarray(y_pred)
    ss_res = np.sum((y_true - y_pred) ** 2)
    ss_tot = np.sum((y_true - np.mean(y_true)) ** 2)
    return float(1 - ss_res / ss_tot) if ss_tot != 0 else float("nan")


@app.callback(
    Output("hist-graph", "figure"),
    Output("hist-stats", "children"),
    Input("tables-state", "value"),
)
def update_hist(state_value):
    dfl = _filtered_last_snapshot(state_value)
    fig = px.histogram(
        dfl,
        x="RentIndex",
        nbins=25,
        labels={"RentIndex": "Renta (miles USD)"},
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["on-background"],
        margin=dict(t=20, b=40, l=40, r=20),
    )
    # stats
    vals = dfl["RentIndex"].dropna()
    if len(vals) == 0:
        return fig, stat_box("Sin datos para el filtro seleccionado", [])
    p50 = float(vals.median())
    p25 = float(vals.quantile(0.25))
    p75 = float(vals.quantile(0.75))
    stats = [
        ("Ciudades", f"{len(vals):,}"),
        ("Promedio", _fmt_money(vals.mean())),
        ("Mediana", _fmt_money(p50)),
        ("P25 / P75", f"{_fmt_money(p25)} / {_fmt_money(p75)}"),
        ("Mín / Máx", f"{_fmt_money(vals.min())} / {_fmt_money(vals.max())}"),
    ]
    title = "Distribución (última fecha)"
    if state_value and state_value != "__ALL__":
        title += f" — Estado {state_value}"
    return fig, stat_box(title, stats)


@app.callback(
    Output("pie-graph", "figure"),
    Output("pie-stats", "children"),
    Input("tables-state", "value"),
)
def update_pie(state_value):
    dfl = _filtered_last_snapshot(state_value)

    by_state = (
        dfl.groupby("State", as_index=False)["RentIndex"]
        .mean()
        .sort_values("RentIndex", ascending=False)
    )
    top = by_state.head(10).copy()
    if len(by_state) > 10:
        others_mean = by_state.iloc[10:]["RentIndex"].mean()
        top = pd.concat([top, pd.DataFrame([{"State": "Otros", "RentIndex": others_mean}])], ignore_index=True)

    fig = px.pie(top, names="State", values="RentIndex")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["on-background"],
        margin=dict(t=20, b=20, l=20, r=20),
        legend_title_text="Estado",
    )

    # stats for selected state if any
    if state_value and state_value != "__ALL__":
        st_vals = dfl["RentIndex"].dropna()
        stats = [
            ("Estado", state_value),
            ("Ciudades", f"{len(st_vals):,}"),
            ("Promedio", _fmt_money(st_vals.mean())),
            ("Mediana", _fmt_money(st_vals.median())),
        ]
        note = "El gráfico muestra el promedio por estado en la última fecha, pero aquí los estadísticos corresponden solo al estado filtrado."
        return fig, html.Div([stat_box("Resumen del filtro", stats), html.P(note, style=STYLES["note"])])
    else:
        # national
        vals = df_latest["RentIndex"].dropna()
        stats = [
            ("Estados", f"{df_latest['State'].nunique():,}"),
            ("Ciudades", f"{len(vals):,}"),
            ("Promedio nacional", _fmt_money(vals.mean())),
        ]
        note = "El pie resume el promedio de renta por estado (Top 10 + Otros) usando la última fecha disponible."
        return fig, html.Div([stat_box("Resumen nacional", stats), html.P(note, style=STYLES["note"])])


@app.callback(
    Output("reg-graph", "figure"),
    Output("reg-stats", "children"),
    Input("tables-city", "value"),
)
def update_reg(city):
    dff = df[df["RegionName"] == city].dropna(subset=["Date", "RentIndex"]).copy()
    dff = dff.sort_values("Date")
    # x as months since start
    x = (dff["Date"] - dff["Date"].min()).dt.days / 30.4375
    y = dff["RentIndex"].astype(float).values
    if len(dff) < 2:
        fig = px.line(dff, x="Date", y="RentIndex", labels={"RentIndex": "Renta (miles USD)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["on-background"])
        return fig, stat_box("Modelo lineal", [("Ciudad", city), ("Nota", "No hay suficientes puntos para ajustar")])

    # linear fit
    coef, intercept = np.polyfit(x, y, 1)
    y_hat = coef * x + intercept
    r2 = _r2(y, y_hat)

    # build fig
    fig = px.line(dff, x="Date", y="RentIndex", labels={"RentIndex": "Renta (miles USD)", "Date": "Fecha"})
    fig.add_scatter(x=dff["Date"], y=y_hat, mode="lines", name="Tendencia (lineal)")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["on-background"],
        margin=dict(t=20, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
    )

    slope_year = coef * 12.0  # miles USD por año aprox
    stats = [
        ("Ciudad", city),
        ("Pendiente", f"{_fmt_money(slope_year)} mil USD / año"),
        ("R²", f"{r2:.3f}" if not np.isnan(r2) else "NA"),
        ("Inicio → Actual", f"{_fmt_money(y[0])} → {_fmt_money(y[-1])}"),
        ("Cambio %", f"{((y[-1] / y[0]) - 1) * 100:,.1f}%" if y[0] else "NA"),
    ]
    expl = "Interpretación rápida: una pendiente positiva indica que, en promedio, la renta sube con el tiempo; R² cercano a 1 indica que la tendencia lineal explica gran parte de la variación (ojo: no significa causalidad)."
    return fig, html.Div([stat_box("Resultados del modelo", stats), html.P(expl, style=STYLES["note"])])


@app.callback(
    Output("state-table-wrap", "children"),
    Output("state-table-note", "children"),
    Input("tables-state", "value"),
)
def update_state_table(state_value):
    dfl = _filtered_last_snapshot(state_value)

    # growth using first vs last per city within filter
    d_first = (
        df.sort_values("Date")
        .groupby("RegionName", as_index=False)
        .first()[["RegionName", "State", "RentIndex"]]
        .rename(columns={"RentIndex": "Rent_start"})
    )
    d_last = df_latest[["RegionName", "State", "RentIndex"]].rename(columns={"RentIndex": "Rent_last"})
    g = d_last.merge(d_first, on=["RegionName", "State"], how="left")
    g["Growth_%"] = (g["Rent_last"] / g["Rent_start"] - 1) * 100

    if state_value and state_value != "__ALL__":
        g = g[g["State"] == state_value]
    # state summary
    st = (
        g.groupby("State", as_index=False)
        .agg(
            Ciudades=("RegionName", "count"),
            Renta_prom=("Rent_last", "mean"),
            Renta_mediana=("Rent_last", "median"),
            Crec_prom=("Growth_%", "mean"),
        )
        .sort_values("Renta_prom", ascending=False)
    )
    st = st.rename(columns={"Crec_prom": "Crec_%_prom"})

    # format
    st_disp = st.copy()
    for c in ["Renta_prom", "Renta_mediana"]:
        st_disp[c] = st_disp[c].map(_fmt_money)
    st_disp["Crec_%_prom"] = st_disp["Crec_%_prom"].map(lambda v: f"{v:,.1f}%")

    note = "Tabla calculada con la última fecha disponible. Crecimiento % = (última / primera) - 1 por ciudad, luego promedio por estado."
    return _dash_table(st_disp, page_size=12), html.P(note, style=STYLES["note"])


@app.callback(
    Output("growth-table-wrap", "children"),
    Output("growth-table-note", "children"),
    Input("tables-state", "value"),
)
def update_growth_table(state_value):
    d_first = (
        df.sort_values("Date")
        .groupby("RegionName", as_index=False)
        .first()[["RegionName", "State", "RentIndex"]]
        .rename(columns={"RentIndex": "Rent_start"})
    )
    d_last = df_latest[["RegionName", "State", "RentIndex"]].rename(columns={"RentIndex": "Rent_last"})
    g = d_last.merge(d_first, on=["RegionName", "State"], how="left")
    g["Growth_%"] = (g["Rent_last"] / g["Rent_start"] - 1) * 100
    g["Growth_abs"] = g["Rent_last"] - g["Rent_start"]

    if state_value and state_value != "__ALL__":
        g = g[g["State"] == state_value]

    g = g.sort_values("Growth_%", ascending=False).head(20).copy()
    disp = g[["RegionName", "State", "Rent_start", "Rent_last", "Growth_abs", "Growth_%"]].copy()
    for c in ["Rent_start", "Rent_last", "Growth_abs"]:
        disp[c] = disp[c].map(_fmt_money)
    disp["Growth_%"] = disp["Growth_%"].map(lambda v: f"{v:,.1f}%")

    note = "Top 20 por crecimiento % desde la primera fecha disponible. Útil para detectar mercados con mayor aceleración (ojo con bases pequeñas o series cortas)."
    return _dash_table(disp, page_size=10), html.P(note, style=STYLES["note"])


if __name__ == "__main__":
    load_dotenv()
    debug = os.getenv("DEBUG", "false").lower() == "true"
    port = int(os.getenv("PORT", "8050"))
    app.run(debug=debug, port=port)
