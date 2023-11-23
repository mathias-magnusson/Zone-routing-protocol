import pandas as pd

data = pd.read_csv("/Users/mathiasmagnusson/Zone-routing-protocol/iarp-test-4.csv")

# Convert the comma-separated string to a list of floats
values = [float(x) for x in data.split(',')]

# Find the maximum value
max_value = max(values)

print("The largest value is:", max_value)