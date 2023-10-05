import pandas as pd
import os

# /Users/mathiasmagnusson/Zone-routing-protocol/data.csv

FILE_PATH = os.environ.get("MY_PROJECT_FILE_PATH", "data.csv")

headers = [f"sat{i}" for i in range(0, 66)]
data = pd.read_csv(FILE_PATH, names=headers)

def get_position_data(satIndex: int):
    return data.iloc[:,satIndex]