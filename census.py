import requests as req
import pandas as pd
from dotenv import load_dotenv
import os


def fetch_census_income(api_key: str, year: int) -> pd.DataFrame:
    # B19013_001E = Median Household Income
    url = f"https://api.census.gov/data/{year}/acs/acs5?get=NAME,B19013_001E&for=place:*&key={api_key}"

    response = req.get(url)
    if response.status_code == 200:
        data = response.json()
        # The first row is the header
        df_census = pd.DataFrame(data[1:], columns=data[0])
        df_census['B19013_001E'] = pd.to_numeric(
            df_census['B19013_001E'], errors='coerce'
        )

        # Filter to only keep locations categorized as "city"
        # The NAME format is typically "CityName city, StateName"
        df_census = df_census[df_census['NAME'].str.contains(
            " city, ", case=False, na=False)]
        return df_census
    else:
        print(f"Error: {response.status_code}")
        return None


def save_census(df: pd.DataFrame, year: int):
    # Save the cleaned data to a new CSV
    output_path = f"data/census_{year}.csv"
    df.to_csv(output_path, index=False)
    print(f"Saved census data for {year} to {output_path}")


if __name__ == '__main__':
    load_dotenv()
    api_key = os.getenv("CENSUS_API_KEY")
    if api_key is None:
        raise ValueError("CENSUS_API_KEY not found in .env file")
    years = [year for year in range(2015, 2025)]
    for year in years:
        df_census = fetch_census_income(api_key, year)
        save_census(df_census, year)
