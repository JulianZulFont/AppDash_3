import pandas as pd
from config import MESES_ES

def clean_data():
    # Load the data
    df = pd.read_csv("data-raw/city-zori.csv")

    # Identify metadata columns vs date columns
    # The metadata columns are the first 8 columns (RegionID to CountyName)
    metadata_cols = ["RegionID", "SizeRank", "RegionName", "RegionType", "StateName", "State", "Metro", "CountyName"]
    date_cols = [col for col in df.columns if col not in metadata_cols]

    # Melt the data (transform from wide format to long format)
    # This makes it easier to plot time series
    df_melted = df.melt(
        id_vars=metadata_cols,
        value_vars=date_cols,
        var_name="Date",
        value_name="RentIndex"
    )

    # Convert Date to datetime objects
    df_melted["Date"] = pd.to_datetime(df_melted["Date"])

    # Fecha en español
    df_melted["Fecha_ES"] = df_melted["Date"].dt.month.map(MESES_ES) + " " + df_melted["Date"].dt.year.astype(str)
    # Calcular año
    df_melted["Year"] = df_melted["Date"].dt.year
    
    return df_melted

def save_cleaned(df: pd.DataFrame):
    # Save the cleaned data to a new CSV
    output_path = "data/city-zori-long.csv"
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")
    
if __name__ == "__main__":
    df_clean = clean_data()
    save_cleaned(df_clean)
