import re
import io
import csv
from datetime import datetime, date, timedelta

import streamlit as st

from backend.onboarding_service import (
    get_connection,
    get_onboarding_candidates,
    get_candidate,
    start_onboarding,
    update_progress,
    approve_candidate,
    reject_candidate,
    complete_onboarding,
    create_employee,
    get_missing_documents,
    get_missing_documents_for_all_candidates,
    get_employee_by_candidate,
    REQUIRED_ONBOARDING_DOCUMENTS,
)

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

if st.session_state.role != "Recruiter":
    st.error("🚫 Access Denied. This module is available only to Recruiters.")
    st.stop()

# ==========================================================
# PAGE CONFIG
# ==========================================================

st.set_page_config(
    page_title="Employee Onboarding",
    page_icon="📋",
    layout="wide"
)

# ==========================================================
# STYLES
# ==========================================================

st.markdown(
    """
    <style>
    .badge {
        display: inline-block;
        padding: 4px 14px;
        border-radius: 999px;
        font-size: 0.78rem;
        font-weight: 600;
        letter-spacing: 0.01em;
        white-space: nowrap;
    }
    .badge-success { background:#DCFCE7; color:#166534; }
    .badge-warning { background:#FEF3C7; color:#92400E; }
    .badge-danger  { background:#FEE2E2; color:#991B1B; }
    .badge-info    { background:#DBEAFE; color:#1E40AF; }
    .badge-neutral { background:#F1F5F9; color:#334155; }

    .candidate-name {
        font-size: 1.1rem;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 0.1rem;
    }
    .candidate-sub {
        color: #64748B;
        font-size: 0.85rem;
    }
    .selected-tag {
        color: #166534;
        font-size: 0.78rem;
        font-weight: 700;
    }
    .section-caption {
        color: #64748B;
        font-size: 0.85rem;
        margin-bottom: 0.6rem;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ==========================================================
# DATA ACCESS HELPERS
# ----------------------------------------------------------
# onboarding_service.py exposes accessors for candidates and
# the onboarding record. resume_analysis, candidate_documents,
# document_verification and onboarding_timeline do not yet have
# dedicated service functions, so they are read here through the
# shared get_connection() factory using small, parameterized,
# single-purpose helpers.
# ==========================================================

def fetch_latest_ats_scores():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT
            c.id,
            COALESCE(MAX(ra.ats_score),0)

        FROM candidates c

        LEFT JOIN resume_analysis ra

        ON LOWER(ra.resume_name)
           LIKE '%' || LOWER(REPLACE(c.name,' ','_')) || '%'

        GROUP BY c.id

    """)

    rows = cursor.fetchall()

    conn.close()

    return {row[0]: row[1] for row in rows}

