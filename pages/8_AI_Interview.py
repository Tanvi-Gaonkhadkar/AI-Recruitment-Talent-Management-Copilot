import streamlit as st

from backend.ai_interviewer import AIInterviewer

from backend.interview_service import (
    evaluate_candidate_answer,
    complete_ai_interview
)

from backend.pdf_parser import extract_resume_text
from backend.jd_parser import extract_jd_text

from backend.ai_parser import (
    extract_resume_info,
    extract_jd_info
)

from database.database import (
    save_ai_interview_answer,
    save_ai_interview_summary
)

st.set_page_config(
    page_title="AI Interview",
    page_icon="🎤",
    layout="wide"
)
if "logged_in" not in st.session_state:
    st.switch_page("Login.py")
candidate_name = st.session_state.get("selected_candidate_name")
role = st.session_state.get("selected_role")
interview_id = st.session_state.get("selected_interview_id")
if not candidate_name or not interview_id:

    st.error("No interview selected.")

    if st.button("⬅ Back"):

        st.switch_page(
            "pages/7_Interview_Management.py"
        )

    st.stop()
if "ai_interviewer" not in st.session_state:
    st.session_state.ai_interviewer = None

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "current_evaluation" not in st.session_state:
    st.session_state.current_evaluation = None

if "final_report" not in st.session_state:
    st.session_state.final_report = None

if "ai_resume_data" not in st.session_state:
    st.session_state.ai_resume_data = None

if "ai_jd_data" not in st.session_state:
    st.session_state.ai_jd_data = None
    
if "end_interview" not in st.session_state:
    st.session_state.end_interview = False

if "force_completed" not in st.session_state:
    st.session_state.force_completed = False
st.markdown("""
<style>

[data-testid="stSidebar"]{
display:none;
}

header{
visibility:hidden;
}

.block-container{
padding-top:1rem;
}

</style>
""", unsafe_allow_html=True)
# ---------------------------------------------------------------------
# AI Interview Assistant
# ---------------------------------------------------------------------
st.title("🎤 AI Interview Session")
# ----------------------------------------------------------
# INITIALIZE AI INTERVIEW
# ----------------------------------------------------------

if st.session_state.ai_interviewer is None:

    resume_path = f"uploads/{candidate_name.replace(' ','_')}.pdf"
    jd_path = "uploads/AI_EngineerJD.pdf"

    resume_text = extract_resume_text(resume_path)
    jd_text = extract_jd_text(jd_path)

    st.session_state.ai_resume_data = extract_resume_info(
        resume_text
    )

    st.session_state.ai_jd_data = extract_jd_info(
        jd_text
    )

    st.session_state.ai_interviewer = AIInterviewer(

        st.session_state.ai_resume_data,

        st.session_state.ai_jd_data

    )

    st.session_state.current_evaluation = None

    st.session_state.final_report = None

    greeting = f"""
👋 Hello **{candidate_name}**,

Welcome to your AI Interview.

I'll conduct your interview based on your Resume and Job Description.

Let's begin.
"""

    first_question = (
        st.session_state.ai_interviewer
        .get_current_question()
    )

    if not st.session_state.chat_history:

     st.session_state.chat_history = [

        ("assistant", greeting),

        (
            "assistant",
            f"### Question 1\n\n{first_question}"
        )

    ]


# Hide Streamlit navigation during interview

ai_interviewer = st.session_state.ai_interviewer

# ---------------- TOP BAR ----------------

top1, top2 = st.columns([5,1])

with top1:

    # st.markdown("# 🎤 AI Interview Session")

    st.caption(
        f"Candidate : {candidate_name} | Role : {role}"
    )

with top2:

    st.success("🟢 Live")

st.progress(ai_interviewer.progress()/100)

st.caption(
    f"Question {min(ai_interviewer.current_index+1,len(ai_interviewer.questions))}"
    f"/{len(ai_interviewer.questions)}"
)

st.divider()

# ----------------------------------------------------------
# END INTERVIEW
# ----------------------------------------------------------

top_left, top_right = st.columns([5, 1])

with top_right:

    if st.button(
        "🛑 End Interview",
        use_container_width=True,
        type="secondary"
    ):

        st.session_state.end_interview = True

        st.rerun()


if st.session_state.end_interview:

    st.warning(
        "Are you sure you want to end this interview?"
    )

    c1, c2 = st.columns(2)

    with c1:

        if st.button(
            "✅ Yes, End Interview",
            use_container_width=True
        ):

            with st.spinner("Generating Final Report..."):

                report = complete_ai_interview(
                    ai_interviewer
                )

                save_ai_interview_summary(
                    interview_id,
                    report
                )

                st.session_state.final_report = report

                st.session_state.force_completed = True

                st.session_state.end_interview = False

                st.rerun()

    with c2:

        if st.button(
            "Continue Interview",
            use_container_width=True
        ):

            st.session_state.end_interview = False

            st.rerun()

# ---------------- CHAT ----------------

for role_name, message in st.session_state.chat_history:

    with st.chat_message(role_name):

        st.markdown(message)

# ---------------- INPUT ----------------

