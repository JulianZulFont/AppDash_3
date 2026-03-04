# callbacks/scatter_callbacks.py

from dash import Output, Input, callback
import plotly.express as px
import pandas as pd
from data_loader import growth
from utils.plotting import apply_dark_layout
from utils.formatting import fmt_k, fmt_pct
from components.common import stat_card


@callback(Output("scatter-graph", "figure"), Input("tabs", "value"))
def update_scatter_fig(tab_value):
    if tab_value != "tab-scatter":
        return {}
    g = growth.dropna(subset=["RentIndex_last", "Growth_pct"]).copy()

    fig = px.scatter(
        g, x="RentIndex_last", y="Growth_pct",
        hover_name="Label",
        labels={"RentIndex_last": "Renta actual",
                "Growth_pct": "Crecimiento (%)"},
    )
    fig.update_traces(
        marker=dict(size=10, opacity=0.8, line=dict(width=0)),
        hovertemplate="<b>%{hovertext}</b><br>Renta: %{x:,.2f}k<br>Crecimiento: %{y:,.1f}%<extra></extra>",
    )
    fig = apply_dark_layout(fig, "Precio vs crecimiento")

    x_med = float(g["RentIndex_last"].median())
    y_med = float(g["Growth_pct"].median())
    fig.add_vline(x=x_med, line_width=1)
    fig.add_hline(y=y_med, line_width=1)
    return fig


@callback(Output("scatter-stats", "children"), Input("scatter-graph", "clickData"))
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
