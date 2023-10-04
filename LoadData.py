import pandas as pd

headers = [f"sat{i}" for i in range(0, 66)]
data = pd.read_csv("Zone-routing-protocol/data.csv", names=headers)

def get_position_data(satIndex: int):
    return data.iloc[:,satIndex]