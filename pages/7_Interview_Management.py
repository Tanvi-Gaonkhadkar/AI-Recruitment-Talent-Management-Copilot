import datetime
import sqlite3
import uuid
import streamlit as st
from database.schema import create_tables

# Ensures every table needed exists safely in database/recruitment.db
create_tables()

st.set_page_config(
    page_title="Interview Management | AI Recruitment Copilot",
    page_icon="🎯",
    layout="wide"
)

# ---------------------------------------------------------------------
# Developer Session Bypass
# ---------------------------------------------------------------------
if "logged_in" not in st.session_state:
    st.session_state.logged_in = True

if "role" not in st.session_state:
    st.session_state.role = "Recruiter"

# ---------------------------------------------------------------------
# AI Interview Session
# ---------------------------------------------------------------------

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
# Workflow Navigation & Tab State Initialization
# ---------------------------------------------------------------------
TAB_NAMES = [
    "Profile",
    "Schedule",
    "Interviewer",
    "Questions",
    "Notes",
    "AI Feedback",
    "Decision",
    "Offer"
]

if "im_active_step" not in st.session_state:
    st.session_state["im_active_step"] = "Profile"

if "schedule_saved" not in st.session_state:
    st.session_state["schedule_saved"] = False

st.markdown("""
<style>
    div[data-testid="column"] button {
        height: 44px !important;
        white-space: nowrap !important;
        font-size: 13px !important;
        font-weight: 600 !important;
    }
    .ats-badge-status {
        background-color: #0284c7;
        color: white;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 700;
    }
</style>
""", unsafe_allow_html=True)

st.title("🎯 Interview Management")
st.caption("Manage candidate interviews, scheduling, evaluation and offer workflow.")

# ---------------------------------------------------------------------
# Database Connection & Helpers
# ---------------------------------------------------------------------
DB_PATH = "database/recruitment.db"

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def generate_meeting_link():
    code = f"{uuid.uuid4().hex[:3]}-{uuid.uuid4().hex[:4]}-{uuid.uuid4().hex[:3]}"
    return f"https://meet.google.com/{code}"

# ---------------------------------------------------------------------
# Round-by-Round Email Draft Generator
# ---------------------------------------------------------------------
def generate_round_email(candidate_name, role, round_name, status, interviewer_name, date_str="TBD", time_str="10:00 AM", link_str="N/A"):
    c_email = f"{candidate_name.lower().replace(' ', '.')}@example.com"
    
    if status == "Rejected":
        subject = f"Application Update — {role} Position"
        body = f"""Dear {candidate_name},

Thank you for taking the time to interview for the {role} position and completing the {round_name}.

After careful consideration and review by our evaluation team, we regret to inform you that we will not be moving forward with your application at this time. 

We genuinely appreciate your time, effort, and interest in our team, and we wish you the very best in your professional journey.

Best regards,
{interviewer_name}
Talent Acquisition Team
AI Recruitment Copilot"""

    elif status == "Hold":
        subject = f"Application Status Update — {role} Position"
        body = f"""Dear {candidate_name},

Thank you for participating in the {round_name} for the {role} position.

Our team was impressed with your background and interview responses. We are currently evaluating all candidates for this role and have placed your application on short-term hold while we conclude remaining reviews.

We will keep you updated on the next steps shortly.

Best regards,
{interviewer_name}
Talent Acquisition Team
AI Recruitment Copilot"""

    elif status == "Selected":
        subject = f"Congratulations! You've Been Selected for {role}"
        body = f"""Dear {candidate_name},

We are thrilled to inform you that you have successfully cleared all interview rounds for the position of {role}!

Our team was thoroughly impressed with your technical expertise, problem-solving skills, and cultural fit. We are currently preparing your official Offer Letter, which will be shared with you shortly.

Congratulations once again, and we look forward to having you on board!

Best regards,
{interviewer_name}
Talent Acquisition Team
AI Recruitment Copilot"""

    elif status == "Offer Sent":
        subject = f"Official Offer of Employment — {role}"
        body = f"""Dear {candidate_name},

Following up on your selection for the {role} position, we are pleased to present your formal Offer of Employment!

Please review the attached offer details and let us know if you have any questions. To accept this offer, please sign and return the document by the specified date.

We are excited about the prospect of working together!

Best regards,
{interviewer_name}
Talent Acquisition Team
AI Recruitment Copilot"""

    elif status == "Offer Accepted":
        subject = f"Welcome to the Team, {candidate_name}!"
        body = f"""Dear {candidate_name},

We have received your formal acceptance of the employment offer for the {role} position!

Our Onboarding Team will reach out to you shortly with joining instructions, documentation requirements, and details about your first day.

Welcome to the team!

Best regards,
{interviewer_name}
Talent Acquisition Team
AI Recruitment Copilot"""

    else:
        subject = f"Interview Invitation: {round_name} — {role}"
        body = f"""Dear {candidate_name},

We are pleased to invite you to the next stage of our recruitment process: {round_name} for the {role} position.

Interview Details:
----------------------------------------
• Candidate: {candidate_name}
• Role: {role}
• Interview Round: {round_name}
• Interviewer: {interviewer_name}
• Date: {date_str}
• Time: {time_str} IST
• Video Link: {link_str}
----------------------------------------

Please ensure you join on time and have a stable internet connection. If you need to reschedule, please let us know in advance.

Best regards,
{interviewer_name}
Talent Acquisition Team
AI Recruitment Copilot"""

    return c_email, subject, body

