
"""
Candidate Screening - AI Recruitment Copilot
Connected with backend Candidate Service
"""

import os

import streamlit as st
import pandas as pd

from backend.candidate_service import candidate_service

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

if st.session_state.role != "Recruiter":
    st.error("🚫 Access Denied. This module is available only to Recruiters.")
    st.stop()
st.set_page_config(page_title="Candidate Screening", page_icon="👥", layout="wide")

st.title("👥 Candidate Screening")
st.caption("AI-powered candidate screening with backend integration.")

UPLOAD_DIR = "uploads"

from database.database import get_candidates

candidates = get_candidates()

resume_files = [
    path
    for path in candidates["resume_path"]
    if isinstance(path, str) and os.path.exists(path)
]
# st.write(candidates[["name", "resume_path"]])

# st.write(resume_files)

# for i, r in enumerate(resume_files):
#     st.write(i, r, type(r))

jd_file = os.path.join(UPLOAD_DIR, "AI_EngineerJD.pdf")

with st.sidebar:
    st.header("🤖 AI Modules")
    st.success("Candidate Ranking AI")
    st.success("Hiring Recommendation AI")
    st.success("Resume Comparison AI")

@st.cache_data(show_spinner=False)
def load_data():
    return candidate_service(resume_files, jd_file)

with st.spinner("Running AI Candidate Screening..."):
    result = load_data()

rows = []
for c in result["ranking"]:
    experience = c["result"]["resume_json"].get("experience", [])

    if isinstance(experience, list):
        experience = ", ".join(experience)

    db_candidate = candidates[
                candidates["name"] == c["name"].replace("_", " ")
    ].iloc[0]
    
    rows.append({
                    "Name": db_candidate["name"],
                    "Role": db_candidate["role_applied"],
                    "Experience": db_candidate["experience"],
                    "Match": c["match"],
                    "Rank": c["rank"],
                    "Status": db_candidate["status"]
                })
        
data = pd.DataFrame(rows)

c1, c2, c3 = st.columns([2, 1, 1.2])

with c1:
    search = st.text_input("🔍 Search Candidate")

with c2:
    status_list = ["All"] + sorted(candidates["status"].unique().tolist())

    status = st.selectbox(
        "Filter Status",
        status_list
    )

with c3:
    selected = st.selectbox(
        "Select Candidate",
        data["Name"]
    )

# ==========================
# Apply Filters
# ==========================

df = data.copy()

if search:
    df = df[df["Name"].str.contains(search, case=False)]

if status != "All":
    df = df[df["Status"] == status]

candidate = next(
    c for c in result["ranking"]
    if c["name"].replace("_", " ") == selected
)

# ==========================
# Main Layout
# ==========================

left, right = st.columns([1.4, 1])

with left:
    st.subheader("📋 Candidate List")
    st.dataframe(
        df,
        hide_index=True,
        use_container_width=True
    )

with right:

    st.subheader("👤 Candidate Details")

    selected_candidate = candidates[
        candidates["name"] == selected
    ].iloc[0]

    st.write(f"**Role:** {selected_candidate['role_applied']}")
    st.write(f"**Rank:** #{candidate['rank']}")

    st.progress(
        candidate["match"],
        text=f"ATS Match {candidate['match']}%"
    )

    st.write("### Experience")

    for e in candidate["result"]["resume_json"].get("experience", []):
        st.write("-", e)

    st.write("### Education")

    for e in candidate["result"]["resume_json"].get("education", []):
        st.write("-", e)

tabs = st.tabs([
    "🏆 Ranking AI",
    "🤖 Hiring Recommendation",
    "⚖️ Resume Comparison"
    
])

with tabs[0]:
    a,b,c,d = st.columns(4)
    a.metric("Rank", f"#{candidate['rank']}")
    b.metric("Match", f"{candidate['match']}%")
    c.metric("Matched", candidate["result"]["matching"]["matched_count"])
    d.metric("Missing", len(candidate["result"]["matching"]["missing"]))
    st.success(f"Candidate ranked #{candidate['rank']} with ATS Match Score of {candidate['match']}%.")

with tabs[1]:
    rec = next(r["recommendation"] for r in result["recommendations"] if r["candidate"].replace("_"," ") == selected)
    st.markdown(rec)

from backend.resume_comparison import compare_candidates

with tabs[2]:

    st.subheader("⚖️ AI Resume Comparison")

    candidate_names = data["Name"].tolist()

    col1, col2 = st.columns(2)

    with col1:
        candidate1 = st.selectbox(
            "Candidate 1",
            candidate_names,
            key="candidate1"
        )

    with col2:

        candidate2 = st.selectbox(
            "Candidate 2",
            [c for c in candidate_names if c != candidate1],
            key="candidate2"
        )

    result1 = next(
        c["result"]
        for c in result["ranking"]
        if c["name"].replace("_", " ") == candidate1
    )

    result2 = next(
        c["result"]
        for c in result["ranking"]
        if c["name"].replace("_", " ") == candidate2
    )

    with st.spinner("Comparing candidates..."):

        comparison = compare_candidates(
            result1,
            result2
        )

    st.markdown(comparison)

st.divider()