def fetch_resume_analysis(candidate_id):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        SELECT

            ra.ats_score,
            ra.summary,
            ra.matched_skills,
            ra.missing_skills,
            ra.recommendation

        FROM resume_analysis ra

        JOIN candidates c

        ON LOWER(ra.resume_name)
           LIKE '%' || LOWER(REPLACE(c.name,' ','_')) || '%'

        WHERE c.id=?

        LIMIT 1

    """, (candidate_id,))

    row = cursor.fetchone()

    conn.close()

    return row


def fetch_candidate_documents(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            id,
            employee_id,
            document_name,
            file_path,
            upload_status,
            verification_status,
            uploaded_at
        FROM candidate_documents
        WHERE candidate_id = ?
        ORDER BY uploaded_at DESC
    """, (candidate_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def set_document_verification_status(document_id, verification_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE candidate_documents
        SET verification_status = ?
        WHERE id = ?
    """, (verification_status, document_id))
    conn.commit()
    conn.close()


def set_document_upload_status(document_id, upload_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        UPDATE candidate_documents
        SET upload_status = ?
        WHERE id = ?
    """, (upload_status, document_id))
    conn.commit()
    conn.close()


def fetch_document_verification(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT document_name, trust_score, fraud_probability, ai_result, remarks, verified_at
        FROM document_verification
        WHERE candidate_id = ?
        ORDER BY verified_at DESC
    """, (candidate_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def fetch_onboarding_timeline(candidate_id):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT event_name, event_status, event_time
        FROM onboarding_timeline
        WHERE candidate_id = ?
        ORDER BY event_time ASC
    """, (candidate_id,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def log_timeline_event(candidate_id, event_name, event_status):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO onboarding_timeline (candidate_id, event_name, event_status)
        VALUES (?, ?, ?)
    """, (candidate_id, event_name, event_status))
    conn.commit()
    conn.close()


# ==========================================================
# DOMAIN HELPERS
# ==========================================================

DEPARTMENT_KEYWORDS = [
    ("data scien", "Data Science"),
    ("data", "Data Science"),
    ("machine learning", "AI/ML"),
    ("ai", "AI/ML"),
    ("ml", "AI/ML"),
    ("engineer", "Engineering"),
    ("developer", "Engineering"),
    ("software", "Engineering"),
    ("qa", "Quality Assurance"),
    ("test", "Quality Assurance"),
    ("hr", "Human Resources"),
    ("human resource", "Human Resources"),
    ("sales", "Sales"),
    ("marketing", "Marketing"),
    ("design", "Design"),
    ("product", "Product"),
    ("finance", "Finance"),
]


def derive_department(role_applied):
    if not role_applied:
        return "Not Assigned"
    role = role_applied.lower()
    for keyword, department in DEPARTMENT_KEYWORDS:
        if keyword in role:
            return department
    return "Not Assigned"


def derive_candidate_type(experience_text):
    if not experience_text:
        return "Fresher"
    text = experience_text.strip().lower()
    if "fresher" in text or "no experience" in text:
        return "Fresher"
    match = re.search(r"(\d+(\.\d+)?)", text)
    if match:
        try:
            years = float(match.group(1))
            return "Fresher" if years <= 0 else "Experienced"
        except ValueError:
            pass
    return "Experienced"


def stage_kind(stage_text):
    if not stage_text:
        return "neutral"
    s = stage_text.lower()
    if "complet" in s or "approved" in s:
        return "success"
    if "reject" in s:
        return "danger"
    if "pending" in s or "not started" in s:
        return "neutral"
    return "info"


def render_badge(label, kind):
    st.markdown(
        f'<span class="badge badge-{kind}">{label}</span>',
        unsafe_allow_html=True
    )


def parse_date_safe(value):
    if not value:
        return None
    formats = ["%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y", "%Y/%m/%d"]
    for fmt in formats:
        try:
            return datetime.strptime(str(value).strip(), fmt).date()
        except ValueError:
            continue
    return None


# ==========================================================
# RECORD BUILDERS
# ==========================================================

def build_candidate_records():
    rows = get_onboarding_candidates()
    ats_map = fetch_latest_ats_scores()
    missing_docs_map = get_missing_documents_for_all_candidates()

    records = []
    for row in rows:
        candidate_id = row[0]
        role_applied = row[4]
        experience = row[5]
        missing_documents = missing_docs_map.get(candidate_id, [])

        records.append({
            "id": candidate_id,
            "name": row[1] or "Unnamed Candidate",
            "email": row[2] or "-",
            "phone": row[3] or "-",
            "role": role_applied or "-",
            "experience": experience or "-",
            "skills": row[6] or "",
            "status": row[7] or "-",
            "onboarding_status": row[8] or "Not Started",
            "progress": row[9] if row[9] is not None else 0,
            "joining_date": row[10] or "Not Assigned",
            "hr_status": row[11] or "Pending",
            "department": derive_department(role_applied),
            "type": derive_candidate_type(experience),
            "ats": ats_map.get(candidate_id, 0),
            "missing_documents": missing_documents,
        })
    return records


def build_selected_candidate(candidate_id):
    row = get_candidate(candidate_id)
    if not row:
        return None

    role_applied = row[4]
    experience = row[5]

    return {
        "id": row[0],
        "name": row[1] or "Unnamed Candidate",
        "email": row[2] or "-",
        "phone": row[3] or "-",
        "role": role_applied or "-",
        "experience": experience or "-",
        "skills": row[6] or "",
        "resume_path": row[7],
        "status": row[8] or "-",
        "onboarding_status": row[9] or "Not Started",
        "progress": row[10] if row[10] is not None else 0,
        "joining_date": row[11] or "Not Assigned",
        "hr_status": row[12] or "Pending",
        "department": derive_department(role_applied),
        "type": derive_candidate_type(experience),
        "missing_documents": get_missing_documents(row[0]),
    }


def compute_kpis(records):
    total = len(records)
    pending = sum(
        1 for r in records
        if r["onboarding_status"] not in ("Completed", "Rejected")
    )
    documents_stage = sum(
        1 for r in records
        if 10 <= (r["progress"] or 0) < 60
    )
    ai_review_stage = sum(
        1 for r in records
        if 60 <= (r["progress"] or 0) < 100
    )
    completed = sum(
        1 for r in records
        if r["onboarding_status"] == "Completed"
    )

    missing_documents_count = sum(
        1 for r in records
        if r["missing_documents"] and r["onboarding_status"] not in ("Completed", "Rejected")
    )

    today = date.today()
    week_ahead = today + timedelta(days=7)
    joining_this_week = 0
    for r in records:
        parsed = parse_date_safe(r["joining_date"])
        if parsed and today <= parsed <= week_ahead:
            joining_this_week += 1

    avg_progress = int(sum((r["progress"] or 0) for r in records) / total) if total else 0

    return {
        "total": total,
        "pending": pending,
        "documents_stage": documents_stage,
        "ai_review_stage": ai_review_stage,
        "joining_this_week": joining_this_week,
        "completed": completed,
        "avg_progress": avg_progress,
        "missing_documents_count": missing_documents_count,
    }


def build_export_report(candidate, documents, verifications, timeline):
    buffer = io.StringIO()
    writer = csv.writer(buffer)

    writer.writerow(["Onboarding Report"])
    writer.writerow(["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    writer.writerow(["Candidate ID", candidate["id"]])
    writer.writerow(["Name", candidate["name"]])
    writer.writerow(["Email", candidate["email"]])
    writer.writerow(["Phone", candidate["phone"]])
    writer.writerow(["Role Applied", candidate["role"]])
    writer.writerow(["Department", candidate["department"]])
    writer.writerow(["Candidate Type", candidate["type"]])
    writer.writerow(["Status", candidate["status"]])
    writer.writerow(["Onboarding Status", candidate["onboarding_status"]])
    writer.writerow(["HR Status", candidate["hr_status"]])
    writer.writerow(["Progress", f'{candidate["progress"]}%'])
    writer.writerow(["Joining Date", candidate["joining_date"]])
    writer.writerow([])

    writer.writerow(["Missing Documents"])
    missing_documents = candidate.get("missing_documents") or []
    if missing_documents:
        for doc_name in missing_documents:
            writer.writerow([doc_name, "Not Uploaded"])
    else:
        writer.writerow(["None - all required documents uploaded"])
    writer.writerow([])

    writer.writerow(["Documents"])
    writer.writerow(["Document Name", "Upload Status", "Verification Status", "Uploaded At"])
    for doc in documents:
        writer.writerow([doc[2], doc[4], doc[5], doc[6]])
    writer.writerow([])

    writer.writerow(["AI Verification"])
    writer.writerow(["Document Name", "Trust Score", "Fraud Probability", "AI Result", "Remarks", "Verified At"])
    for v in verifications:
        writer.writerow([v[0], v[1], v[2], v[3], v[4], v[5]])
    writer.writerow([])

    writer.writerow(["Timeline"])
    writer.writerow(["Event", "Status", "Time"])
    for event in timeline:
        writer.writerow([event[0], event[1], event[2]])

    return buffer.getvalue()


# ==========================================================
# SESSION STATE
# ==========================================================

if "selected_candidate_id" not in st.session_state:
    st.session_state.selected_candidate_id = None

if "email_log" not in st.session_state:
    st.session_state.email_log = {}


def select_candidate(candidate_id):
    st.session_state.selected_candidate_id = candidate_id


def send_email(candidate_id, subject):
    log = st.session_state.email_log.setdefault(candidate_id, [])
    log.append({
        "subject": subject,
        "status": "Sent",
        "timestamp": datetime.now().strftime("%d %b %Y, %I:%M %p"),
    })


# ==========================================================
# LOAD DATA
# ==========================================================

all_candidates = build_candidate_records()

if st.session_state.selected_candidate_id is None and all_candidates:
    st.session_state.selected_candidate_id = all_candidates[0]["id"]

kpis = compute_kpis(all_candidates)

# ==========================================================
# HEADER
# ==========================================================

with st.sidebar:
    st.header("🤖 AI Modules")
    st.success("Missing Document Detection AI")
    st.success("AI Document Verification (Fraud/Trust Score)")
    st.success("Employee ID Generator")
    st.info("Powered by Local Llama 3.2")

st.title("📋 Employee Onboarding")
st.caption(
    "Manage offers, onboarding documents, AI verification and employee creation."
)

st.divider()

# ==========================================================
# KPI DASHBOARD
# ==========================================================

k1, k2, k3, k4, k5, k6, k7 = st.columns(7)

with k1:
    st.metric("Total In Pipeline", kpis["total"])

with k2:
    st.metric("Pending", kpis["pending"])

with k3:
    st.metric("Documents Stage", kpis["documents_stage"])

with k4:
    st.metric("AI Review Stage", kpis["ai_review_stage"])

with k5:
    st.metric("Joining This Week", kpis["joining_this_week"])

with k6:
    st.metric("Completed", kpis["completed"])

with k7:
    st.metric("Missing Documents", kpis["missing_documents_count"])

st.divider()

# ==========================================================
# FILTERS
# ==========================================================

department_options = ["All"] + sorted({r["department"] for r in all_candidates})
stage_options = ["All"] + sorted({r["onboarding_status"] for r in all_candidates})

f1, f2, f3, f4 = st.columns([2, 1, 1, 1])

with f1:
    search = st.text_input(
        "Search Candidate",
        placeholder="Search by candidate name...",
        key="search_candidate_input"
    )

with f2:
    department_filter = st.selectbox(
        "Department",
        department_options,
        key="department_filter"
    )

with f3:
    type_filter = st.selectbox(
        "Candidate Type",
        ["All", "Experienced", "Fresher"],
        key="type_filter"
    )

with f4:
    stage_filter = st.selectbox(
        "Stage",
        stage_options,
        key="stage_filter"
    )

filtered_candidates = []
for candidate in all_candidates:
    if search and search.lower() not in candidate["name"].lower():
        continue
    if department_filter != "All" and candidate["department"] != department_filter:
        continue
    if type_filter != "All" and candidate["type"] != type_filter:
        continue
    if stage_filter != "All" and candidate["onboarding_status"] != stage_filter:
        continue
    filtered_candidates.append(candidate)

st.divider()

# ==========================================================
# LAYOUT: CANDIDATE QUEUE + AI COMMAND CENTER
# ==========================================================

left, right = st.columns([2.3, 1])

with left:
    st.subheader("Candidate Queue")

    if not filtered_candidates:
        st.info("No candidates found.")

    for candidate in filtered_candidates:
        is_selected = candidate["id"] == st.session_state.selected_candidate_id

        with st.container(border=True):
            c1, c2 = st.columns([4, 1])

            with c1:
                if is_selected:
                    st.markdown('<span class="selected-tag">● CURRENTLY OPEN</span>', unsafe_allow_html=True)
                st.markdown(f'<div class="candidate-name">{candidate["name"]}</div>', unsafe_allow_html=True)
                st.markdown(f'<div class="candidate-sub">{candidate["role"]}</div>', unsafe_allow_html=True)
                st.caption(f'{candidate["department"]} • {candidate["type"]}')
                if candidate["missing_documents"]:
                    st.caption(f'⚠️ Missing: {", ".join(candidate["missing_documents"])}')

            with c2:
                st.metric("ATS", f'{candidate["ats"]}%')

            st.progress(min(max(candidate["progress"] or 0, 0), 100) / 100)

            b1, b2, b3, b4 = st.columns([2, 2, 2, 1.4])

            with b1:
                st.caption("Stage")
                render_badge(candidate["onboarding_status"], stage_kind(candidate["onboarding_status"]))

            with b2:
                st.caption("Joining")
                st.write(candidate["joining_date"])

            with b3:
                st.caption("Progress")
                st.write(f'{candidate["progress"]}%')

            with b4:
                st.button(
                    "Open",
                    key=f"open_{candidate['id']}",
                    use_container_width=True,
                    on_click=select_candidate,
                    args=(candidate["id"],)
                )

with right:
    st.subheader("🤖 AI Command Center")

    missing_docs_candidates = [
        r for r in all_candidates if (r["progress"] or 0) < 60 and r["onboarding_status"] not in ("Completed", "Rejected")
    ]
    approval_waiting = [
        r for r in all_candidates if r["hr_status"] == "Pending" and (r["progress"] or 0) >= 60
    ]

    st.info(
        f"""
**AI Alerts**

- {len(approval_waiting)} candidate(s) waiting on HR approval
- {len(missing_docs_candidates)} candidate(s) still in document/verification stage
- {kpis['missing_documents_count']} candidate(s) missing required documents
- {kpis['joining_this_week']} candidate(s) joining this week
- {kpis['completed']} onboarding(s) fully completed
"""
    )

    st.divider()

    st.metric("Average Progress", f'{kpis["avg_progress"]}%')
    st.metric("Pending HR Approval", len(approval_waiting))
    st.metric("Ready To Join", kpis["completed"])

    if kpis["missing_documents_count"] > 0:
        st.divider()
        st.markdown("**📂 Missing Documents**")
        for r in all_candidates:
            if r["missing_documents"] and r["onboarding_status"] not in ("Completed", "Rejected"):
                st.caption(f'**{r["name"]}** — {", ".join(r["missing_documents"])}')

st.divider()

# ==========================================================
# SELECTED CANDIDATE
# ==========================================================

if st.session_state.selected_candidate_id is None:
    st.info("No onboarding candidates available yet.")
    st.stop()

selected = build_selected_candidate(st.session_state.selected_candidate_id)

if selected is None:
    st.warning("No onboarding candidate found.")
    st.stop()

# The onboarding row only gets created by start_onboarding(). All other
# service functions (approve_candidate, reject_candidate, update_progress,
# create_employee) only UPDATE an existing row and will silently affect
# zero rows if it doesn't exist yet. To prevent that class of silent
# no-op, we ensure the row exists the moment a candidate is opened.
if selected["progress"] in (0, None) and selected["onboarding_status"] in (None, "Not Started"):
    default_joining_date = (
        selected["joining_date"]
        if selected["joining_date"] not in (None, "Not Assigned")
        else date.today().strftime("%Y-%m-%d")
    )
    start_onboarding(selected["id"], default_joining_date)
    selected = build_selected_candidate(selected["id"])

st.header("Candidate Workspace")
st.caption(f'{selected["name"]} • {selected["role"]} • {selected["department"]}')

overview_tab, documents_tab, ai_tab, timeline_tab, email_tab = st.tabs(
    ["Overview", "Document Review", "AI Verification", "Timeline", "Email Center"]
)

# ==========================================================
# OVERVIEW TAB
# ==========================================================

with overview_tab:
    left_col, right_col = st.columns([2, 1])

    with left_col:
        st.subheader("Candidate Information")

        c1, c2 = st.columns(2)

        with c1:
            st.markdown("**Candidate ID**")
            st.write(selected["id"])

            st.markdown("**Candidate Name**")
            st.write(selected["name"])

            st.markdown("**Email Address**")
            st.write(selected["email"])

            st.markdown("**Phone Number**")
            st.write(selected["phone"])

        with c2:
            st.markdown("**Job Role**")
            st.write(selected["role"])

            st.markdown("**Department**")
            st.write(selected["department"])

            st.markdown("**Candidate Type**")
            st.write(selected["type"])

            st.markdown("**Joining Date**")
            st.write(selected["joining_date"])

            st.markdown("**Current Stage**")
            render_badge(selected["onboarding_status"], stage_kind(selected["onboarding_status"]))

    with right_col:
        st.subheader("Resume Summary")

        resume_row = fetch_resume_analysis(selected["id"])

        if resume_row:
            ats_score, summary, skills_csv, missing_skills, recommendation = resume_row

            st.metric("ATS Score", f'{ats_score if ats_score is not None else 0}%')

            st.success(f'Experience: {selected["experience"]}')
            st.info(summary if summary else "No resume summary available.")

            st.markdown("### Skills")
            skill_list = [s.strip() for s in (skills_csv or "").split(",") if s.strip()]
            if skill_list:
                for skill in skill_list:
                    st.success(skill)
            else:
                st.caption("No skills recorded.")

            if missing_skills:
                st.markdown("### Missing Skills")
                for skill in [s.strip() for s in missing_skills.split(",") if s.strip()]:
                    st.warning(skill)

            if recommendation:
                st.markdown("### Recommendation")
                st.write(recommendation)
        else:
            st.info("No resume analysis available yet for this candidate.")

    st.divider()

    st.subheader("Resume vs Job Description Match")

    if resume_row:
        ats_score = resume_row[0] or 0
        missing_skills_text = resume_row[3] or ""
        skills_text = resume_row[2] or ""

        skill_count = len([s for s in skills_text.split(",") if s.strip()])
        missing_count = len([s for s in missing_skills_text.split(",") if s.strip()])
        skills_match = int((skill_count / (skill_count + missing_count)) * 100) if (skill_count + missing_count) else ats_score

        m1, m2 = st.columns(2)
        with m1:
            st.metric("Overall ATS Match", f'{ats_score}%')
        with m2:
            st.metric("Skills Match", f'{skills_match}%')

        st.progress(min(max(ats_score, 0), 100) / 100)
    else:
        st.caption("Match score will appear once resume analysis is available.")

    st.divider()

    st.subheader("Onboarding Progress")

    st.progress(min(max(selected["progress"] or 0, 0), 100) / 100)
    st.caption(f'{selected["progress"]}% Completed')

    p1, p2, p3, p4, p5 = st.columns(5)

    with p1:
        st.success("Offer")

    with p2:
        if selected["progress"] >= 10:
            st.success("Accepted")
        else:
            st.warning("Accepted")

    with p3:
        if selected["progress"] >= 60:
            st.success("Documents")
        else:
            st.warning("Documents")

    with p4:
        if selected["progress"] >= 80:
            st.success("AI Verification")
        else:
            st.warning("AI Verification")

    with p5:
        if selected["progress"] >= 100:
            st.success("Completed")
        else:
            st.warning("HR Approval")

    st.divider()

    st.subheader("Quick Actions")

    st.text_input(
        "Assign Manager (used when creating the employee record)",
        key="assign_manager_input",
        placeholder="e.g. Priya Sharma"
    )

    q1, q2, q3, q4, q5 = st.columns(5)

    with q1:
        with st.popover("Generate Offer", use_container_width=True):
            joining_date_input = st.date_input(
                "Joining Date",
                value=date.today(),
                key="offer_joining_date"
            )
            if st.button("Confirm Offer", key="confirm_generate_offer", use_container_width=True):
                start_onboarding(selected["id"], joining_date_input.strftime("%Y-%m-%d"))
                log_timeline_event(selected["id"], "Offer Letter Generated", "Completed")
                send_email(selected["id"], "Offer Letter")
                st.success("Offer generated successfully.")
                st.rerun()

    with q2:
        if st.button("Request Documents", key="request_documents", use_container_width=True):
            log_timeline_event(selected["id"], "Document Upload Requested", "Pending")
            send_email(selected["id"], "Document Upload Request")
            st.success("Document request email sent.")
            st.rerun()

    with q3:
        if st.button("Approve", key="quick_approve_candidate", use_container_width=True):
            approve_candidate(selected["id"])
            log_timeline_event(selected["id"], "HR Final Approval", "Completed")
            st.success("Candidate Approved Successfully.")
            st.rerun()

    with q4:
        if st.button("Reject", key="quick_reject_candidate", use_container_width=True):
            reject_candidate(selected["id"])
            log_timeline_event(selected["id"], "Candidate Rejected", "Completed")
            st.warning("Candidate Rejected.")
            st.rerun()

    with q5:
        if st.button("Create Employee", key="quick_create_employee", use_container_width=True):
            manager_name = st.session_state.get("assign_manager_input", "").strip()
            if create_employee(selected["id"], manager=manager_name):
                log_timeline_event(selected["id"], "Employee Record Created", "Completed")
                employee_details = get_employee_by_candidate(selected["id"])
                employee_code = employee_details.get("employee_code") if employee_details else None
                if employee_code:
                    st.success(
                        f"Employee Created Successfully.\n\nEmployee Code: {employee_code}"
                    )
                else:
                    st.success("Employee Created Successfully.")
                st.rerun()
            else:
                st.error("Unable to create employee.")

    st.divider()

    st.subheader("Manual Progress Override")

    progress_col, button_col = st.columns([4, 1])

    with progress_col:
        new_progress = st.slider(
            "Onboarding Progress",
            min_value=0,
            max_value=100,
            value=int(selected["progress"] or 0),
            key="progress_override_slider"
        )

    with button_col:
        st.write("")
        st.write("")
        if st.button("Update", key="update_progress_button", use_container_width=True):
            update_progress(selected["id"], new_progress)
            log_timeline_event(selected["id"], f"Progress Updated to {new_progress}%", "Completed")
            st.success("Progress updated.")
            st.rerun()

# ==========================================================
# DOCUMENT REVIEW TAB
# ==========================================================

with documents_tab:
    st.subheader("📂 Document Review")
    st.markdown(
        '<div class="section-caption">Candidates upload their own documents. HR can only review, '
        'approve, reject or request re-upload.</div>',
        unsafe_allow_html=True
    )

    documents = fetch_candidate_documents(selected["id"])
    missing_documents = selected["missing_documents"]

    st.markdown("#### 🚩 Missing Documents")

    if missing_documents:
        st.warning(
            f"{len(missing_documents)} of {len(REQUIRED_ONBOARDING_DOCUMENTS)} required documents "
            "have not been uploaded yet."
        )
        mcols = st.columns(min(len(missing_documents), 4) or 1)
        for i, doc_name in enumerate(missing_documents):
            with mcols[i % len(mcols)]:
                render_badge(doc_name, "danger")

        if st.button("📧 Send Missing Document Reminder", key="send_missing_doc_reminder", use_container_width=True):
            send_email(
                selected["id"],
                f'Missing Documents: {", ".join(missing_documents)}'
            )
            log_timeline_event(
                selected["id"],
                f'Missing Document Reminder Sent: {", ".join(missing_documents)}',
                "Pending"
            )
            st.success("Reminder email sent for missing documents.")
            st.rerun()
    else:
        st.success("All required documents have been uploaded.")

    st.divider()

    if not documents:
        st.info("Candidate has not uploaded any documents yet.")
    else:
        approved_count = sum(1 for d in documents if d[4] == "Approved")
        completion = int((approved_count / len(documents)) * 100)

        st.metric("Approved Documents", f'{approved_count} / {len(documents)}')
        st.progress(completion / 100)

        st.divider()

        for doc in documents:

            (
                doc_id,
                employee_id,
                document_name,
                file_path,
                upload_status,
                verification_status,
                uploaded_at
            ) = doc

            with st.container(border=True):
                d1, d2, d3 = st.columns([3, 2, 3])

                with d1:
                    st.markdown(f"**{document_name}**")
                    st.caption(f"Uploaded: {uploaded_at or 'Unknown'}")
                    if file_path:
                        st.caption(f"File: {file_path}")

                with d2:
                    st.caption("Upload Status")
                    render_badge(upload_status or "Pending", stage_kind(upload_status))
                    st.caption("Verification Status")
                    render_badge(verification_status or "Pending", stage_kind(verification_status))

                with d3:
                    a1, a2, a3 = st.columns(3)

                    with a1:
                        if st.button("Approve", key=f"approve_doc_{doc_id}", use_container_width=True):
                            set_document_verification_status(doc_id, "Approved")
                            log_timeline_event(selected["id"], f"Document Approved: {document_name}", "Completed")
                            st.success(f"{document_name} approved.")
                            st.rerun()

                    with a2:
                        if st.button("Reject", key=f"reject_doc_{doc_id}", use_container_width=True):
                            set_document_verification_status(doc_id, "Rejected")
                            log_timeline_event(selected["id"], f"Document Rejected: {document_name}", "Completed")
                            st.warning(f"{document_name} rejected.")
                            st.rerun()

                    with a3:
                        if st.button("Re-upload", key=f"reupload_doc_{doc_id}", use_container_width=True):
                            set_document_upload_status(doc_id, "Re-upload Requested")
                            set_document_verification_status(doc_id, "Pending")
                            log_timeline_event(selected["id"], f"Re-upload Requested: {document_name}", "Pending")
                            send_email(selected["id"], f"Re-upload Request: {document_name}")
                            st.info(f"Re-upload requested for {document_name}.")
                            st.rerun()

# ==========================================================
# AI VERIFICATION TAB
# ==========================================================

with ai_tab:
    st.subheader("🤖 AI Verification Dashboard")

    verifications = fetch_document_verification(selected["id"])

    if not verifications:
        st.info("No AI verification records found for this candidate yet.")
    else:
        trust_scores = [v[1] for v in verifications if v[1] is not None]
        fraud_scores = [v[2] for v in verifications if v[2] is not None]

        avg_trust = round(sum(trust_scores) / len(trust_scores), 1) if trust_scores else 0
        avg_fraud = round(sum(fraud_scores) / len(fraud_scores), 1) if fraud_scores else 0
        # fraud_probability is stored and displayed as a percentage (0-100),
        # so the flag threshold must be on the same scale (50 = 50%), not 0.5.
        FRAUD_FLAG_THRESHOLD_PERCENT = 50

        flagged = sum(
            1 for v in verifications
            if (v[2] is not None and v[2] > FRAUD_FLAG_THRESHOLD_PERCENT)
            or (v[3] and "suspicious" in v[3].lower())
        )

        m1, m2, m3, m4 = st.columns(4)

        with m1:
            st.metric("Avg Trust Score", f"{avg_trust}%")

        with m2:
            st.metric("Avg Fraud Probability", f"{avg_fraud}%")

        with m3:
            st.metric("Documents Flagged", flagged)

        with m4:
            risk_level = "High" if flagged > 0 else "Low"
            st.metric("Risk Level", risk_level)

        st.divider()

        st.subheader("Document Verification Results")

        for v in verifications:
            document_name, trust_score, fraud_probability, ai_result, remarks, verified_at = v

            with st.container(border=True):
                v1, v2, v3 = st.columns([3, 2, 3])

                with v1:
                    st.markdown(f"**{document_name}**")
                    st.caption(f"Verified: {verified_at or 'Unknown'}")

                with v2:
                    st.caption("Trust Score")
                    st.write(f"{trust_score}%" if trust_score is not None else "N/A")
                    st.caption("Fraud Probability")
                    st.write(f"{fraud_probability}%" if fraud_probability is not None else "N/A")

                with v3:
                    st.caption("AI Result")
                    if ai_result and "suspicious" in ai_result.lower():
                        render_badge(ai_result, "danger")
                    elif ai_result:
                        render_badge(ai_result, "success")
                    else:
                        render_badge("Not Evaluated", "neutral")
                    if remarks:
                        st.caption(remarks)

        st.divider()

        st.subheader("AI Recommendation")

        if flagged > 0:
            st.warning(
                "One or more documents show elevated fraud probability or suspicious results. "
                "Manual review is recommended before HR approval."
            )
        else:
            st.success(
                "All reviewed documents appear genuine. No forged document indicators detected. "
                "Recommended for HR Approval."
            )

# ==========================================================
# TIMELINE TAB
# ==========================================================

with timeline_tab:
    st.subheader("📅 Onboarding Timeline")

    timeline_events = fetch_onboarding_timeline(selected["id"])

    if not timeline_events:
        st.info("No timeline events recorded for this candidate yet.")
    else:
        for event_name, event_status, event_time in timeline_events:
            with st.container(border=True):
                t1, t2, t3 = st.columns([2, 6, 2])

                with t1:
                    st.write(event_time)

                with t2:
                    st.write(event_name)

                with t3:
                    render_badge(event_status or "Pending", stage_kind(event_status))

    st.divider()

    st.subheader("Log New Event")

    with st.form(key="log_timeline_event_form", clear_on_submit=True):
        te1, te2, te3 = st.columns([3, 2, 1])

        with te1:
            new_event_name = st.text_input("Event Name", key="new_event_name")

        with te2:
            new_event_status = st.selectbox(
                "Status",
                ["Pending", "In Progress", "Completed"],
                key="new_event_status"
            )

        with te3:
            st.write("")
            submitted = st.form_submit_button("Add", use_container_width=True)

        if submitted and new_event_name.strip():
            log_timeline_event(selected["id"], new_event_name.strip(), new_event_status)
            st.success("Timeline event added.")
            st.rerun()

# ==========================================================
# EMAIL CENTER TAB
# ==========================================================

with email_tab:
    st.subheader("📧 Email Center")

    candidate_emails = st.session_state.email_log.get(selected["id"], [])

    if not candidate_emails:
        st.info("No emails sent yet for this candidate.")
    else:
        for entry in reversed(candidate_emails):
            with st.container(border=True):
                e1, e2, e3 = st.columns([4, 2, 2])

                with e1:
                    st.write(entry["subject"])

                with e2:
                    render_badge(entry["status"], "success")

                with e3:
                    st.caption(entry["timestamp"])

    st.divider()

    st.subheader("Email Actions")

    em1, em2, em3, em4 = st.columns(4)

    with em1:
        if st.button("Send Offer Email", key="send_offer_email", use_container_width=True):
            send_email(selected["id"], "Offer Letter")
            log_timeline_event(selected["id"], "Offer Email Sent", "Completed")
            st.success("Offer email sent.")
            st.rerun()

    with em2:
        if st.button("Send Reminder Email", key="send_reminder_email", use_container_width=True):
            send_email(selected["id"], "Onboarding Reminder")
            log_timeline_event(selected["id"], "Reminder Email Sent", "Completed")
            st.success("Reminder email sent.")
            st.rerun()

    with em3:
        if st.button("Send Welcome Email", key="send_welcome_email", use_container_width=True):
            send_email(selected["id"], "Welcome Email")
            log_timeline_event(selected["id"], "Welcome Email Sent", "Completed")
            st.success("Welcome email sent.")
            st.rerun()

    with em4:
        if st.button("Send Joining Instructions", key="send_joining_instructions", use_container_width=True):
            send_email(selected["id"], "Joining Instructions")
            log_timeline_event(selected["id"], "Joining Instructions Sent", "Completed")
            st.success("Joining instructions sent.")
            st.rerun()

# ==========================================================
# HR ACTION CENTER
# ==========================================================

st.divider()
st.subheader("🧑‍💼 HR Action Center")

h1, h2, h3, h4 = st.columns(4)

with h1:
    if st.button("Approve Candidate", key="hr_approve_final", use_container_width=True):
        approve_candidate(selected["id"])
        log_timeline_event(selected["id"], "HR Final Approval", "Completed")
        st.success("Candidate Approved Successfully.")
        st.rerun()

with h2:
    if st.button("Reject Candidate", key="hr_reject_final", use_container_width=True):
        reject_candidate(selected["id"])
        log_timeline_event(selected["id"], "Candidate Rejected", "Completed")
        st.warning("Candidate Rejected.")
        st.rerun()

with h3:
    if st.button("Create Employee", key="hr_create_employee_final", use_container_width=True):
        manager_name = st.session_state.get("assign_manager_input", "").strip()
        if create_employee(selected["id"], manager=manager_name):
            log_timeline_event(selected["id"], "Employee Record Created", "Completed")
            employee_details = get_employee_by_candidate(selected["id"])
            employee_id = employee_details.get("employee_id") if employee_details else None
            if employee_id:
                st.success(f"Employee Created Successfully. Employee ID: {employee_id}")
            else:
                st.success("Employee Created Successfully.")
            st.rerun()
        else:
            st.error("Unable to create employee.")

with h4:
    export_documents = fetch_candidate_documents(selected["id"])
    export_verifications = fetch_document_verification(selected["id"])
    export_timeline = fetch_onboarding_timeline(selected["id"])

    report_text = build_export_report(
        selected,
        export_documents,
        export_verifications,
        export_timeline
    )

    st.download_button(
        "Export Report",
        data=report_text,
        file_name=f'onboarding_report_{selected["id"]}.csv',
        mime="text/csv",
        key="hr_export_report",
        use_container_width=True
    )

st.divider()