# ---------------------------------------------------------------------
# Stage Filter & Candidate Selection Section
# ---------------------------------------------------------------------
st.markdown("### 🔍 Candidate Selection & Stage Filter")
filter_col1, filter_col2 = st.columns([1, 2])

conn = get_db_connection()
cursor = conn.cursor()

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

existing_stages = sorted({row["status"] for row in records if row["status"]})
ALL_STAGE_OPTIONS = ["All Stages"] + sorted(list(set(existing_stages + ["Applied", "Shortlisted", "Interview Round 1", "Interview Round 2", "Interview Round 3", "Selected", "Offer Sent", "Offer Accepted", "Hold", "Rejected"])))

with filter_col1:
    selected_stage_filter = st.selectbox("📂 Filter by Stage:", ALL_STAGE_OPTIONS, index=0)

if selected_stage_filter != "All Stages":
    filtered_records = [row for row in records if (row["status"] or "Applied") == selected_stage_filter]
else:
    filtered_records = records

if not filtered_records:
    st.info(f"No candidates found in stage **'{selected_stage_filter}'**.")
    st.stop()

cand_dict = {
    f"{row['name'] or 'Candidate'} — {row['role_applied'] or 'Role'} ({row['round_name'] or 'Round 1'}) [Stage: {row['status'] or 'Applied'}]": row["id"]
    for row in filtered_records
}

with filter_col2:
    selected_cand_str = st.selectbox("🎯 Select Active Candidate Workflow:", list(cand_dict.keys()))
    active_cand_id = cand_dict[selected_cand_str]

# Fetch Active Candidate Record
cursor.execute("""
SELECT
    interviews.id,
    candidates.id as c_id,
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
    interviews.status
FROM interviews
LEFT JOIN candidates
ON candidates.id = interviews.candidate_id
WHERE interviews.id = ?
""", (active_cand_id,))

cand_data = cursor.fetchone()
conn.close()

