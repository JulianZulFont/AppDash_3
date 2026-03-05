# This file is for testing purposes and viewing the cleaned data

import pandas as pd
from config import DATA_FILE

if __name__ == '__main__':
    df = pd.read_csv(DATA_FILE)
    nan_df = df[df['MedianIncome'] < 0]
    print(nan_df)
