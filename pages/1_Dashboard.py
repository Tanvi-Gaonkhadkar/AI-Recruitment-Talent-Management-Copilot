import streamlit as st
import plotly.express as px

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")
from utils.loader import load_css
from utils.cards import metric_card
from database.database import (
    get_dashboard_stats,
    get_hiring_funnel,
    get_candidate_sources,
    get_recent_candidates
)

def load_css():
    with open("styles/style.css") as f:
        st.markdown(
            f"<style>{f.read()}</style>",
            unsafe_allow_html=True
        )

load_css()
with st.sidebar:

    st.title("🤖 AI Recruitment")

    st.caption("Talent Management Copilot")

    st.divider()

    st.write(f"👤 {st.session_state.user}")

    st.divider()

    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.clear()
        st.switch_page("pages/1_Dashboard.py")
username = st.session_state.user.split("@")[0].title()

left, right = st.columns([8, 2])

with left:
    st.title("🤖 AI Recruitment Copilot")
    st.caption("AI-powered Recruitment Dashboard")

with right:
    st.write("")
    st.info(f"👤 {username}")

st.divider()

st.subheader(f"Welcome back, {username}! 👋")
st.write("Here's today's hiring overview.")

# -----------------------------
# KPI CARDS
# -----------------------------
c1, c2, c3, c4 = st.columns(4)
stats = get_dashboard_stats()

with c1:
    metric_card(
    "👥 Candidates",
    stats["candidates"],
    ""
)
with c2:
    metric_card("📅 Interviews", stats["interviews"])

with c3:
    metric_card("💼 Open Jobs", stats["employees"])

with c4:
    metric_card("✅ Hiring Rate", f"{stats['hiring_rate']}%")

st.divider()

#charts section
left, right = st.columns([6,4])

funnel_df = get_hiring_funnel()

pie_df = get_candidate_sources()

with left:

    st.subheader("📊 Hiring Funnel")

    funnel = px.funnel(
        funnel_df,
        x="Candidates",
        y="Stage",
        color="Stage"
    )

    funnel.update_layout(
        showlegend=False,
        height=450,
        margin=dict(
            l=10,
            r=10,
            t=25,
            b=10
        )
    )

    st.plotly_chart(
        funnel,
        width="stretch"
    )
# -----------------------------
# RIGHT COLUMN
# -----------------------------
with right:

    st.subheader("🌍 Candidate Sources")

    pie = px.pie(
        pie_df,
        names="Source",
        values="Candidates",
        hole=0.6
    )

    pie.update_layout(
        height=450,
        margin=dict(
            l=10,
            r=10,
            t=25,
            b=10
        )
    )

    st.plotly_chart(
        pie,
        width="stretch"
    )
    
#bottom section    
st.divider()

left, right = st.columns([6,4])

with left:

    st.subheader("👤 Recent Candidates")

    st.dataframe(
        get_recent_candidates(),
        width="stretch",
        hide_index=True
    )
    
with right:

    st.subheader("🤖 AI Copilot")

    st.success(
        """
### Hiring Recommendation

⭐ Rahul Sharma

Match Score : **92%**

Recommendation

Proceed with Technical Interview.

Confidence : **High**
"""
    )

    st.info(
        """
### Today's Insights

✔ Python demand increased

✔ 18 new candidates today

✔ AI Engineer role has highest applications

✔ Interview success rate is 84%
"""
    )

    st.button(
    "View Insights",
    width="stretch"
)

# -----------------------------
# HIRING TREND
# -----------------------------
st.divider()

trend = {
    "Month": [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun"
    ],

    "Hires": [
        12,
        18,
        16,
        25,
        30,
        27
    ]
}

import pandas as pd

trend_df = pd.DataFrame(trend)

line = px.line(
    trend_df,
    x="Month",
    y="Hires",
    markers=True,
    title="📈 Hiring Trend"
)

line.update_layout(
    height=350
)

st.plotly_chart(
    line,
    width="stretch"
)
st.divider()
