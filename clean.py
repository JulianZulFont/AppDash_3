import pandas as pd
import os
from config import MESES_ES


def clean_data() -> pd.DataFrame:
    """
    Takes the raw city-zori.csv file and returns a version with melted data
    """

    # Load the data
    df = pd.read_csv("data-raw/city-zori.csv")

    # Identify metadata columns vs date columns
    # The metadata columns are the first 8 columns (RegionID to CountyName)
    metadata_cols = ["RegionID", "SizeRank", "RegionName",
                     "RegionType", "StateName", "State", "Metro", "CountyName"]
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
    # Drop rows with missing values
    df_melted = df_melted.dropna(
        subset=["Date", "RegionName", "State", "RentIndex"])

    # Top 100 by SizeRank
    df_melted = df_melted[df_melted["SizeRank"] < 100]

    # Calculate Spanish date
    df_melted["Fecha_ES"] = df_melted["Date"].dt.month.map(
        MESES_ES) + " " + df_melted["Date"].dt.year.astype(str)
    # Calculate year
    df_melted["Year"] = df_melted["Date"].dt.year

    # Return data from 2015 to 2024 since median household income data is only available for those years
    df_melted = df_melted[df_melted['Year'].isin(
        [year for year in range(2015, 2025)])]

    return df_melted


US_STATES = {
    'Alabama': 'AL', 'Alaska': 'AK', 'Arizona': 'AZ', 'Arkansas': 'AR', 'California': 'CA',
    'Colorado': 'CO', 'Connecticut': 'CT', 'Delaware': 'DE', 'Florida': 'FL', 'Georgia': 'GA',
    'Hawaii': 'HI', 'Idaho': 'ID', 'Illinois': 'IL', 'Indiana': 'IN', 'Iowa': 'IA',
    'Kansas': 'KS', 'Kentucky': 'KY', 'Louisiana': 'LA', 'Maine': 'ME', 'Maryland': 'MD',
    'Massachusetts': 'MA', 'Michigan': 'MI', 'Minnesota': 'MN', 'Mississippi': 'MS',
    'Missouri': 'MO', 'Montana': 'MT', 'Nebraska': 'NE', 'Nevada': 'NV', 'New Hampshire': 'NH',
    'New Jersey': 'NJ', 'New Mexico': 'NM', 'New York': 'NY', 'North Carolina': 'NC',
    'North Dakota': 'ND', 'Ohio': 'OH', 'Oklahoma': 'OK', 'Oregon': 'OR', 'Pennsylvania': 'PA',
    'Rhode Island': 'RI', 'South Carolina': 'SC', 'South Dakota': 'SD', 'Tennessee': 'TN',
    'Texas': 'TX', 'Utah': 'UT', 'Vermont': 'VT', 'Virginia': 'VA', 'Washington': 'WA',
    'West Virginia': 'WV', 'Wisconsin': 'WI', 'Wyoming': 'WY', 'District of Columbia': 'DC', 'Puerto Rico': 'PR'
}


def add_census_data(df: pd.DataFrame) -> pd.DataFrame:
    dfs = []
    # Read every file from data/census_<year>.csv
    for year in range(2015, 2025):
        file_path = f"data/census_{year}.csv"
        if os.path.exists(file_path):
            census_df = pd.read_csv(file_path)
            census_df["Year"] = year
            dfs.append(census_df)

    if not dfs:
        return df

    all_census = pd.concat(dfs, ignore_index=True)
    all_census['MedianIncome'] = pd.to_numeric(
        all_census['B19013_001E'], errors='coerce'
    )

    # Parse NAME (e.g., "Houston city, Texas")
    all_census[['CityRaw', 'StateName']] = all_census['NAME'].str.split(
        ', ', expand=True, n=1)

    # Clean City name (remove " city")
    all_census['City'] = all_census['CityRaw'].str.replace(
        " city", "", case=False, regex=False)

    # Map State Name to Abbreviation
    all_census['State'] = all_census['StateName'].map(US_STATES)

    # Keep only relevant columns
    all_census = all_census[['City', 'State', 'Year', 'MedianIncome']]

    # Merge with original DataFrame
    df_merged = df.merge(
        all_census,
        how='left',
        left_on=['RegionName', 'State', 'Year'],
        right_on=['City', 'State', 'Year']
    )

    # Drop the redundant City column
    df_merged = df_merged.drop(columns=['City'])
    df_merged = df_merged[df_merged['MedianIncome'].notna()]
    df_merged['MedianIncome'] = df_merged['MedianIncome'] / 12 # Convert to monthly
    # Calculate percentage of rent index
    df_merged["RentIndexPct"] = df_merged["RentIndex"] / df_merged["MedianIncome"] * 100

    return df_merged


def save_cleaned(df: pd.DataFrame):
    # Save the cleaned data to a new CSV
    output_path = "data/city-zori-long.csv"
    df.to_csv(output_path, index=False)
    print(f"Cleaned data saved to {output_path}")


if __name__ == "__main__":
    df_clean = clean_data()
    df_clean = add_census_data(df_clean)
    save_cleaned(df_clean)
