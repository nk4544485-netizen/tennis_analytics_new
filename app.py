import streamlit as st
import pandas as pd
from database.connection import get_connection


st.set_page_config(
    page_title="Tennis Analytics",
    page_icon="🎾",
    layout="wide"
)


def run_query(query, params=None):
    connection = get_connection()

    try:
        return pd.read_sql(
            query,
            connection,
            params=params
        )
    finally:
        connection.close()


st.title("🎾 Tennis Analytics Dashboard")
st.caption("SportRadar Tennis Data Analytics")

try:
    # =========================
    # SUMMARY
    # =========================

    competitor_count = run_query(
        "SELECT COUNT(*) AS total FROM competitors"
    ).iloc[0]["total"]

    competition_count = run_query(
        "SELECT COUNT(*) AS total FROM competitions"
    ).iloc[0]["total"]

    venue_count = run_query(
        "SELECT COUNT(*) AS total FROM venues"
    ).iloc[0]["total"]

    category_count = run_query(
        "SELECT COUNT(*) AS total FROM categories"
    ).iloc[0]["total"]

    col1, col2, col3, col4 = st.columns(4)

    col1.metric("Competitors", competitor_count)
    col2.metric("Competitions", competition_count)
    col3.metric("Venues", venue_count)
    col4.metric("Categories", category_count)

    st.divider()

    # =========================
    # COMPETITOR SEARCH
    # =========================

    st.subheader("🔎 Competitor Search")

    search = st.text_input(
        "Search competitor",
        placeholder="Enter competitor name..."
    )

    if search:

        competitors = run_query(
            """
            SELECT
                r.rank,
                c.name AS competitor,
                c.country,
                r.points,
                r.movement
            FROM competitors c
            JOIN competitor_rankings r
                ON c.competitor_id = r.competitor_id
            WHERE c.name LIKE %s
            ORDER BY r.rank
            """,
            (f"%{search}%",)
        )

        st.dataframe(
            competitors,
            use_container_width=True,
            hide_index=True
        )

    # =========================
    # TOP 10
    # =========================

    st.subheader("🏆 Top 10 Doubles Competitors")

    top_competitors = run_query(
        """
        SELECT
            r.rank,
            c.name AS competitor,
            r.points,
            r.movement
        FROM competitor_rankings r
        JOIN competitors c
            ON r.competitor_id = c.competitor_id
        ORDER BY r.rank
        LIMIT 10
        """
    )

    st.dataframe(
        top_competitors,
        use_container_width=True,
        hide_index=True
    )

    # =========================
    # COMPETITION ANALYSIS
    # =========================

    st.divider()

    st.subheader("🎾 Competition Analysis")

    competition_data = run_query(
        """
        SELECT
            cat.category_name,
            COUNT(*) AS competition_count
        FROM competitions c
        JOIN categories cat
            ON c.category_id = cat.category_id
        GROUP BY cat.category_name
        ORDER BY competition_count DESC
        """
    )

    st.bar_chart(
        competition_data.set_index("category_name")
    )

    # =========================
    # VENUE ANALYSIS
    # =========================

    st.subheader("🌍 Venues by Country")

    venue_data = run_query(
        """
        SELECT
            country_name,
            COUNT(*) AS venue_count
        FROM venues
        WHERE country_name IS NOT NULL
          AND country_name != ''
        GROUP BY country_name
        ORDER BY venue_count DESC
        LIMIT 15
        """
    )

    st.bar_chart(
        venue_data.set_index("country_name")
    )

    # =========================
    # FOOTER
    # =========================

    st.divider()

    st.caption(
        "Tennis Analytics • Data sourced from SportRadar API"
    )

except Exception as exc:
    st.error("Database not configured or unreachable. Add your MySQL settings in Streamlit Cloud Secrets.")
    st.code(
        """
        [mysql]
        host = "your-db-host"
        port = "3306"
        user = "your-db-user"
        password = "your-db-password"
        database = "tennis_analytics"
        """
    )
    st.write(f"Technical details: {exc}")
    st.stop()