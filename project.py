import streamlit as st
import pandas as pd
from sqlalchemy import create_engine

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Global Seismic Trends",
    layout="wide",
)

# ---------------- FULL BLUE THEME ----------------
st.markdown("""
<style>

/* FULL PAGE BACKGROUND */
.stApp {
    background: linear-gradient(180deg, #061826, #0b2d4a);
}

/* SIDEBAR */
[data-testid="stSidebar"] {
    background-color: #081f33;
}

/* TITLE */
.title-text {
    font-size: 42px;
    font-weight: 800;
    color: #ffffff;
}


/* KPI CARD */
.metric-card {
    background: linear-gradient(180deg, #0b3c5d, #072f4a);
    padding: 26px;
    border-radius: 18px;
    text-align: center;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.5);
}
            
/* HEADER */
.header-text {
    font-size: 40px;   /* size increase */
    font-weight: 700;  /* bold */
    color: #cfe8ff;
    margin-bottom: 30px;
}

/* REMOVE UNWANTED BLUE BAR */
hr {display:none;}

/* SECTION CARD */
.section-card {
    background-color: #08263f;
    padding: 22px;
    border-radius: 18px;
    margin-top: 30px;
}

</style>
""", unsafe_allow_html=True)

# ---------------- DB CONNECTION ----------------
engine = create_engine("mysql+pymysql://root:root@localhost:3306/guvi_project_1")

def run_query(q):
    return pd.read_sql(q, engine)

# ---------------- SIDEBAR ----------------
st.sidebar.title("🧭 Navigation")
category = st.sidebar.radio(
    "Select Category",
    ["All Data", "Data Analysis"]
)

# ---------------- TITLE & HEADER ----------------
st.markdown("""
<div class="title-text">
 Global Seismic Trends: Data-Driven Earthquake Insights
</div>

<div class="header-text">
Earthquakes Insights Dashboard
</div>
""", unsafe_allow_html=True)

# ---------------- KPI METRICS ----------------
metrics = run_query("""
SELECT
    COUNT(*) AS total_eq,
    SUM(tsunami) AS tsunami_events,
    ROUND(AVG(depth_km),2) AS avg_depth,
    ROUND(AVG(mag),2) AS avg_mag
FROM earthquakes
""")

c1, c2, c3, c4 = st.columns(4)

cards = [
    ("Total Earthquakes", metrics["total_eq"][0]),
    ("Tsunami Events", metrics["tsunami_events"][0]),
    ("Avg Depth (km)", metrics["avg_depth"][0]),
    ("Avg Magnitude", metrics["avg_mag"][0])
]