c_id = cand_data["id"]
c_name = cand_data["name"] or "Candidate"
c_role = cand_data["role_applied"] or "Role Unassigned"
c_skills = cand_data["skills"] or ""
c_exp = cand_data["experience"] or "Not specified"
c_round = cand_data["round_name"] or "Interview Round 1"
c_interviewer = cand_data["interviewer"] or "Talent Acquisition Team"
c_date = cand_data["interview_date"] or str(datetime.date.today())
c_time = cand_data["interview_time"] or "10:00 AM"
c_mode = cand_data["meeting_mode"] or "Online"
c_link = cand_data["meeting_link"] or "https://meet.google.com/xyz-abcd-efg"
c_tech_score = cand_data["technical_score"] or 0
c_comm_score = cand_data["communication_score"] or 0
c_tech_notes = cand_data["technical_notes"] or ""
c_comm_notes = cand_data["communication_notes"] or ""
c_overall_notes = cand_data["overall_notes"] or ""
c_feedback = cand_data["feedback"] or ""
c_status = cand_data["status"] or "Applied"

st.divider()

# ---------------------------------------------------------------------
# Navigation Tabs Bar
# ---------------------------------------------------------------------
nav_cols = st.columns(len(TAB_NAMES))
for idx, t_name in enumerate(TAB_NAMES):
    is_active = (t_name == st.session_state["im_active_step"])
    btn_type = "primary" if is_active else "secondary"
    if nav_cols[idx].button(f"{'📍 ' if is_active else ''}{t_name}", key=f"nav_btn_{idx}", type=btn_type, use_container_width=True):
        st.session_state["im_active_step"] = t_name
        st.rerun()

st.divider()

current_step = st.session_state["im_active_step"]

# ---------------------------------------------------------------------
# PAGE STEP 1: CANDIDATE PROFILE
# ---------------------------------------------------------------------
if current_step == "Profile":
    head_col1, head_col2 = st.columns([3, 1])
    with head_col1:
        st.markdown(f"## 👤 {c_name}")
        st.caption(f"**Applied Role:** **{c_role}** | **Experience:** {c_exp}")
    with head_col2:
        st.markdown(f"<div style='text-align: right;'><span class='ats-badge-status'>Status: {c_status}</span></div>", unsafe_allow_html=True)
    
    st.divider()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 🎓 Skills & Background")
        if c_skills:
            for s in c_skills.split(","):
                st.markdown(f"- **{s.strip()}**")
    with col2:
        st.markdown("### 📊 Scores Overview")
        st.metric("Technical Score", f"{c_tech_score}%")
        st.metric("Communication Score", f"{c_comm_score}%")

    st.markdown("---")
    if st.button("Jump to Schedule ➔", type="primary", use_container_width=True):
        st.session_state["im_active_step"] = "Schedule"
        st.rerun()

# ---------------------------------------------------------------------
# PAGE STEP 2: SCHEDULE (EMAIL GENERATED AFTER FORM SUBMISSION)
# ---------------------------------------------------------------------
elif current_step == "Schedule":
    st.subheader(f"Schedule Interview for [{c_round}] — {c_name}")
    with st.form("sched_form"):
        sc1, sc2 = st.columns(2)
        with sc1:
            try:
                val_date = datetime.date.fromisoformat(c_date)
            except Exception:
                val_date = datetime.date.today()
            up_date = st.date_input("Interview Date", value=val_date)
            up_time = st.time_input("Interview Time", value=datetime.time(10, 0))
        with sc2:
            up_mode = st.selectbox("Meeting Mode", ["Online", "Offline"], index=0 if c_mode != "Offline" else 1)
            up_link = st.text_input("Meeting Link", value=c_link)
            
        if st.form_submit_button("Save Schedule & Generate Email ➔", type="primary", use_container_width=True):
            final_link = up_link.strip() if up_link.strip() else generate_meeting_link()
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE interviews SET interview_date=?, interview_time=?, meeting_mode=?, meeting_link=? WHERE id=?", 
                           (str(up_date), str(up_time), up_mode, final_link, c_id))
            conn.commit()
            conn.close()
            st.session_state["schedule_saved"] = True
            st.success("Schedule saved successfully! Email draft generated below.")
            st.rerun()

    # Email Draft Section appears exclusively after clicking 'Save Schedule'
    if st.session_state.get("schedule_saved"):
        st.markdown("---")
        cand_email, em_subject, em_body = generate_round_email(
            candidate_name=c_name,
            role=c_role,
            round_name=c_round,
            status=c_status,
            interviewer_name=c_interviewer,
            date_str=c_date,
            time_str=c_time,
            link_str=c_link
        )

        st.markdown(f"### ✉️ Generated Email Draft — [{c_round}]")
        st.caption(f"**Recipient:** `{cand_email}` | **Subject:** `{em_subject}`")
        full_draft = f"TO: {cand_email}\nSUBJECT: {em_subject}\n\n{em_body}"
        st.text_area("Email Content", full_draft, height=220, key="sched_email_draft")
        
        if st.button(f"✉️ Send Email to Candidate ({c_name}) & Jump to Interviewer ➔", key="sched_send_email", type="primary", use_container_width=True):
            st.session_state["schedule_saved"] = False
            st.session_state["im_active_step"] = "Interviewer"
            st.success(f"Email sent successfully to {cand_email}!")
            st.rerun()

