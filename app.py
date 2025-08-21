import streamlit as st
import pandas as pd
from sqlalchemy import create_engine, text

st.set_page_config(page_title="Local Food Wastage Management", layout="wide")

# Database connection
@st.cache_resource
def get_engine():
    return create_engine("sqlite:///food.db", future=True)

engine = get_engine()

st.title("🍲 Local Food Wastage Management System")

# --- Sidebar Filters ---
with st.sidebar:
    st.header("Filters")
    with engine.begin() as conn:
        cities = pd.read_sql("SELECT DISTINCT Location FROM food_listings ORDER BY Location", conn)["Location"].tolist()
        provider_types = pd.read_sql("SELECT DISTINCT Provider_Type FROM food_listings ORDER BY Provider_Type", conn)["Provider_Type"].tolist()
        meal_types = pd.read_sql("SELECT DISTINCT Meal_Type FROM food_listings ORDER BY Meal_Type", conn)["Meal_Type"].tolist()

    sel_city = st.selectbox("City", ["(All)"] + cities)
    sel_pt   = st.selectbox("Provider Type", ["(All)"] + provider_types)
    sel_meal = st.selectbox("Meal Type", ["(All)"] + meal_types)

def build_where():
    clauses, params = [], {}
    if sel_city != "(All)":
        clauses.append("Location = :city"); params["city"] = sel_city
    if sel_pt != "(All)":
        clauses.append("Provider_Type = :pt"); params["pt"] = sel_pt
    if sel_meal != "(All)":
        clauses.append("Meal_Type = :meal"); params["meal"] = sel_meal
    where = " WHERE " + " AND ".join(clauses) if clauses else ""
    return where, params

# Tabs
tab_dash, tab_prov, tab_recv, tab_food, tab_claims, tab_sql = st.tabs(
    ["📊 Dashboard", "🏪 Providers", "🤝 Receivers", "🥗 Food Listings", "📦 Claims", "🧮 SQL Outputs"]
)

# Dashboard (Filtered Food Listings)
with tab_dash:
    st.subheader("Filtered Food Listings")
    where, params = build_where()
    q = f"SELECT * FROM food_listings{where} ORDER BY Expiry_Date"
    with engine.begin() as conn:
        df_food = pd.read_sql(text(q), conn, params=params)
    st.dataframe(df_food, use_container_width=True)

    # --- EDA Charts ---
    st.markdown("### 📊 Insights")

    # 1. Food Types Distribution
    if not df_food.empty:
        st.bar_chart(df_food["Food_Type"].value_counts())

    # 2. Meal Type Distribution
        st.bar_chart(df_food["Meal_Type"].value_counts())

    # 3. Expiry Timeline
        df_expiry = df_food.groupby("Expiry_Date")["Quantity"].sum().reset_index()
        st.line_chart(df_expiry.set_index("Expiry_Date"))

    else:
        st.info("No food listings match the selected filters.")


# Providers (CRUD example)
with tab_prov:
    st.subheader("Providers (CRUD)")
    with engine.begin() as conn:
        df = pd.read_sql("SELECT * FROM providers ORDER BY Name", conn)
    st.dataframe(df, use_container_width=True)

    with st.expander("➕ Add / ✏️ Update / ❌ Delete"):
        act = st.radio("Action", ["Add", "Update", "Delete"], horizontal=True)
        pid = st.number_input("Provider_ID", min_value=0, step=1)
        name = st.text_input("Name"); typ = st.text_input("Type")
        addr = st.text_input("Address"); city = st.text_input("City"); contact = st.text_input("Contact")
        if st.button("Submit", type="primary"):
            with engine.begin() as conn:
                if act=="Add":
                    conn.execute(text("""INSERT INTO providers(Provider_ID,Name,Type,Address,City,Contact)
                                          VALUES(:pid,:n,:t,:a,:c,:p)"""),
                                 {"pid":pid,"n":name,"t":typ,"a":addr,"c":city,"p":contact})
                elif act=="Update":
                    conn.execute(text("""UPDATE providers SET Name=:n,Type=:t,Address=:a,City=:c,Contact=:p
                                         WHERE Provider_ID=:pid"""),
                                 {"pid":pid,"n":name,"t":typ,"a":addr,"c":city,"p":contact})
                else:
                    conn.execute(text("DELETE FROM providers WHERE Provider_ID=:pid"), {"pid":pid})
            st.success("✅ Operation successful. Refresh page to see changes.")

# Receivers
with tab_recv:
    st.subheader("Receivers")
    with engine.begin() as conn:
        st.dataframe(pd.read_sql("SELECT * FROM receivers ORDER BY Name", conn), use_container_width=True)

# Food Listings
with tab_food:
    st.subheader("Food Listings")
    with engine.begin() as conn:
        where, params = build_where()
        q = f"SELECT * FROM food_listings{where} ORDER BY Expiry_Date"
        st.dataframe(pd.read_sql(text(q), conn, params=params), use_container_width=True)

