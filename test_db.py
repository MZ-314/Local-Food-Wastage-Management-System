import sqlite3
import pandas as pd

con = sqlite3.connect("food.db")

# Check tables
tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", con)
print("Tables:", tables)

# Show first 5 providers
df = pd.read_sql("SELECT * FROM providers LIMIT 5;", con)
print("\nSample providers data:")
print(df)

con.close()
