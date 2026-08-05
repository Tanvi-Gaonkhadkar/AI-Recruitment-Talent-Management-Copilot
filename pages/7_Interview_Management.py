import datetime
import sqlite3
import uuid
import streamlit as st
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
from backend.resume_service import analyze_resume
from backend.ai_interviewer import AIInterviewer
from database.database import (
    save_ai_interview_answer,
    save_ai_interview_summary
)
st.set_page_config(
    page_title="Interview Management | AI Recruitment Copilot",
    page_icon="🎯",
    layout="wide"
)
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

# -------------------------
# AI Interview Session
# -------------------------

if "ai_interviewer" not in st.session_state:
    st.session_state.ai_interviewer = None

if "ai_resume_data" not in st.session_state:
    st.session_state.ai_resume_data = None

if "ai_jd_data" not in st.session_state:
    st.session_state.ai_jd_data = None

if "current_evaluation" not in st.session_state:
    st.session_state.current_evaluation = None

if "final_report" not in st.session_state:
    st.session_state.final_report = None
    
if "interview_mode" not in st.session_state:
    st.session_state.interview_mode = False

if st.session_state.role != "Recruiter":
    st.error("🚫 Access Denied. This module is available only to Recruiters.")
    st.stop()

# ---------------------------------------------------------------------
# Database Connection
# ---------------------------------------------------------------------

DB_PATH = "database/recruitment.db"


def get_db_connection():
    return sqlite3.connect(DB_PATH)


# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

def generate_meeting_link():
    code = (
        f"{uuid.uuid4().hex[:3]}-"
        f"{uuid.uuid4().hex[:4]}-"
        f"{uuid.uuid4().hex[:3]}"
    )

    return f"https://meet.google.com/{code}"


def generate_ai_email(
    candidate_name,
    role,
    round_name,
    status,
    date_str="TBD",
    link_str="N/A"
):

    if status in ("Passed", "Next Round"):

        return f"""Subject: Congratulations! Next Interview Round

Dear {candidate_name},

Congratulations!

You have successfully cleared the {round_name}
for the {role} position.

Interview Details

Role : {role}

Round : Next Round

Date : {date_str}

Meeting Link : {link_str}

Regards,
Talent Acquisition Team
"""

    elif status == "Rejected":

        return f"""Subject: Application Update

Dear {candidate_name},

Thank you for interviewing for the
{role} position.

After careful evaluation,
we will not be moving ahead
with your application.

We wish you success in your career.

Regards,
Talent Acquisition Team
"""

    else:

        return f"""Subject: Interview Invitation

Dear {candidate_name},

You have been shortlisted for the
{role} position.

Interview Round :
{round_name}

Date :
{date_str}

Meeting Link :
{link_str}

Regards,
Talent Acquisition Team
"""


PIPELINE_STAGES = [
    "Applied",
    "AI Reviewed",
    "Shortlisted",
    "Interview Round 1",
    "Interview Round 2",
    "Interview Round 3",
    "Selected",
    "Offer Sent"
]

st.title("🎯 Interview Management")

st.caption(
    "Manage candidate interviews, scheduling, evaluation and offer workflow."
)

st.markdown("""
<style>

.im-chip{
display:inline-block;
padding:4px 10px;
border-radius:10px;
background:#273244;
margin:2px;
font-size:12px;
}

.im-stat-value{
font-size:24px;
font-weight:bold;
}

.im-stat-label{
font-size:11px;
opacity:0.7;
}

</style>
""", unsafe_allow_html=True)


# ---------------------------------------------------------------------
# Load Candidates
# ---------------------------------------------------------------------

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""

SELECT
    id,
    name,
    role_applied

FROM candidates

ORDER BY name

""")

candidate_rows = cursor.fetchall()

candidate_options = {
    row[1]: row[0]
    for row in candidate_rows
}

# ---------------------------------------------------------------------
# Existing Interview Workflows
# ---------------------------------------------------------------------

cursor.execute("""

SELECT

    interviews.id,

    candidates.name,

    candidates.role_applied,

    interviews.round_name,

    interviews.status

