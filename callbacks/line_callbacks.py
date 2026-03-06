# callbacks/line_callbacks.py

from dash import Output, Input, callback
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from data_loader import df
from theme import COLORS
from utils.plotting import apply_dark_layout
from utils.formatting import fmt_k, fmt_pct
from components.common import stat_card


@callback(Output("line-graph", "figure"), Input("city-dropdown", "value"))
def update_line_fig(selected_city):
    color_map = {
        "RentIndex": COLORS["primary"],
        "MedianIncome": COLORS["tertiary"],
    }

    dff = df[df["RegionName"] == selected_city].copy()

    fig = go.Figure()

    # Trazas individuales
    fig.add_trace(go.Scatter(
        x=dff["Date"],
        y=dff["MedianIncome"],
        name="Ingreso (k USD)",
        line=dict(color=color_map["MedianIncome"], width=3),
        hovertemplate="<b>%{customdata}</b><br>Ingreso: %{y:,.2f}k<extra></extra>",
        customdata=dff["Fecha_ES"]
    ))
    fig.add_trace(go.Scatter(
        x=dff["Date"],
        y=dff["RentIndex"],
        name="Renta (k USD)",
        line=dict(color=color_map["RentIndex"], width=3),
        hovertemplate="<b>%{customdata}</b><br>Renta: %{y:,.2f}k<extra></extra>",
        customdata=dff["Fecha_ES"]
    ))

    fig = apply_dark_layout(fig, f"Índice de Renta Histórico: {selected_city}")
    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=COLORS["surface-variant"],
            font_color=COLORS["on-background"],
            font_size=13,
            font_family="Inter"
        ),
        xaxis_title="Fecha",
        yaxis_title="Miles USD"
    )
    return fig


@callback(Output("percentage-line-graph", "figure"), Input("city-dropdown", "value"))
def update_percentage_line_fig(selected_city):
    dff = df[df["RegionName"] == selected_city].copy()
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=dff["Date"],
        y=dff["RentIndexPct"],
        name="Renta (%)",
        line=dict(color=COLORS["primary"], width=3),
        hovertemplate="<b>%{customdata}</b><br>Renta: %{y:,.2f}%<extra></extra>",
        customdata=dff["Fecha_ES"]
    ))

    # Línea de referencia del 30% (Límite de asequibilidad)
    fig.add_hline(
        y=30,
        line_dash="dot",
        line_color=COLORS["error"],
        line_width=2,
        annotation_text="Límite 30%",
        annotation_position="bottom right",
        annotation_font_color=COLORS["error"]
    )
    fig = apply_dark_layout(
        fig, f"Porcentaje de Renta sobre Ingreso: {selected_city}")
    fig.update_layout(
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor=COLORS["surface-variant"],
            font_color=COLORS["on-background"],
            font_size=13,
            font_family="Inter"
        ),
        xaxis_title="Fecha",
        yaxis_title="Porcentaje (%)"
    )
    return fig


@callback(
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
            yoy = ((v_last - v_prev) / v_prev) * \
                100 if v_prev else float("nan")
            yoy_txt = fmt_pct(yoy)
    except Exception:
        pass

    card = stat_card(
        "Estadísticos (ciudad seleccionada)",
        [
            ("Ciudad", f"{selected_city}"),
            ("Primera fecha", str(pd.to_datetime(first["Date"]).date())),
            ("Última fecha", str(pd.to_datetime(last["Date"]).date())),
            ("Renta inicial", fmt_k(v_first)),
            ("Renta actual", fmt_k(v_last)),
            ("Cambio acumulado",
             f"{fmt_k(abs_change)} ({fmt_pct(pct_change)})"),
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