if (
    not ai_interviewer.interview_completed()
    and not st.session_state.force_completed
    and not st.session_state.end_interview
):

    answer = st.chat_input(
        "Type your answer..."
    )

    if answer:

        # Candidate message

        st.session_state.chat_history.append(
            (
                "user",
                answer
            )
        )

        question = ai_interviewer.get_current_question()

        with st.spinner("AI Interviewer is evaluating..."):

            evaluation = evaluate_candidate_answer(

                ai_interviewer,

                st.session_state.ai_resume_data,

                st.session_state.ai_jd_data,

                answer

            )

        st.session_state.current_evaluation = evaluation

        save_ai_interview_answer(

            interview_id,

            question,

            answer,

            evaluation["score"],

            evaluation["feedback"],

            ", ".join(evaluation["strengths"]),

            ", ".join(evaluation["weaknesses"]),

            evaluation["follow_up"]

        )

        feedback = f"""
### ✅ AI Evaluation

⭐ **Score : {evaluation['score']}/10**

🎯 **Confidence : {evaluation['confidence']}%**

**Feedback**

{evaluation['feedback']}

---

**Follow-up**

{evaluation['follow_up']}
"""

        st.session_state.chat_history.append(

            (
                "assistant",
                feedback
            )

        )

        # Next Question

        if not ai_interviewer.interview_completed():

            next_question = ai_interviewer.get_current_question()

            st.session_state.chat_history.append(

                (
                    "assistant",

                    f"""
### Question {ai_interviewer.current_index+1}

{next_question}
"""
                )

            )

        st.rerun()
# ----------------------------------------------------------
# INTERVIEW COMPLETED
# ----------------------------------------------------------

if (
    ai_interviewer.interview_completed()
    or st.session_state.force_completed
):

    st.divider()

    st.success("🎉 AI Interview Completed Successfully!")

    st.markdown("""
The candidate has answered all interview questions.

Click below to generate the complete AI Interview Assessment Report.
""")

    c1, c2 = st.columns([2,1])

    with c1:

    # Only show this button if report has not already been generated
        if st.session_state.final_report is None:

            if st.button(
                "📊 Generate Final AI Report",
                use_container_width=True
            ):

                with st.spinner("Generating Final Report..."):

                    report = complete_ai_interview(
                        ai_interviewer
                    )

                    save_ai_interview_summary(
                        interview_id,
                        report
                    )

                    st.session_state.final_report = report

                st.rerun()

    with c2:

        if st.button(
            "❌ Exit Interview",
            use_container_width=True
        ):

            st.session_state.ai_interviewer = None
            st.session_state.chat_history = []
            st.session_state.current_evaluation = None
            st.session_state.final_report = None
            st.session_state.ai_resume_data = None
            st.session_state.ai_jd_data = None
            st.session_state.end_interview = False
            st.session_state.force_completed = False

            st.switch_page(
                "pages/7_Interview_Management.py"
            )
    # ----------------------------------------------------------
# SHOW FINAL REPORT
# ----------------------------------------------------------

if st.session_state.final_report:

    report = st.session_state.final_report

    st.divider()

    st.markdown("# 📋 AI Interview Assessment Report")

    st.caption(
        f"Candidate : {candidate_name}    |    Role : {role}"
    )

    st.write("")

    # ---------------- SCORE CARDS ----------------

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        st.metric(
            "Technical",
            f"{report['technical_score']}%"
        )

    with c2:
        st.metric(
            "Communication",
            f"{report['communication_score']}%"
        )

    with c3:
        st.metric(
            "Confidence",
            f"{report['confidence_score']}%"
        )

    with c4:
        st.metric(
            "Overall",
            f"{report['overall_score']}%"
        )

    st.divider()

# ---------------- RECOMMENDATION ----------------

    recommendation = report["recommendation"]

    if recommendation.lower().startswith("recommend"):

        st.success(
            f"✅ Recommendation : {recommendation}"
        )

    elif "hold" in recommendation.lower():

        st.warning(
            f"⚠ Recommendation : {recommendation}"
        )

    else:

        st.error(
            f"❌ Recommendation : {recommendation}"
        )

    # ---------------- SUMMARY ----------------

    st.subheader("📝 AI Summary")

    st.info(
        report["summary"]
    )

    st.divider()

    import json

    left, right = st.columns(2)

    # ---------------- DOWNLOAD ----------------

    with left:

        st.download_button(

            "📥 Download Interview Report",

            data=json.dumps(

                report,

                indent=4

            ),

            file_name=f"{candidate_name}_Interview_Report.json",

            mime="application/json",

            use_container_width=True

        )

    # ---------------- EXIT ----------------

    with right:

        if st.button(

            "🏠 Return to Interview Management",

            use_container_width=True

        ):

            st.session_state.ai_interviewer = None
            st.session_state.chat_history = []
            st.session_state.current_evaluation = None
            st.session_state.final_report = None
            st.session_state.ai_resume_data = None
            st.session_state.ai_jd_data = None
            st.session_state.end_interview = False
            st.session_state.force_completed = False

            st.switch_page(
                "pages/7_Interview_Management.py"
            )

            