FROM interviews

LEFT JOIN candidates

ON interviews.candidate_id = candidates.id

ORDER BY interviews.id DESC

""")

records = cursor.fetchall()

conn.close()


# ---------------------------------------------------------------------
# No Interviews Yet
# ---------------------------------------------------------------------

if not records:

    st.info(
        "No interviews scheduled yet."
    )

    with st.form("schedule_first"):

        st.subheader("Schedule Interview")

        c1, c2 = st.columns(2)

        with c1:

            selected_candidate = st.selectbox(
                "Candidate",
                list(candidate_options.keys())
            )

            interviewer = st.text_input(
                "Interviewer"
            )

        with c2:

            round_name = st.selectbox(

                "Round",

                [
                    "Interview Round 1",
                    "Interview Round 2",
                    "Interview Round 3"
                ]
            )

            interview_date = st.date_input(
                "Interview Date",
                min_value=datetime.date.today()
            )

            interview_time = st.time_input(
                "Interview Time",
                value=datetime.time(10, 0)
            )

        submit = st.form_submit_button(
            "Schedule Interview",
            width="stretch"
        )

        if submit:

            meeting_link = generate_meeting_link()

            conn = get_db_connection()
            cursor = conn.cursor()

            cursor.execute("""

            INSERT INTO interviews(

                candidate_id,

                round_name,

                interviewer,

                interview_date,

                interview_time,

                meeting_mode,

                meeting_link,

                status

            )

            VALUES(?,?,?,?,?,?,?,?)

            """, (

                candidate_options[selected_candidate],

                round_name,

                interviewer,

                str(interview_date),

                str(interview_time),

                "Online",

                meeting_link,

                "Shortlisted"

            ))

            conn.commit()
            conn.close()

            st.success("Interview scheduled.")

            st.rerun()

    st.stop()

# ---------------------------------------------------------------------
# Candidate Selector
# ---------------------------------------------------------------------

candidate_map = {
    f"{row[1]} | {row[2]} | {row[3]} | {row[4]}": row[0]
    for row in records
}

selected_candidate = st.selectbox(
    "🎯 Active Candidate",
    list(candidate_map.keys())
)

interview_id = candidate_map[selected_candidate]


# ---------------------------------------------------------------------
# Load Selected Interview
# ---------------------------------------------------------------------

conn = get_db_connection()
cursor = conn.cursor()

cursor.execute("""

SELECT

    interviews.id,

    candidates.id,

    candidates.name,

    candidates.role_applied,

    candidates.skills,

    candidates.experience,

    interviews.round_name,

    interviews.interviewer,

    interviews.interview_date,

    interviews.interview_time,

    interviews.meeting_mode,

    interviews.meeting_link,

    interviews.technical_score,

    interviews.communication_score,

    interviews.technical_notes,

    interviews.communication_notes,

    interviews.overall_notes,

    interviews.feedback,

    interviews.ai_feedback,

    interviews.recommendation,

    interviews.status

FROM interviews

LEFT JOIN candidates

ON candidates.id = interviews.candidate_id

WHERE interviews.id = ?

