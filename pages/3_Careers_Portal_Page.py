"""
Careers Portal - AI Recruitment Copilot

Recruiter-facing view of every application received across all
published job openings.

Functions (per project plan, Module 4 - Careers Portal):
    - View applications by job
    - Search candidates
    - Filter by status
    - View uploaded resume
    - Run AI Resume Analysis
    - Move candidate to screening
"""

import os
from datetime import datetime
import pandas as pd

import streamlit as st

from database.database import (
    get_jobs,
    get_all_applications,
    add_job_application,
    update_application_status,
    save_application_analysis,
    move_application_to_screening
)

from backend.careers_portal_service import analyze_application

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

st.set_page_config(
    page_title="Careers Portal",
    page_icon="🌐",
    layout="wide"
)
UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# HEADER

st.title("🌐 Careers Portal")
st.caption(
    "View and manage applications received for all published job openings."
)

with st.sidebar:
    st.header("🤖 AI Modules")
    st.success("Resume Parsing AI")
    st.success("ATS Scoring AI")
    st.success("Hiring Recommendation AI")

jobs = get_jobs()
if jobs.empty:
    st.warning(
        "No job openings yet. Create one in Job Openings first, "
        "then applications for it will appear here."
    )
    st.stop()

job_options = {"All Jobs": None}
job_options.update({
    f"{row['job_title']} (ID {row['id']})": row["id"]
    for _, row in jobs.iterrows()
})


# LOG A NEW APPLICATION
# Bridges the gap until candidates can apply from a public-facing
# page: lets a recruiter register an application that came in
# through email / a job board / referral, resume file and all.

with st.expander("➕ Log a New Application"):

    with st.form("new_application_form", clear_on_submit=True):

        col1, col2 = st.columns(2)

        with col1:
            selected_job_label = st.selectbox(
                "Job Opening",
                [label for label in job_options if label != "All Jobs"]
            )
            candidate_name = st.text_input("Candidate Name")

        with col2:
            candidate_email = st.text_input("Candidate Email")
            resume_file = st.file_uploader("Resume (PDF)", type=["pdf"])

        submitted = st.form_submit_button("Save Application", width="stretch")

        if submitted:

            if not candidate_name or not resume_file:
                st.warning("Candidate name and resume are required.")

            else:
                resume_path = os.path.join(
                    UPLOAD_DIR, resume_file.name
                )

                with open(resume_path, "wb") as f:
                    f.write(resume_file.getbuffer())

                add_job_application(
                    job_id=job_options[selected_job_label],
                    candidate_name=candidate_name,
                    candidate_email=candidate_email,
                    resume_path=resume_path,
                    applied_date=datetime.now().strftime("%Y-%m-%d")
                )

                st.success(f"Application for {candidate_name} saved.")
                st.rerun()

st.divider()

# FILTERS -> View applications by job / Search candidates / Filter by status

filter_col1, filter_col2, filter_col3 = st.columns([2, 2, 2])

with filter_col1:
    job_filter_label = st.selectbox("Job Opening", list(job_options.keys()))

with filter_col2:
    search_term = st.text_input("🔍 Search candidates", placeholder="Candidate name")

with filter_col3:
    status_filter = st.selectbox(
        "Filter by status",
        ["All", "Applied", "AI Reviewed", "Shortlisted",
         "Hold", "Rejected", "Moved to Screening"]
    )

applications = get_all_applications(
    job_id=job_options[job_filter_label],
    search=search_term if search_term else None,
    status=status_filter
)

st.caption(f"{len(applications)} application(s) found")
st.divider()

if applications.empty:
    st.info("No applications match these filters.")
    st.stop()

# APPLICATION LIST

