# callbacks/map_callbacks.py

from dash import Output, Input, callback
import plotly.express as px
from data_loader import state_latest, df_latest, latest_date
from utils.plotting import apply_dark_layout
from utils.formatting import fmt_k, fmt_pct
from components.common import stat_card


@callback(Output("map-graph", "figure"), Input("tabs", "value"))
def update_map_fig(tab_value):
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


@callback(Output("map-stats", "children"), Input("map-graph", "clickData"))
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