""", (interview_id,))

row = cursor.fetchone()

conn.close()


(

interview_id,

candidate_id,

candidate_name,

role,

skills,

experience,

round_name,

interviewer,

interview_date,

interview_time,

meeting_mode,

meeting_link,

technical_score,

communication_score,

technical_notes,

communication_notes,

overall_notes,

feedback,

ai_feedback,

recommendation,

status

) = row


st.divider()


# ---------------------------------------------------------------------
# Progress Tracker
# ---------------------------------------------------------------------

st.subheader("Recruitment Pipeline")

current_stage = 0

if round_name in PIPELINE_STAGES:
    current_stage = PIPELINE_STAGES.index(round_name)

if status == "Selected":
    current_stage = 6

if status == "Offer Sent":
    current_stage = 7


cols = st.columns(len(PIPELINE_STAGES))

for i, stage in enumerate(PIPELINE_STAGES):

    with cols[i]:

        if i < current_stage:

            st.success(stage)

        elif i == current_stage:

            st.info(stage)

        else:

            st.write(stage)


st.divider()


# ---------------------------------------------------------------------
# Candidate Summary
# ---------------------------------------------------------------------

st.subheader("Candidate Summary")

left, right = st.columns([3,2])

with left:

    st.markdown(f"### {candidate_name}")

    st.write(f"**Role:** {role}")

    st.write(f"**Experience:** {experience}")

    st.write(f"**Current Round:** {round_name}")

    st.write(f"**Status:** {status}")

    st.write("**Skills**")

    if skills:

        for skill in skills.split(","):

            st.markdown(f"- {skill.strip()}")

with right:

    st.metric(
        "Technical",
        technical_score if technical_score else 0
    )

    st.metric(
        "Communication",
        communication_score if communication_score else 0
    )


st.divider()


# ---------------------------------------------------------------------
# Schedule / Update Interview
# ---------------------------------------------------------------------

st.subheader("Interview Scheduling")

with st.form("update_schedule"):

    c1, c2 = st.columns(2)

    with c1:

        new_interviewer = st.text_input(
            "Interviewer",
            interviewer if interviewer else ""
        )

        new_mode = st.selectbox(

            "Mode",

            ["Online","Offline"],

            index=0 if meeting_mode != "Offline" else 1

        )

    with c2:

        try:

            date_value = datetime.date.fromisoformat(
                interview_date
            )

        except:

            date_value = datetime.date.today()

        new_date = st.date_input(

            "Interview Date",

            value=date_value

        )

        new_time = st.time_input(

            "Interview Time",

            value=datetime.time(10,0)

        )

    new_link = st.text_input(

        "Meeting Link",

        value=meeting_link if meeting_link else ""

    )

    submit = st.form_submit_button(

        "Update Interview",

        width="stretch"

    )

    if submit:

        if not new_link:

            new_link = generate_meeting_link()

        conn = get_db_connection()

        cursor = conn.cursor()

        cursor.execute("""

        UPDATE interviews

        SET

            interviewer=?,

            interview_date=?,

            interview_time=?,

            meeting_mode=?,

            meeting_link=?

        WHERE id=?

        """,

        (

            new_interviewer,

            str(new_date),

            str(new_time),

            new_mode,

            new_link,

            interview_id

        ))

        conn.commit()

        conn.close()

        st.success("Interview updated.")

        st.rerun()


if meeting_link:

    st.info(f"Meeting Link: {meeting_link}")


st.divider()


# ---------------------------------------------------------------------
# AI Email Draft
# ---------------------------------------------------------------------

st.subheader("AI Email Draft")

email = generate_ai_email(

    candidate_name,

    role,

    round_name,

    status,

    f"{interview_date} {interview_time}",

    meeting_link

)

st.text_area(

    "Generated Email",

    email,

    height=220

)
# ---------------------------------------------------------------------
# Interview Notes
# ---------------------------------------------------------------------

st.divider()

st.subheader("Interview Notes")

with st.form("interview_notes_form"):

    tech_notes = st.text_area(
        "Technical Notes",
        value=technical_notes if technical_notes else "",
        height=120
    )

    comm_notes = st.text_area(
        "Communication Notes",
        value=communication_notes if communication_notes else "",
        height=120
    )

    overall = st.text_area(
        "Overall Notes",
        value=overall_notes if overall_notes else "",
        height=120
    )

    recruiter_feedback = st.text_area(
        "Recruiter Feedback",
        value=feedback if feedback else "",
        height=120
    )

    c1, c2 = st.columns(2)

    with c1:
        tech_score = st.slider(
            "Technical Score",
            0,
            100,
            int(technical_score or 0)
        )

    with c2:
        comm_score = st.slider(
            "Communication Score",
            0,
            100,
            int(communication_score or 0)
        )

    save_notes = st.form_submit_button(
        "Save Notes",
        width="stretch"
    )

    if save_notes:

        conn = get_db_connection()
        cursor = conn.cursor()

        cursor.execute("""

        UPDATE interviews

        SET

            technical_notes=?,

            communication_notes=?,

            overall_notes=?,

            feedback=?,

            technical_score=?,

            communication_score=?

        WHERE id=?

        """,

        (

            tech_notes,

            comm_notes,

            overall,

            recruiter_feedback,

            tech_score,

            comm_score,

            interview_id

        ))

        conn.commit()
        conn.close()

        st.success("Interview notes saved successfully.")

        st.rerun()

st.divider()
# # ---------------------------------------------------------------------
# # AI Interview Assistant
# # ---------------------------------------------------------------------
if st.button(
    "▶ Start AI Interview",
    use_container_width=True
):

    st.session_state.selected_candidate_name = candidate_name
    st.session_state.selected_role = role
    st.session_state.selected_interview_id = interview_id

    st.switch_page("pages/8_AI_Interview.py")
# st.divider()

# # ---------------- SESSION STATE ----------------

# if "chat_history" not in st.session_state:
#     st.session_state.chat_history = []

# if "interview_mode" not in st.session_state:
#     st.session_state.interview_mode = False


# # ----------------------------------------------------------
# # NORMAL INTERVIEW MANAGEMENT SCREEN
# # ----------------------------------------------------------

# if not st.session_state.interview_mode:

#     with st.container(border=True):

#         st.markdown("## 🎤 AI Interview")

#         st.write(
#             "Conduct a complete AI mock interview based on the "
#             "candidate's resume and job description."
#         )

#         c1, c2 = st.columns([3, 1])

#         with c1:

#             st.write(f"**Candidate :** {candidate_name}")

#             st.write(f"**Role :** {role}")

#             st.write(
#                 "**Interview :** Technical + HR + Behavioural"
#             )

#         with c2:

#             if st.session_state.ai_interviewer:

#                 st.success("🟢 Active")

#             else:

#                 st.info("⚪ Ready")

#         st.write("")

#         if st.button(
#             "▶ Start AI Interview",
#             use_container_width=True
#         ):

#             st.session_state.selected_candidate_name = candidate_name
#             st.session_state.selected_role = role
#             st.session_state.selected_interview_id = interview_id

#             st.switch_page("pages/8_AI_Interview.py")

#             resume_path = (
#                 f"uploads/{candidate_name.replace(' ','_')}.pdf"
#             )

#             jd_path = "uploads/AI_EngineerJD.pdf"

#             try:

#                 resume_text = extract_resume_text(
#                     resume_path
#                 )

#                 jd_text = extract_jd_text(
#                     jd_path
#                 )

#                 st.session_state.ai_resume_data = (
#                     extract_resume_info(resume_text)
#                 )

#                 st.session_state.ai_jd_data = (
#                     extract_jd_info(jd_text)
#                 )

#                 st.session_state.ai_interviewer = AIInterviewer(

#                     st.session_state.ai_resume_data,

#                     st.session_state.ai_jd_data

#                 )

#                 st.session_state.current_evaluation = None

#                 st.session_state.final_report = None

#                 st.session_state.chat_history = []

#                 st.session_state.interview_mode = True

#                 greeting = f"""
# 👋 Hello **{candidate_name}**,

