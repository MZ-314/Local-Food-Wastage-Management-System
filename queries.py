import sqlite3
import pandas as pd

# Connect to SQLite
con = sqlite3.connect("food.db")

# Define queries
queries = {
    "1. Providers & Receivers per City": """
        SELECT City, 'Providers' AS Entity, COUNT(*) AS Count 
        FROM providers GROUP BY City
        UNION ALL
        SELECT City, 'Receivers' AS Entity, COUNT(*) 
        FROM receivers GROUP BY City;
    """,

    "2. Provider Type contributing the most (by total quantity)": """
        SELECT Provider_Type, SUM(Quantity) AS Total_Quantity
        FROM food_listings
        GROUP BY Provider_Type
        ORDER BY Total_Quantity DESC;
    """,

    "3. Providers contact info by city": """
        SELECT Name, Type, Address, Contact, City
        FROM providers
        ORDER BY City, Name;
    """,

    "4. Receivers with most claims": """
        SELECT r.Receiver_ID, r.Name, COUNT(*) AS Claims
        FROM claims c
        JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
        GROUP BY r.Receiver_ID, r.Name
        ORDER BY Claims DESC;
    """,

    "5. Total quantity of food available": """
        SELECT SUM(Quantity) AS Total_Quantity_Available FROM food_listings;
    """,

    "6. City with most food listings": """
        SELECT Location AS City, COUNT(*) AS Listings
        FROM food_listings
        GROUP BY Location
        ORDER BY Listings DESC;
    """,

    "7. Most common food types": """
        SELECT Food_Type, COUNT(*) AS Listings
        FROM food_listings
        GROUP BY Food_Type
        ORDER BY Listings DESC;
    """,

    "8. Claims per food item": """
        SELECT f.Food_ID, f.Food_Name, COUNT(c.Claim_ID) AS Claims
        FROM food_listings f
        LEFT JOIN claims c ON f.Food_ID = c.Food_ID
        GROUP BY f.Food_ID, f.Food_Name
        ORDER BY Claims DESC;
    """,

    "9. Provider with most completed claims": """
        SELECT p.Name, COUNT(*) AS Completed_Claims
        FROM claims c
        JOIN food_listings f ON f.Food_ID = c.Food_ID
        JOIN providers p ON p.Provider_ID = f.Provider_ID
        WHERE c.Status = 'Completed'
        GROUP BY p.Name
        ORDER BY Completed_Claims DESC;
    """,

    "10. Claim status percentages": """
        WITH T AS (
            SELECT Status, COUNT(*) AS cnt FROM claims GROUP BY Status
        ),
        S AS (SELECT SUM(cnt) AS total FROM T)
        SELECT T.Status, T.cnt, ROUND(100.0*T.cnt/S.total,2) AS Percent
        FROM T, S;
    """,

    "11. Avg quantity claimed per receiver": """
        SELECT r.Name, ROUND(AVG(f.Quantity), 2) AS Avg_Quantity_Claimed
        FROM claims c
        JOIN receivers r ON r.Receiver_ID = c.Receiver_ID
        JOIN food_listings f ON f.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY r.Name
        ORDER BY Avg_Quantity_Claimed DESC;
    """,

    "12. Most claimed meal type": """
        SELECT f.Meal_Type, COUNT(*) AS Claims
        FROM claims c
        JOIN food_listings f ON f.Food_ID = c.Food_ID
        WHERE c.Status = 'Completed'
        GROUP BY f.Meal_Type
        ORDER BY Claims DESC;
    """,

    "13. Total food donated by each provider": """
        SELECT p.Name, SUM(f.Quantity) AS Total_Donated
        FROM food_listings f
        JOIN providers p ON p.Provider_ID = f.Provider_ID
        GROUP BY p.Name
        ORDER BY Total_Donated DESC;
    """,

    "14. Near-expiry items (next 48h)": """
        SELECT Food_ID, Food_Name, Quantity, Expiry_Date, Location
        FROM food_listings
        WHERE julianday(Expiry_Date) - julianday('now') BETWEEN 0 AND 2
        ORDER BY Expiry_Date;
    """,

    "15. Claim conversion rate by city": """
        WITH L AS (
            SELECT Location, COUNT(*) AS Listings
            FROM food_listings
            GROUP BY Location
        ),
        C AS (
            SELECT f.Location, COUNT(*) AS Completed_Claims
            FROM claims c
            JOIN food_listings f ON f.Food_ID = c.Food_ID
            WHERE c.Status = 'Completed'
            GROUP BY f.Location
        )
        SELECT L.Location, L.Listings,
               COALESCE(C.Completed_Claims,0) AS Completed_Claims,
               ROUND(100.0*COALESCE(C.Completed_Claims,0)/L.Listings,2) AS Conversion_Percent
        FROM L LEFT JOIN C ON L.Location = C.Location
        ORDER BY Conversion_Percent DESC;
    """
}

# Run all queries
for title, q in queries.items():
    print("="*50)
    print(title)
    print("-"*50)
    df = pd.read_sql(q, con)
    print(df.head(), "\n")  # print top 5 rows

con.close()
