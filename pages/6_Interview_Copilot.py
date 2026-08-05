
import os
import pandas as pd
import streamlit as st


from backend.pdf_parser import extract_resume_text
from backend.jd_parser import extract_jd_text
from backend.ai_parser import extract_resume_info, extract_jd_info
from backend.interview_service import interview_service

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

if st.session_state.role != "Recruiter":
    st.error("🚫 Access Denied. This module is available only to Recruiters.")
    st.stop()
st.set_page_config(page_title="Interview Copilot", page_icon="🎤", layout="wide")

st.title("🎤 Interview Copilot")
st.caption("AI-assisted interview planning powered by your local Llama model.")

UPLOADS = "uploads"

from database.database import get_resume_files

resume_df = get_resume_files()
print(resume_df)
resume_options = {
    os.path.basename(path): path
    for path in resume_df["resume_path"]
    if pd.notna(path) and isinstance(path, str)
}

jd_files = sorted([
    f for f in os.listdir(UPLOADS)
    if f.lower().endswith(".pdf")
    and "jd" in f.lower()
])

with st.sidebar:
    st.header("🤖 AI Modules")
    st.success("Interview Question Generator AI")
    st.success("AI Suggested Topics")
    st.success("Evaluation Checklist")
    st.info("Powered by Local Llama 3.2")

c1, c2 = st.columns(2)

with c1:
    selected_resume = st.selectbox("📄 Candidate Resume", list(resume_options.keys()))

with c2:
    selected_jd = st.selectbox("💼 Job Description", jd_files)

difficulty = st.select_slider(
    "🎯 Difficulty",
    ["Easy", "Medium", "Hard"],
    value="Medium"
)

if "interview_result" not in st.session_state:
    st.session_state.interview_result = None

if st.button("🤖 Generate Interview Kit", use_container_width=True):

    with st.spinner("Generating Interview Kit..."):

        try:
            resume_path = resume_options[selected_resume]
            jd_path = os.path.join(UPLOADS, selected_jd)

            resume_text = extract_resume_text(resume_path)
            jd_text = extract_jd_text(jd_path)

            resume_data = extract_resume_info(resume_text)
            jd_data = extract_jd_info(jd_text)

            st.session_state.interview_result = interview_service(
                resume_data,
                jd_data
            )

            st.success("Interview Kit Generated Successfully.")

        except Exception as e:
            st.error(f"Error: {e}")

result = st.session_state.interview_result

if result:

    m1, m2, m3, m4 = st.columns(4)

    candidate_name = selected_resume.replace(".pdf", "").replace("_", " ")

    m1.metric("Candidate", candidate_name)
    m2.metric("Difficulty", difficulty)

    total_questions = (
        len(result["questions"]["technical"])
        + len(result["questions"]["hr"])
        + len(result["questions"]["behavioral"])
    )

    m3.metric("Questions", total_questions)
    m4.metric("Sections", "5")

    tabs = st.tabs([
        "💻 Technical",
        "🧠 HR",
        "🤝 Behavioral",
        "🎯 AI Suggested Topics",
        "📋 Evaluation"
    ])

    with tabs[0]:
        st.subheader("Technical Questions")
        for i, q in enumerate(result["questions"]["technical"], 1):
            st.write(f"{i}. {q}")

    with tabs[1]:
        st.subheader("HR Questions")
        for i, q in enumerate(result["questions"]["hr"], 1):
            st.write(f"{i}. {q}")

    with tabs[2]:
        st.subheader("Behavioral Questions")
        for i, q in enumerate(result["questions"]["behavioral"], 1):
            st.write(f"{i}. {q}")

    with tabs[3]:
        st.subheader("AI Suggested Interview Focus")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("### ✅ Strong Areas")
            for item in result["topics"]["strong_areas"]:
                st.write("•", item)

            st.markdown("### 📌 Project Discussion")
            for item in result["topics"]["project_discussion"]:
                st.write("•", item)

        with c2:
            st.markdown("### ⚠ Weak Areas")
            for item in result["topics"]["weak_areas"]:
                st.write("•", item)

            st.markdown("### 🔍 Missing Skill Verification")
            for item in result["topics"]["missing_skill_verification"]:
                st.write("•", item)

    with tabs[4]:

        st.subheader("Evaluation Checklist")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### Technical")
            for item in result["checklist"]["technical"]:
                st.checkbox(item)

            st.markdown("#### Soft Skills")
            for item in result["checklist"]["soft_skills"]:
                st.checkbox(item)

        with col2:
            st.markdown("#### Professional")
            for item in result["checklist"]["professional"]:
                st.checkbox(item)

        st.slider("Overall Rating", 1, 10, 8)

        st.text_area(
            "Recruiter Notes",
            height=150,
            placeholder="Write interview observations..."
        )

    report = f"""
Interview Kit

Candidate : {selected_resume}
Job Description : {selected_jd}
Difficulty : {difficulty}

Technical Questions
-------------------
""" + "\n".join(result["questions"]["technical"])

    st.download_button(
        "⬇ Download Interview Kit",
        report,
        file_name="Interview_Kit.txt",
        use_container_width=True
    )

else:
    st.info("Select a resume and job description, then click Generate Interview Kit.")