# Welcome to your AI Interview.

# I will conduct a complete interview based on
# your Resume and Job Description.

# Let's begin.
# """

#                 st.session_state.chat_history.append(

#                     ("assistant", greeting)

#                 )

#                 first_question = (
#                     st.session_state.ai_interviewer
#                     .get_current_question()
#                 )

#                 st.session_state.chat_history.append(

#                     (
#                         "assistant",
#                         f"### Question 1\n\n{first_question}"
#                     )

#                 )

#                 st.rerun()

#             except Exception as e:

#                 st.error(e)
#     # ----------------------------------------------------------
# # FULL SCREEN AI INTERVIEW
# # ----------------------------------------------------------

# if st.session_state.interview_mode:

#     # Hide Streamlit navigation during interview

#     st.markdown("""
#     <style>

#     header {visibility:hidden;}

#     [data-testid="stSidebar"]{
#         display:none;
#     }

#     .block-container{
#         padding-top:1rem;
#         padding-left:2rem;
#         padding-right:2rem;
#     }

#     </style>
#     """, unsafe_allow_html=True)

#     ai_interviewer = st.session_state.ai_interviewer

#     # ---------------- TOP BAR ----------------

#     top1, top2 = st.columns([5,1])

#     with top1:

#         st.markdown("# 🎤 AI Interview Session")

