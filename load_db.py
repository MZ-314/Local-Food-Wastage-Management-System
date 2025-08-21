import pandas as pd
import sqlite3
from dateutil.parser import parse

# Connect to SQLite (creates food.db if it doesn’t exist)
con = sqlite3.connect("food.db")
cur = con.cursor()

# Run schema
with open("schema.sql", "r") as f:
    cur.executescript(f.read())

# Load CSVs
p = pd.read_csv("data/providers_data.csv")
r = pd.read_csv("data/receivers_data.csv")
f = pd.read_csv("data/food_listings_data.csv")
c = pd.read_csv("data/claims_data.csv")

# Parse dates
f["Expiry_Date"] = pd.to_datetime(f["Expiry_Date"]).dt.date
c["Timestamp"] = pd.to_datetime(c["Timestamp"])

# Write to DB
p.to_sql("providers", con, if_exists="append", index=False)
r.to_sql("receivers", con, if_exists="append", index=False)
f.to_sql("food_listings", con, if_exists="append", index=False)
c.to_sql("claims", con, if_exists="append", index=False)

con.commit()
con.close()

print("Database created successfully ✅")
