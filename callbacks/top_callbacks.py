# callbacks/top_callbacks.py

from dash import Output, Input, callback
import plotly.express as px
from data_loader import df_latest, growth, latest_date
from utils.plotting import apply_dark_layout
from utils.formatting import fmt_k, fmt_pct
from components.common import stat_card


@callback(Output("top-graph", "figure"), Input("tabs", "value"))
def update_top_fig(tab_value):
    if tab_value != "tab-top":
        return {}
    topn = df_latest.sort_values("RentIndex", ascending=False).head(15).copy()
    topn["Label"] = topn["RegionName"] + ", " + topn["State"]

    fig = px.bar(
        topn.sort_values("RentIndex"),
        x="RentIndex", y="Label",
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


@callback(Output("top-stats", "children"), Input("top-graph", "clickData"))
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