#         st.caption(
#             f"Candidate : {candidate_name} | "
#             f"Role : {role}"
#         )

#     with top2:

#         st.success("🟢 Live")

#     st.progress(ai_interviewer.progress()/100)

#     st.caption(
#         f"Question "
#         f"{min(ai_interviewer.current_index+1,len(ai_interviewer.questions))}"
#         f"/{len(ai_interviewer.questions)}"
#     )

#     st.divider()

#     # ---------------- CHAT ----------------

#     for role_name, message in st.session_state.chat_history:

#         with st.chat_message(role_name):

#             st.markdown(message)

#     # ---------------- INPUT ----------------

#     if not ai_interviewer.interview_completed():

#         answer = st.chat_input(
#             "Type your answer..."
#         )

#         if answer:

#             # Candidate message

#             st.session_state.chat_history.append(
#                 (
#                     "user",
#                     answer
#                 )
#             )

#             question = ai_interviewer.get_current_question()

#             with st.spinner("AI Interviewer is evaluating..."):

#                 evaluation = evaluate_candidate_answer(

#                     ai_interviewer,

#                     st.session_state.ai_resume_data,

#                     st.session_state.ai_jd_data,

#                     answer

#                 )

#             st.session_state.current_evaluation = evaluation

#             save_ai_interview_answer(

#                 interview_id,

#                 question,

#                 answer,

#                 evaluation["score"],

#                 evaluation["feedback"],

#                 ", ".join(evaluation["strengths"]),

#                 ", ".join(evaluation["weaknesses"]),

#                 evaluation["follow_up"]

#             )

#             feedback = f"""
# ### ✅ AI Evaluation

# ⭐ **Score : {evaluation['score']}/10**

# 🎯 **Confidence : {evaluation['confidence']}%**

# **Feedback**

# {evaluation['feedback']}

# ---

# **Follow-up**

# {evaluation['follow_up']}
# """

#             st.session_state.chat_history.append(

#                 (
#                     "assistant",
#                     feedback
#                 )

#             )

#             # Next Question

#             if not ai_interviewer.interview_completed():

#                 next_question = ai_interviewer.get_current_question()

#                 st.session_state.chat_history.append(

#                     (
#                         "assistant",

#                         f"""
# ### Question {ai_interviewer.current_index+1}

# {next_question}
# """
#                     )

#                 )

#             st.rerun()
#     # ----------------------------------------------------------
# # INTERVIEW COMPLETED
# # ----------------------------------------------------------

#     if ai_interviewer.interview_completed():

#         st.divider()

#         st.success("🎉 AI Interview Completed Successfully!")

#         st.markdown("""
#     The candidate has answered all interview questions.

#     Click below to generate the complete AI Interview Assessment Report.
#     """)

#         c1, c2 = st.columns([2,1])

#         with c1:

#             if st.button(
#                 "📊 Generate Final AI Report",
#                 use_container_width=True
#             ):

#                 with st.spinner("Generating Final Report..."):

#                     report = complete_ai_interview(
#                         ai_interviewer
#                     )

#                     save_ai_interview_summary(
#                         interview_id,
#                         report
#                     )

#                     st.session_state.final_report = report

#                     st.rerun()

#         with c2:

#             if st.button(
#                 "❌ Exit Interview",
#                 use_container_width=True
#             ):

#                 st.session_state.interview_mode = False

#                 st.session_state.ai_interviewer = None

#                 st.session_state.chat_history = []

#                 st.session_state.current_evaluation = None

