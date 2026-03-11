# callbacks/tables_callbacks.py

from dash import Output, Input, callback, dash_table, html
import plotly.express as px
import pandas as pd
import numpy as np
from data_loader import df, df_latest
from theme import COLORS
from styles import STYLES
from components.common import stat_box
from utils.formatting import _fmt_money, _r2

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

def _filtered_last_snapshot(state_value: str):
    dfl = df_latest.copy()
    if state_value and state_value != "__ALL__":
        dfl = dfl[dfl["State"] == state_value]
    return dfl

@callback(
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


@callback(
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
        top = pd.concat([top, pd.DataFrame(
            [{"State": "Otros", "RentIndex": others_mean}])], ignore_index=True)

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


@callback(
    Output("reg-graph", "figure"),
    Output("reg-stats", "children"),
    Input("tables-city", "value"),
)
def update_reg(city):
    dff = df[df["RegionName"] == city].dropna(
        subset=["Date", "RentIndex"]).copy()
    dff = dff.sort_values("Date")
    # x as months since start
    x = (dff["Date"] - dff["Date"].min()).dt.days / 30.4375
    y = dff["RentIndex"].astype(float).values
    if len(dff) < 2:
        fig = px.line(dff, x="Date", y="RentIndex", labels={
                      "RentIndex": "Renta (miles USD)"})
        fig.update_layout(paper_bgcolor="rgba(0,0,0,0)",
                          plot_bgcolor="rgba(0,0,0,0)", font_color=COLORS["on-background"])
        return fig, stat_box("Modelo lineal", [("Ciudad", city), ("Nota", "No hay suficientes puntos para ajustar")])

    # linear fit
    coef, intercept = np.polyfit(x, y, 1)
    y_hat = coef * x + intercept
    r2 = _r2(y, y_hat)

    # build fig
    fig = px.line(dff, x="Date", y="RentIndex", labels={
                  "RentIndex": "Renta (miles USD)", "Date": "Fecha"})
    fig.add_scatter(x=dff["Date"], y=y_hat, mode="lines",
                    name="Tendencia (lineal)")
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font_color=COLORS["on-background"],
        margin=dict(t=20, b=40, l=40, r=20),
        legend=dict(orientation="h", yanchor="bottom",
                    y=1.02, xanchor="right", x=1),
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


@callback(
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
    d_last = df_latest[["RegionName", "State", "RentIndex"]].rename(
        columns={"RentIndex": "Rent_last"})
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
    st = st.rename(columns={"Crec_prom": "Crec_%_prom", "State": "Estado"})

    # format
    st_disp = st.copy()
    for c in ["Renta_prom", "Renta_mediana"]:
        st_disp[c] = st_disp[c].map(_fmt_money)
    st_disp["Crec_%_prom"] = st_disp["Crec_%_prom"].map(lambda v: f"{v:,.1f}%")

    note = "Tabla calculada con la última fecha disponible. Crecimiento % = (última / primera) - 1 por ciudad, luego promedio por estado."
    return _dash_table(st_disp, page_size=12), html.P(note, style=STYLES["note"])


@callback(
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
    d_last = df_latest[["RegionName", "State", "RentIndex"]].rename(
        columns={"RentIndex": "Rent_last"})
    g = d_last.merge(d_first, on=["RegionName", "State"], how="left")
    g["Growth_%"] = (g["Rent_last"] / g["Rent_start"] - 1) * 100
    g["Growth_abs"] = g["Rent_last"] - g["Rent_start"]

    if state_value and state_value != "__ALL__":
        g = g[g["State"] == state_value]

    g = g.sort_values("Growth_%", ascending=False).head(20).copy()
    disp = g[["RegionName", "State", "Rent_start",
              "Rent_last", "Growth_abs", "Growth_%"]].copy()
    for c in ["Rent_start", "Rent_last", "Growth_abs"]:
        disp[c] = disp[c].map(_fmt_money)
    disp["Growth_%"] = disp["Growth_%"].map(lambda v: f"{v:,.1f}%")

    disp = disp.rename(columns={
        "RegionName": "Ciudad",
        "State": "Estado",
        "Rent_start": "Renta_inicial",
        "Rent_last": "Renta_final",
        "Growth_abs": "Crec_abs",
        "Growth_%": "Crec_%"
    })

    note = "Top 20 por crecimiento % desde la primera fecha disponible. Útil para detectar mercados con mayor aceleración (ojo con bases pequeñas o series cortas)."
    return _dash_table(disp, page_size=10), html.P(note, style=STYLES["note"])