for _, app in applications.iterrows():

    ats_cutoff = 0 if pd.isna(app["ats_cutoff"]) else app["ats_cutoff"]
    score = 0 if pd.isna(app["ats_score"]) else app["ats_score"]

    with st.container(border=True):

        head1, head2, head3 = st.columns([3, 2, 2])

        with head1:
            st.markdown(f"### {app['candidate_name']}")
            applied_date = app["applied_date"]

            if pd.isna(applied_date):
                applied_date = "—"

            job_title = app["job_title"]

            if pd.isna(job_title):
                job_title = "Unknown Job"

            st.caption(
                f"Applied for **{job_title}** on {applied_date}"
            )

        with head2:
            st.metric("ATS Score", f"{score}%")

        with head3:
            if score >= ats_cutoff and score > 0:
                st.success(f"🟢 {app['status']}")
            else:
                st.info(f"🔵 {app['status']}")

        detail1, detail2 = st.columns(2)

        with detail1:
            skill_match = 0 if pd.isna(app["skill_match"]) else app["skill_match"]
            st.write(f"**Skill Match:** {skill_match}%")

        with detail2:
            experience_match = 0 if pd.isna(app["experience_match"]) else app["experience_match"]
            st.write(f"**Experience Match:** {experience_match}%")

        email = app["candidate_email"]

        if pd.notna(email):
            st.caption(f"✉️ {email}")

        action1, action2, action3, action4 = st.columns(4)

        # VIEW UPLOADED RESUME

        with action1:

            resume_path = app["resume_path"]

            if (
                pd.notna(resume_path)
                and isinstance(resume_path, str)
                and os.path.exists(resume_path)
            ):

                with open(resume_path, "rb") as f:
                    st.download_button(
                        "📄 View Resume",
                        f,
                        file_name=os.path.basename(resume_path),
                        key=f"resume_{app['id']}",
                        use_container_width=True
                    )

            else:

                st.button(
                    "📄 No Resume",
                    disabled=True,
                    key=f"noresume_{app['id']}",
                    use_container_width=True
                )

        # RUN AI RESUME ANALYSIS

        with action2:
            if st.button(
                "🤖 Run AI Analysis",
                key=f"analyze_{app['id']}",
                width="stretch"
            ):

                resume_path = app["resume_path"]

                if (
                    pd.isna(resume_path)
                    or not isinstance(resume_path, str)
                    or not os.path.exists(resume_path)
                ):
                    st.error("No resume file found for this application.")

                else:
                    job_description = app["job_description"]

                    if pd.isna(job_description):
                        job_description = ""
                    with st.spinner("Analyzing resume..."):

                        try:
                            result = analyze_application(
                                resume_path=resume_path,
                                job_description_text=job_description
                            )

                            save_application_analysis(
                                application_id=app["id"],
                                ats_score=result["ats_score"],
                                skill_match=result["skill_match"],
                                experience_match=result["experience_match"],
                                ai_report=result["ai_report"]
                            )

                            st.success("Analysis complete.")
                            st.rerun()

                        except Exception as e:
                            st.error(f"Analysis failed: {e}")

        # MOVE TO SCREENING

        with action3:
            if st.button(
                "➡️ Move to Screening",
                key=f"screen_{app['id']}",
                width="stretch",
                disabled=(app["status"] == "Moved to Screening")
            ):

                move_application_to_screening(app["id"])
                st.success(f"{app['candidate_name']} moved to Candidate Screening.")
                st.rerun()

        # REJECT

        with action4:
            if st.button(
                "❌ Reject",
                key=f"reject_{app['id']}",
                width="stretch",
                disabled=(app["status"] == "Rejected")
            ):

                update_application_status(app["id"], "Rejected")
                st.rerun()

        # AI REPORT (if one has been generated)

        report = app["ai_report"]

        if pd.notna(report) and isinstance(report, str) and report.strip():

            with st.expander("View AI Analysis Report"):

                st.markdown(report)

                st.download_button(
                    "Download Report",
                    data=report,
                    file_name=f"{app['candidate_name']}_AI_Report.md",
                    mime="text/markdown",
                    key=f"download_{app['id']}",
                    width="stretch"
                )