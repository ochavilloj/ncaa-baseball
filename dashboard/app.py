import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import plotly.express as px
import os

load_dotenv()
engine = create_engine(os.getenv("DB_URL"))

@st.cache_data
def load_data():
    query = """
        SELECT p.name, p.school, p.conference,
               s.season, s.ab, s.r, s.h, s.hr, s.rbi,
               s.avg, s.obp, s.slg, s.ops, s.pa, s.g
        FROM players p
        JOIN stats_batting s ON p.player_id = s.player_id
        WHERE s.ab IS NOT NULL AND s.ops IS NOT NULL
        ORDER BY s.ops DESC
    """
    return pd.read_sql(query, engine)

df = load_data()

st.title("NCAA Baseball Player Dashboard")
st.markdown("2026 Season — Batting Statistics")

# Sidebar filters
conferences = ["All"] + sorted(df["conference"].dropna().unique().tolist())
selected_conf = st.sidebar.selectbox("Conference", conferences)

schools = ["All"] + sorted(df["school"].dropna().unique().tolist())
selected_school = st.sidebar.selectbox("School", schools)

min_ab = st.sidebar.slider("Minimum At Bats", 0, int(df["ab"].max()), 10)

# Apply filters
filtered = df.copy()
if selected_conf != "All":
    filtered = filtered[filtered["conference"] == selected_conf]
if selected_school != "All":
    filtered = filtered[filtered["school"] == selected_school]
filtered = filtered[filtered["ab"] >= min_ab]

# KPI metrics
col1, col2, col3, col4 = st.columns(4)
col1.metric("Players", len(filtered))
col2.metric("Avg BA", f"{filtered['avg'].mean():.3f}" if not filtered.empty else "N/A")
col3.metric("Avg OPS", f"{filtered['ops'].mean():.3f}" if not filtered.empty else "N/A")
col4.metric("Total HR", int(filtered["hr"].sum()) if not filtered.empty else "N/A")

st.divider()

# Leaderboard
st.subheader("Player Leaderboard")
leaderboard = filtered[["name", "school", "conference", "g", "ab", "h", "hr", "rbi", "avg", "obp", "slg", "ops"]]\
    .sort_values("ops", ascending=False)\
    .reset_index(drop=True)
leaderboard.index += 1
st.dataframe(leaderboard, use_container_width=True)

st.divider()

# OPS by School
st.subheader("Average OPS by School")
ops_by_school = filtered.groupby("school")["ops"].mean().sort_values(ascending=False).reset_index()
fig1 = px.bar(ops_by_school, x="school", y="ops", color="ops",
              color_continuous_scale="blues", labels={"ops": "Avg OPS", "school": "School"})
fig1.update_layout(xaxis_tickangle=-45)
st.plotly_chart(fig1, use_container_width=True)

st.divider()

# AVG vs OPS scatter
st.subheader("Batting Average vs OPS")
fig2 = px.scatter(filtered, x="avg", y="ops", hover_name="name",
                  color="conference", size="ab",
                  labels={"avg": "Batting Average", "ops": "OPS"})
st.plotly_chart(fig2, use_container_width=True)