#                 st.session_state.final_report = None

#                 st.rerun()
#      # ----------------------------------------------------------
#     # SHOW FINAL REPORT
#     # ----------------------------------------------------------

#     if st.session_state.final_report:

#         report = st.session_state.final_report

#         st.divider()

#         st.markdown("# 📋 AI Interview Assessment Report")

#         st.caption(
#             f"Candidate : {candidate_name}    |    Role : {role}"
#         )

#         st.write("")

#         # ---------------- SCORE CARDS ----------------

#         c1, c2, c3, c4 = st.columns(4)

#         with c1:
#             st.metric(
#                 "Technical",
#                 f"{report['technical_score']}%"
#             )

#         with c2:
#             st.metric(
#                 "Communication",
#                 f"{report['communication_score']}%"
#             )

#         with c3:
#             st.metric(
#                 "Confidence",
#                 f"{report['confidence_score']}%"
#             )

#         with c4:
#             st.metric(
#                 "Overall",
#                 f"{report['overall_score']}%"
#             )

#         st.divider()

#     # ---------------- RECOMMENDATION ----------------

#         recommendation = report["recommendation"]

#         if recommendation.lower().startswith("recommend"):

#             st.success(
#                 f"✅ Recommendation : {recommendation}"
#             )

#         elif "hold" in recommendation.lower():

#             st.warning(
#                 f"⚠ Recommendation : {recommendation}"
#             )

#         else:

#             st.error(
#                 f"❌ Recommendation : {recommendation}"
#             )

#         # ---------------- SUMMARY ----------------

#         st.subheader("📝 AI Summary")

#         st.info(
#             report["summary"]
#         )

#         st.divider()

#         import json

#         left, right = st.columns(2)

#         # ---------------- DOWNLOAD ----------------

#         with left:

#             st.download_button(

#                 "📥 Download Interview Report",

#                 data=json.dumps(

#                     report,

#                     indent=4

#                 ),

#                 file_name=f"{candidate_name}_Interview_Report.json",

#                 mime="application/json",

#                 use_container_width=True

#             )

#         # ---------------- EXIT ----------------

#         with right:

#             if st.button(

#                 "🏠 Return to Interview Management",

#                 use_container_width=True

#             ):

#                 st.session_state.ai_interviewer=None

#                 st.session_state.chat_history=[]

#                 st.session_state.current_evaluation=None

#                 st.session_state.final_report=None

#                 st.switch_page(
#                     "pages/7_Interview_Management.py"
#                 )

#                 if st.button("⬅ Return"):

#                     st.session_state.ai_interviewer=None

#                     st.session_state.chat_history=[]

#                     st.session_state.current_evaluation=None

#                     st.session_state.final_report=None

#                     st.switch_page(
#                         "pages/7_Interview_Management.py"
#                     )
# ---------------------------------------------------------------------
# AI Feedback
# ---------------------------------------------------------------------

st.divider()

st.subheader("AI Feedback")

if technical_score is None:
    technical_score = 0

if communication_score is None:
    communication_score = 0

average = int(
    (technical_score + communication_score) / 2
)

if average >= 85:

    ai_feedback_text = """
Strong Hire

Excellent technical ability.

Good communication.

Recommended for next stage.
"""

elif average >= 70:

    ai_feedback_text = """
Hire

Good overall performance.

Minor improvements required.

Proceed to next round.
"""

elif average >= 50:

    ai_feedback_text = """
Hold

Candidate shows potential.

Needs another evaluation.
"""

else:

    ai_feedback_text = """
Reject

Candidate does not currently
meet expectations.
"""

st.metric("Overall Score", f"{average}%")

st.text_area(

    "AI Recommendation",

    ai_feedback_text,

    height=180,

    disabled=True

)


# ---------------------------------------------------------------------
# Candidate Decision
# ---------------------------------------------------------------------

st.divider()

st.subheader("Candidate Decision")

col1, col2, col3, col4 = st.columns(4)

