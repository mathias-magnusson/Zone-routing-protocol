import pandas as pd

headers = [f"sat{i}" for i in range(0,18)]
data = pd.read_csv("Zone-routing-protocol/data_18_100_min.csv", names=headers)

def get_position_data(satIndex: int):
    return data.iloc[:,satIndex]
