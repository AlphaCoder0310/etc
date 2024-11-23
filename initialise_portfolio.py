# from pywarrants_lib.data import position_set
from pywarrants_lib.data.position_set import Position, PositionSet
import datetime as dt
import pandas as pd
import os

# Specify the directory where your CSV files are stored
inputs_path = "/Users/chrisbang/Desktop/Quant Trader/pywarrants_lib/inputs_data"

# Define the current date in yyyymmdd format
current_date = dt.datetime.now().strftime('%Y%m%d')

# Construct the full file path
csv_path = f'{inputs_path}/portfolio_{current_date}.csv'

# Read the CSV file into a DataFrame
df = pd.read_csv(csv_path)

# Extract the date from the CSV file name
filename = os.path.basename(csv_path)
date_str = filename.split('_')[1].split('.')[0]
portfolio_date = dt.datetime.strptime(date_str, '%Y%m%d')

# Create a list of Position instances from the DataFrame
positions = [
    Position(identifier=row['identifier'], quantity=row['quantity'])
    for index, row in df.iterrows()
]

# Initialize the PositionSet
portfolio = PositionSet(date=portfolio_date, positions=positions)

# Display the portfolio
print(f"Portfolio Date: {portfolio.date}")
print("Positions:")
for pos in portfolio.positions:
    print(f" - {pos.identifier}: {pos.quantity} shares")