for col, (title, value) in zip([c1, c2, c3, c4], cards):
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <h4>{title}</h4>
            <h2>{value}</h2>
        </div>
        """, unsafe_allow_html=True)

# ---------------- YOUR QUERIES (UNCHANGED) ----------------
queries = {
    "1. Top 10 strongest earthquakes": """
    SELECT *
    FROM earthquakes
    ORDER BY mag DESC
    LIMIT 10;
    """,

    "2. Top 10 deepest earthquakes": """
    SELECT *
    FROM earthquakes
    ORDER BY depth_km DESC
    LIMIT 10;
    """,

    "3. Shallow earthquakes (<50 km) with high magnitude (>7.5)": """
    SELECT *
    FROM earthquakes
    WHERE depth_km < 50 AND mag > 7.5;
    """,

    "4. Average magnitude by magnitude type": """
    SELECT magType, AVG(mag) AS avg_magnitude_by_type
    FROM earthquakes
    GROUP BY magType;
    """,

    "5. Year with the highest number of earthquakes": """
    SELECT year, COUNT(*) AS total_earthquakes_in_year
    FROM earthquakes
    GROUP BY year
    ORDER BY total_earthquakes_in_year DESC
    LIMIT 1;
    """,

    "6. Month with the highest number of earthquakes": """
    SELECT month, COUNT(*) AS total_earthquakes_in_month
    FROM earthquakes
    GROUP BY month
    ORDER BY total_earthquakes_in_month DESC
    LIMIT 1;
    """,

    "7. Day of week with the most earthquakes": """
    SELECT day_of_week, COUNT(*) AS total_earthquakes_on_day
    FROM earthquakes
    GROUP BY day_of_week
    ORDER BY total_earthquakes_on_day DESC
    LIMIT 1;
    """,

    "8. Number of earthquakes per hour of the day": """
    SELECT strftime('%H', time) AS hour_of_day,
           COUNT(*) AS earthquakes_per_hour
    FROM earthquakes
    GROUP BY hour_of_day
    ORDER BY hour_of_day;
    """,

    "9. Most active reporting network": """
    SELECT net, COUNT(*) AS total_reports_by_network
    FROM earthquakes
    GROUP BY net
    ORDER BY total_reports_by_network DESC
    LIMIT 1;
    """,

    "10. Count of reviewed vs automatic earthquakes": """
    SELECT status, COUNT(*) AS earthquakes_by_status
    FROM earthquakes
    WHERE status IN ('reviewed', 'automatic')
    GROUP BY status;
    """,

    "11. Count of earthquakes by event type": """
    SELECT e_type, COUNT(*) AS earthquakes_by_event_type
    FROM earthquakes
    GROUP BY e_type;
    """,

    "12. Count of earthquakes by data source type": """
    SELECT types, COUNT(*) AS earthquakes_by_data_type
    FROM earthquakes
    GROUP BY types;
    """,

    "13. Events with high station coverage (nst > threshold).": """
    SELECT *,
       (SELECT AVG(nst)
        FROM earthquakes
        WHERE nst IS NOT NULL) AS avg_nst
    FROM earthquake
    WHERE nst > (
        SELECT AVG(nst)
        FROM earthquakes
        WHERE nst IS NOT NULL);
    """,

    "14. Number of tsunami-triggered earthquakes per year": """
    SELECT year, COUNT(*) AS tsunami_triggered_events
    FROM earthquakes
    WHERE tsunami = 1
    GROUP BY year;
    """,

    "15. Count of earthquakes by alert level": """
    SELECT alert, COUNT(*) AS earthquakes_by_alert_level
    FROM earthquakes
    WHERE alert IS NOT NULL
    GROUP BY alert
    ORDER BY earthquakes_by_alert_level DESC;
    """,

    "16. Top 5 countries with highest average magnitude": """
    SELECT country, AVG(mag) AS avg_magnitude_per_country
    FROM earthquakes
    WHERE year >= (SELECT MAX(year) FROM earthquakes)
    GROUP BY country
    ORDER BY avg_magnitude_per_country DESC
    LIMIT 5;
    """,

    "17. Countries experiencing both shallow and deep earthquakes in the same month": """
    SELECT country, month
    FROM earthquakes
    GROUP BY country, month
    HAVING
        SUM(CASE WHEN depth_km < 70 THEN 1 ELSE 0 END) > 0
    AND
        SUM(CASE WHEN depth_km > 70 THEN 1 ELSE 0 END) > 0;
    """,

    "18. Top 3 most seismically active regions": """
    SELECT country,
           COUNT(*) AS earthquake_frequency,
           AVG(mag) AS avg_magnitude
    FROM earthquakes
    GROUP BY country
    ORDER BY earthquake_frequency DESC, avg_magnitude DESC
    LIMIT 3;
    """,

    "19. Average earthquake depth near the equator (±5° latitude)": """
    SELECT country, ROUND(AVG(depth_km),2) AS avg_depth_near_equator_km
    FROM earthquakes
    WHERE ABS(latitude) <= 5
    GROUP BY country;
    """,

    "20. Average magnitude comparison (tsunami vs non-tsunami events)": """
    SELECT
        AVG(CASE WHEN tsunami = 1 THEN mag END) AS avg_mag_with_tsunami,
        AVG(CASE WHEN tsunami = 0 THEN mag END) AS avg_mag_without_tsunami
    FROM earthquakes;
    """,

    "21. Lowest data reliability (gap >120 & rms >0.6)": """
        SELECT *
        FROM earthquakes
        WHERE gap > 120 AND rms > 0.6
        ORDER BY gap DESC, rms DESC;
    """,

    "22. Regions with the highest frequency of deep-focus earthquakes (>300 km)": """
    SELECT place, COUNT(*) AS deep_focus_event_count
    FROM earthquakes
    WHERE depth_km > 300
    GROUP BY place
    ORDER BY deep_focus_event_count DESC;
    """
}

# ---------------- HELPERS ----------------
def plot_curve(df):
    num = df.select_dtypes(include="number")
    if len(num.columns) >= 2:
        st.line_chart(num)

def show_map(df):
    if {"latitude", "longitude"}.issubset(df.columns):
        map_df = df.rename(columns={"latitude": "lat", "longitude": "lon"})
        st.map(map_df)

# ---------------- DATA ANALYSIS ----------------
if category == "Data Analysis":

    st.markdown('<div class="section-card">', unsafe_allow_html=True)

    selected_query = st.selectbox(
        "Choose Question",
        list(queries.keys())
    )

    if st.button("▶ Run Query"):
        df = run_query(queries[selected_query])

        st.subheader("📋 Result Table")
        st.dataframe(df, use_container_width=True)

        st.subheader("📈 Curve Graph")
        plot_curve(df)

        st.subheader("🗺️ Map View")
        show_map(df)

    st.markdown('</div>', unsafe_allow_html=True)

# ---------------- ALL DATA ----------------
else:
    st.markdown('<div class="section-card">', unsafe_allow_html=True)
    st.subheader("📋 All Earthquake Data")
    df = run_query("SELECT * FROM earthquakes LIMIT 1000;")
    st.dataframe(df, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)

