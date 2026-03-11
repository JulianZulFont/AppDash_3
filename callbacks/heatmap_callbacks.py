# callbacks/heatmap_callbacks.py

from dash import Output, Input, callback
import plotly.express as px
from data_loader import df, df_latest
from utils.plotting import apply_dark_layout
from utils.formatting import fmt_k, fmt_pct
from components.common import stat_card


@callback(Output("heatmap-graph", "figure"), Input("tabs", "value"))
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
    fig.update_layout(hovermode="closest", coloraxis_colorbar_title="Renta (miles USD)")
    return fig


@callback(Output("heatmap-stats", "children"), Input("heatmap-graph", "clickData"))
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