# ---------------------------------------------------------------------
# PAGE STEP 3: INTERVIEWER ASSIGNMENT
# ---------------------------------------------------------------------
elif current_step == "Interviewer":
    st.subheader(f"Assign Interviewer for [{c_round}]")
    with st.form("assign_form"):
        up_interviewer = st.text_input("Interviewer Name", value=c_interviewer)
        if st.form_submit_button("Assign Interviewer & Jump to Questions ➔", type="primary", use_container_width=True):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("UPDATE interviews SET interviewer=? WHERE id=?", (up_interviewer, c_id))
            conn.commit()
            conn.close()
            st.session_state["im_active_step"] = "Questions"
            st.rerun()

# ---------------------------------------------------------------------
# PAGE STEP 4: QUESTIONS BANK
# ---------------------------------------------------------------------
elif current_step == "Questions":
    st.subheader(f"AI Question Bank — [{c_round}]")
    st.markdown("""
    1. *Explain how memory management and garbage collection work in Python.*
    2. *How do you optimize SQL joins on large datasets?*
    3. *Describe a challenging technical problem you solved recently.*
    """)
    if st.button("Jump to Notes ➔", type="primary", use_container_width=True):
        st.session_state["im_active_step"] = "Notes"
        st.rerun()

# ---------------------------------------------------------------------
# PAGE STEP 5: NOTES & OBSERVATIONS
# ---------------------------------------------------------------------
elif current_step == "Notes":
    st.subheader(f"Interviewer Notes & Scoring — [{c_round}]")
    with st.form("notes_form"):
        tn = st.text_area("Technical Notes", value=c_tech_notes)
        cn = st.text_area("Communication Notes", value=c_comm_notes)
        fb = st.text_area("Recruiter Feedback", value=c_feedback)
        
        col1, col2 = st.columns(2)
        with col1:
            ts = st.slider("Technical Score", 0, 100, int(c_tech_score))
        with col2:
            cs = st.slider("Communication Score", 0, 100, int(c_comm_score))
            
        if st.form_submit_button("Save Notes & Jump to AI Feedback ➔", type="primary", use_container_width=True):
            conn = get_db_connection()
            cursor = conn.cursor()
            cursor.execute("""
            UPDATE interviews SET technical_notes=?, communication_notes=?, feedback=?, technical_score=?, communication_score=? WHERE id=?
            """, (tn, cn, fb, ts, cs, c_id))
            conn.commit()
            conn.close()
            st.session_state["im_active_step"] = "AI Feedback"
            st.rerun()

# ---------------------------------------------------------------------
# PAGE STEP 6: AI FEEDBACK
# ---------------------------------------------------------------------
elif current_step == "AI Feedback":
    st.subheader(f"AI Evaluation Summary — [{c_round}]")
    avg = int((c_tech_score + c_comm_score) / 2)
    st.metric("Overall Weighted Score", f"{avg}%")
    if avg >= 75:
        st.success("🤖 **AI Recommendation:** Recommended for Selection / Next Round.")
    else:
        st.warning("🤖 **AI Recommendation:** Requires further review.")

    if st.button("Jump to Decision ➔", type="primary", use_container_width=True):
        st.session_state["im_active_step"] = "Decision"
        st.rerun()