# Claims
with tab_claims:
    st.subheader("Claims")
    with engine.begin() as conn:
        df_claims = pd.read_sql("SELECT * FROM claims ORDER BY Timestamp DESC", conn)
    st.dataframe(df_claims, use_container_width=True)

    # Status Pie Chart
    if not df_claims.empty:
        status_counts = df_claims["Status"].value_counts()
        st.markdown("### 📊 Claim Status Distribution")
        st.bar_chart(status_counts)


# SQL Outputs
with tab_sql:
    st.subheader("SQL Analysis (15 Queries)")
    queries = {
        "1. Providers & Receivers per City": """
            SELECT City, 'Providers' AS Entity, COUNT(*) AS Count FROM providers GROUP BY City
            UNION ALL
            SELECT City, 'Receivers' AS Entity, COUNT(*) FROM receivers GROUP BY City;
        """,
        "2. Provider Type contributing the most": """
            SELECT Provider_Type, SUM(Quantity) AS Total_Quantity FROM food_listings
            GROUP BY Provider_Type ORDER BY Total_Quantity DESC;
        """,
        "3. Provider Contacts": """
            SELECT Name, Type, Address, Contact, City FROM providers ORDER BY City, Name;
        """,
        "4. Top Receivers by Claims": """
            SELECT r.Name, COUNT(*) AS Claims
            FROM claims c JOIN receivers r ON r.Receiver_ID=c.Receiver_ID
            GROUP BY r.Name ORDER BY Claims DESC;
        """,
        "5. Total Quantity Available": "SELECT SUM(Quantity) FROM food_listings;",
        "6. City with Most Listings": """
            SELECT Location, COUNT(*) AS Listings FROM food_listings
            GROUP BY Location ORDER BY Listings DESC;
        """,
        "7. Most Common Food Types": """
            SELECT Food_Type, COUNT(*) AS Listings FROM food_listings
            GROUP BY Food_Type ORDER BY Listings DESC;
        """,
        "8. Claims per Food Item": """
            SELECT f.Food_Name, COUNT(c.Claim_ID) AS Claims
            FROM food_listings f LEFT JOIN claims c ON f.Food_ID=f.Food_ID
            GROUP BY f.Food_Name ORDER BY Claims DESC;
        """,
        "9. Provider with Most Completed Claims": """
            SELECT p.Name, COUNT(*) AS Completed_Claims
            FROM claims c JOIN food_listings f ON f.Food_ID=c.Food_ID
            JOIN providers p ON p.Provider_ID=f.Provider_ID
            WHERE c.Status='Completed'
            GROUP BY p.Name ORDER BY Completed_Claims DESC;
        """,
        "10. Claim Status Percentages": """
            WITH T AS (SELECT Status, COUNT(*) AS cnt FROM claims GROUP BY Status),
            S AS (SELECT SUM(cnt) AS total FROM T)
            SELECT T.Status, T.cnt, ROUND(100.0*T.cnt/S.total,2) AS Percent FROM T, S;
        """,
        "11. Avg Quantity per Receiver": """
            SELECT r.Name, ROUND(AVG(f.Quantity),2) AS Avg_Quantity
            FROM claims c JOIN receivers r ON r.Receiver_ID=c.Receiver_ID
            JOIN food_listings f ON f.Food_ID=c.Food_ID
            WHERE c.Status='Completed'
            GROUP BY r.Name ORDER BY Avg_Quantity DESC;
        """,
        "12. Most-Claimed Meal Type": """
            SELECT f.Meal_Type, COUNT(*) AS Claims
            FROM claims c JOIN food_listings f ON f.Food_ID=c.Food_ID
            WHERE c.Status='Completed'
            GROUP BY f.Meal_Type ORDER BY Claims DESC;
        """,
        "13. Total Donated by Provider": """
            SELECT p.Name, SUM(f.Quantity) AS Total_Donated
            FROM food_listings f JOIN providers p ON p.Provider_ID=f.Provider_ID
            GROUP BY p.Name ORDER BY Total_Donated DESC;
        """,
        "14. Near Expiry (48h)": """
            SELECT Food_Name, Quantity, Expiry_Date, Location
            FROM food_listings
            WHERE julianday(Expiry_Date)-julianday('now') BETWEEN 0 AND 2;
        """,
        "15. Claim Conversion by City": """
            WITH L AS (SELECT Location, COUNT(*) AS Listings FROM food_listings GROUP BY Location),
            C AS (SELECT f.Location, COUNT(*) AS Completed_Claims
                  FROM claims c JOIN food_listings f ON f.Food_ID=c.Food_ID
                  WHERE c.Status='Completed' GROUP BY f.Location)
            SELECT L.Location, L.Listings, COALESCE(C.Completed_Claims,0) AS Completed,
                   ROUND(100.0*COALESCE(C.Completed_Claims,0)/L.Listings,2) AS Conversion_Percent
            FROM L LEFT JOIN C ON L.Location=C.Location;
        """
    }

    with engine.begin() as conn:
        for title, sql in queries.items():
            st.markdown(f"**{title}**")
            df = pd.read_sql(text(sql), conn)
            st.dataframe(df, use_container_width=True)