with col1:

    if st.button(
        "Next Round",
        width="stretch"
    ):

        next_round = {

            "Interview Round 1":
                "Interview Round 2",

            "Interview Round 2":
                "Interview Round 3",

            "Interview Round 3":
                "Selected"

        }.get(
            round_name,
            "Interview Round 2"
        )

        conn = get_db_connection()
        cursor = conn.cursor()

        if next_round == "Selected":

            cursor.execute("""

            UPDATE interviews

            SET
                status='Selected'

            WHERE id=?

            """,

            (interview_id,)

            )

        else:

            cursor.execute("""

            UPDATE interviews

            SET

                round_name=?,

                status='Passed'

            WHERE id=?

            """,

            (

                next_round,

                interview_id

            ))

        conn.commit()
        conn.close()

        st.success("Candidate updated.")

        st.rerun()
        with col2:

            if st.button(
                "Select Candidate",
                type="primary",
                width="stretch"
            ):

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""

                UPDATE interviews

                SET

                    status='Selected'

                WHERE id=?

                """,

                (interview_id,)

                )

                conn.commit()
                conn.close()

                st.balloons()
                st.success("Candidate selected successfully.")

                st.rerun()


        with col3:

            if st.button(
                "Hold",
                width="stretch"
            ):

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""

                UPDATE interviews

                SET

                    status='Hold'

                WHERE id=?

                """,

                (interview_id,)

                )

                conn.commit()
                conn.close()

                st.warning("Candidate moved to Hold.")

                st.rerun()


        with col4:

            if st.button(
                "Reject",
                width="stretch"
            ):

                conn = get_db_connection()
                cursor = conn.cursor()

                cursor.execute("""

                UPDATE interviews

                SET

                    status='Rejected'

                WHERE id=?

                """,

                (interview_id,)

                )

                conn.commit()
                conn.close()

                st.error("Candidate rejected.")

                st.rerun()


        # ---------------------------------------------------------------------
        # Offer Management
        # ---------------------------------------------------------------------

        st.divider()

        st.subheader("Offer Management")

        if status in ("Selected", "Offer Sent"):

            offer_letter = f"""
        OFFER LETTER

        Candidate : {candidate_name}

        Role : {role}

        Congratulations!

        We are pleased to offer you the position of
        {role}.

        Joining Mode : Hybrid

        Reporting Manager : HR Team

        Regards,

        Talent Acquisition Team
        """

            st.text_area(

                "Generated Offer Letter",

                offer_letter,

                height=250

            )

            c1, c2 = st.columns(2)

            with c1:

                if st.button(

                    "Send Offer",

                    type="primary",

                    width="stretch"

                ):

                    conn = get_db_connection()
                    cursor = conn.cursor()

                    cursor.execute("""

                    UPDATE interviews

                    SET

                        status='Offer Sent'

                    WHERE id=?

                    """,

                    (interview_id,)

                    )

                    conn.commit()
                    conn.close()

                    st.success("Offer marked as sent.")

                    st.rerun()

            with c2:

                if st.button(

                    "Record Acceptance",

                    width="stretch"

                ):

                    st.success(
                        "Offer acceptance recorded."
                    )

        else:

            st.info(
                "Offer Management becomes available "
                "after candidate selection."
            )


        # ---------------------------------------------------------------------
        # Interview Summary
        # ---------------------------------------------------------------------

        st.divider()

        st.subheader("Interview Summary")

        summary = f"""
        Candidate : {candidate_name}

        Role : {role}

        Round : {round_name}

        Interviewer : {interviewer}

        Interview Date : {interview_date}

        Interview Time : {interview_time}

        Status : {status}

        Technical Score : {technical_score}

        Communication Score : {communication_score}

        Technical Notes

        {technical_notes}

        Communication Notes

        {communication_notes}

        Overall Notes

        {overall_notes}

        Recruiter Feedback

        {feedback}

        AI Recommendation

        {ai_feedback_text}
        """

        st.download_button(

            "Download Interview Report",

            summary,

            file_name=f"{candidate_name}_Interview_Report.txt",

            width="stretch"

        )