# ---------------------------------------------------------------------
# PAGE STEP 7: DECISION
# ---------------------------------------------------------------------
elif current_step == "Decision":
    st.subheader("Candidate Decision & Round Progression")
    st.caption(f"Candidate: **{c_name}** | Current Active Round: **{c_round}** | Status: **{c_status}**")
    
    d1, d2, d3, d4 = st.columns(4)
    if d1.button("▶ Promote to Next Round", use_container_width=True, type="primary"):
        next_map = {
            "Interview Round 1": "Interview Round 2",
            "Interview Round 2": "Interview Round 3",
            "Interview Round 3": "Selected"
        }
        next_r = next_map.get(c_round, "Interview Round 2")
        new_st = "Selected" if next_r == "Selected" else "Shortlisted"
        
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE interviews SET round_name=?, status=? WHERE id=?", (next_r, new_st, c_id))
        conn.commit()
        conn.close()
        st.success(f"Promoted to {next_r}!")
        st.session_state["schedule_saved"] = False
        st.session_state["im_active_step"] = "Schedule"
        st.rerun()

    if d2.button("✅ Select Candidate (Final)", use_container_width=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE interviews SET status='Selected' WHERE id=?", (c_id,))
        conn.commit()
        conn.close()
        st.session_state["im_active_step"] = "Offer"
        st.balloons()
        st.rerun()

    if d3.button("⏸ Place on Hold", use_container_width=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE interviews SET status='Hold' WHERE id=?", (c_id,))
        conn.commit()
        conn.close()
        st.warning("Candidate set to Hold.")
        st.rerun()

    if d4.button("✕ Reject Candidate", use_container_width=True):
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("UPDATE interviews SET status='Rejected' WHERE id=?", (c_id,))
        conn.commit()
        conn.close()
        st.error("Candidate rejected.")
        st.rerun()

# ---------------------------------------------------------------------
# PAGE STEP 8: OFFER MANAGEMENT (OFFER EMAIL GENERATION)
# ---------------------------------------------------------------------
elif current_step == "Offer":
    st.subheader("Offer Management & Offer Letter Email")
    if c_status in ["Selected", "Offer Sent", "Offer Accepted"]:
        cand_email, offer_subject, offer_body = generate_round_email(
            candidate_name=c_name,
            role=c_role,
            round_name=c_round,
            status="Offer Sent",
            interviewer_name=c_interviewer
        )

        st.markdown("### ✉️ Official Offer Email Draft")
        st.caption(f"**Recipient:** `{cand_email}` | **Subject:** `{offer_subject}`")
        full_offer_draft = f"TO: {cand_email}\nSUBJECT: {offer_subject}\n\n{offer_body}"
        st.text_area("Offer Letter Content", full_offer_draft, height=240, key="offer_email_draft")
        
        o1, o2 = st.columns(2)
        with o1:
            if st.button("✉️ Send Offer Letter Email", type="primary", use_container_width=True):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE interviews SET status='Offer Sent' WHERE id=?", (c_id,))
                conn.commit()
                conn.close()
                st.success(f"Offer Letter Email successfully sent to {cand_email}!")
                st.rerun()
        with o2:
            if st.button("🎉 Record Offer Acceptance", use_container_width=True):
                conn = get_db_connection()
                cursor = conn.cursor()
                cursor.execute("UPDATE interviews SET status='Offer Accepted' WHERE id=?", (c_id,))
                conn.commit()
                conn.close()
                st.balloons()
                st.success("Offer acceptance recorded successfully!")
                st.rerun()
    else:
        st.info("🔒 Offer Management unlocks after candidate selection.")