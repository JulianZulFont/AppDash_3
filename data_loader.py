# data_loader.py - Data loading and pre-processing

import pandas as pd
import numpy as np
from config import DATA_FILE


def load_data():
    df = pd.read_csv(DATA_FILE)

    # Normalización
    df["Date"] = pd.to_datetime(df["Date"], errors="coerce")
    df = df.dropna(subset=["Date", "RegionName", "State", "RentIndex"]).copy()

    # Top 100 por SizeRank
    if "SizeRank" in df.columns:
        df = df[df["SizeRank"] < 100].copy()

    return df


def get_options(df):
    city_options = (
        df[["RegionName", "State"]]
        .drop_duplicates()
        .sort_values(["RegionName", "State"])
    )
    return [
        {"label": f"{r.RegionName}, {r.State}", "value": r.RegionName}
        for r in city_options.itertuples(index=False)
    ]


# Carga inicial para exportar a otros módulos
df = load_data()
OPTIONS = get_options(df)
latest_date = df["Date"].max()
df_latest = df[df["Date"] == latest_date].copy()

# Pre-cálculos de crecimiento


def calculate_growth(df):
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
    growth["Growth_pct"] = (growth["Growth_abs"] /
                            growth["RentIndex_first"]) * 100.0
    growth["Label"] = growth["RegionName"] + ", " + growth["State"]
    return growth


growth = calculate_growth(df)

# Promedio por estado
state_latest = (
    df_latest.groupby("State", as_index=False)
    .agg(RentIndex=("RentIndex", "mean"))
)
