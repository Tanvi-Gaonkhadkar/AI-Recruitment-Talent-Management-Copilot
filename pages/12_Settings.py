import streamlit as st

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")
st.set_page_config(
    page_title="Settings",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ Settings")
st.caption("Customize your AI Recruitment Copilot experience.")

st.divider()

# --------------------------------------------------
# General Settings
# --------------------------------------------------

st.subheader("🌐 General Settings")

left, right = st.columns(2)

with left:

    st.selectbox(
        "🌍 Language",
        [
            "English",
            "Hindi",
            "Marathi"
        ]
    )

    st.selectbox(
        "🎨 Theme",
        [
            "Light",
            "Dark"
        ]
    )

with right:

    st.selectbox(
        "📅 Date Format",
        [
            "DD/MM/YYYY",
            "MM/DD/YYYY"
        ]
    )

    st.selectbox(
        "⏰ Time Zone",
        [
            "Asia/Kolkata",
            "UTC",
            "EST",
            "PST"
        ]
    )

st.divider()

# --------------------------------------------------
# Notifications
# --------------------------------------------------

st.subheader("🔔 Notifications")

st.checkbox("Email Notifications", value=True)

st.checkbox("Interview Reminders", value=True)

st.checkbox("Candidate Status Alerts", value=True)

st.checkbox("Weekly Hiring Report", value=False)

st.divider()

# --------------------------------------------------
# AI Preferences
# --------------------------------------------------

st.subheader("🤖 AI Preferences")

st.slider(
    "AI Recommendation Confidence",
    50,
    100,
    85
)

st.radio(
    "Resume Ranking Method",
    [
        "Skill Based",
        "Experience Based",
        "Balanced"
    ]
)

st.divider()

# --------------------------------------------------
# Data Management
# --------------------------------------------------

st.subheader("💾 Data Management")

st.button(
    "⬇ Export Hiring Report",
    width="stretch"
)

st.button(
    "📥 Download Candidate Data",
    width="stretch"
)

st.button(
    "🗑 Clear Demo Data",
    width="stretch"
)

st.divider()

# --------------------------------------------------
# About
# --------------------------------------------------

st.subheader("ℹ About Project")

st.info("""
### AI Recruitment & Talent Acquisition Copilot

**Version:** 1.0

Developed as part of the **Infosys Springboard Internship**.

**Technology Stack**

✅ Streamlit

✅ Python

✅ Plotly

✅ Pandas

**Project Type**

Frontend Prototype (UI Only)

Future enhancements include:

• Resume Parsing

• AI Candidate Ranking

• Interview Scheduling APIs

• LLM Integration (GPT/Gemini)

• ATS Database Integration
""")

st.divider()

st.success("✅ Settings saved successfully (Demo UI).")
