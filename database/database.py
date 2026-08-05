import sqlite3
import pandas as pd
import json
from database.schema import create_tables
DB_NAME = "database/recruitment.db"


# ---------------- CONNECTION ----------------

def get_connection():
    return sqlite3.connect(DB_NAME)

STAGE_ORDER = [
    "Applied",
    "AI Reviewed",
    "Shortlisted",
    "Interview Round 1",
    "Interview Round 2",
    "Interview Round 3",
    "Selected",
    "Offer Sent",
    "Onboarded"
]

def init_db():
    create_tables()


# ---------------- USERS ----------------

def get_user(email, password):
    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM users
        WHERE email=?
        AND password=?
    """, (email, password))

    user = cursor.fetchone()

    conn.close()

    return user


# ---------------- DASHBOARD ----------------

def get_total_candidates():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM candidates")

    total = cursor.fetchone()[0]

    conn.close()

    return total
def get_dashboard_stats():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT COUNT(*) FROM candidates")
    total_candidates = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM interviews")
    total_interviews = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*) FROM employees")
    total_employees = cursor.fetchone()[0]

    hiring_rate = 0

    if total_candidates > 0:
        hiring_rate = round(
            (total_employees / total_candidates) * 100,
            1
        )

    conn.close()

    return {
        "candidates": total_candidates,
        "interviews": total_interviews,
        "employees": total_employees,
        "hiring_rate": hiring_rate
    }
    

def get_hiring_funnel():

    conn = get_connection()

    query = """
        SELECT
            status,
            COUNT(*) as Candidates
        FROM candidates
        GROUP BY status
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    df.rename(
        columns={"status":"Stage"},
        inplace=True
    )

    return df
def get_candidate_sources():

    return pd.DataFrame({

        "Source":[
            "LinkedIn",
            "Naukri",
            "Referral",
            "Website"
        ],

        "Candidates":[
            45,
            30,
            15,
            10
        ]

    })
def get_recent_candidates():

    conn = get_connection()

    query = """
        SELECT

            name as Candidate,

            role_applied as Role,

            status as Status

        FROM candidates

        ORDER BY id DESC

        LIMIT 5
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

# ---------------- RESUME ----------------

def save_resume_analysis(
    resume_name,
    jd_name,
    ats_score,
    matched_skills,
    missing_skills,
    summary,
    recommendation,
    analysis
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

    INSERT INTO resume_analysis(

        resume_name,
        jd_name,
        ats_score,
        matched_skills,
        missing_skills,
        summary,
        recommendation,
        analysis

    )

    VALUES(?,?,?,?,?,?,?,?)

    """, (

        resume_name,
        jd_name,
        ats_score,
        matched_skills,
        missing_skills,
        summary,
        recommendation,
        analysis

    ))

    conn.commit()

    conn.close()
def get_resume_history():

    conn = get_connection()

    query = """

    SELECT *

    FROM resume_analysis

    ORDER BY analyzed_at DESC

    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df

def update_candidate_status(candidate_name, status):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        UPDATE candidates
        SET status=?
        WHERE name=?
    """, (status, candidate_name))

    conn.commit()

    conn.close()

# ---------------- CANDIDATES ----------------

def get_candidates():

    conn = get_connection()

    query = """
        SELECT
            id,
            name,
            role_applied,
            experience,
            skills,
            resume_path,
            status
        FROM candidates
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df
def get_candidate(candidate_name):

    conn = get_connection()

    query = """
        SELECT *
        FROM candidates
        WHERE name=?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(candidate_name,)
    )

    conn.close()

    if len(df):
        return df.iloc[0]

    return None
def get_candidate_by_id(candidate_id):

    conn = get_connection()

    query = """
        SELECT *
        FROM candidates
        WHERE id=?
    """

    df = pd.read_sql_query(
        query,
        conn,
        params=(candidate_id,)
    )

    conn.close()

    if len(df):
        return df.iloc[0]

    return None
def get_all_job_candidates():

    conn = get_connection()

    query = """
        SELECT
            id,
            name,
            email,
            phone,
            role_applied,
            experience,
            skills,
            resume_path,
            status
        FROM candidates
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df
def update_candidate_stage(candidate_id, status):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE candidates

        SET status=?

        WHERE id=?

    """, (

        status,
        candidate_id

    ))

    conn.commit()
    conn.close()
def get_candidate_documents(candidate_id):

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM candidate_documents

        WHERE candidate_id=?

    """, conn, params=(candidate_id,))

    conn.close()

    return df
def add_candidate_document(
    candidate_id,
    document_name,
    document_path,
    verified=0
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO candidate_documents(

            candidate_id,
            document_name,
            document_path,
            verified

        )

        VALUES(?,?,?,?)

    """, (

        candidate_id,
        document_name,
        document_path,
        verified

    ))

    conn.commit()
    conn.close()
def update_document_status(
    document_id,
    verified
):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE candidate_documents

        SET verified=?

        WHERE id=?

    """, (

        verified,
        document_id

    ))

    conn.commit()
    conn.close()

# ---------------- INTERVIEW ----------------

def get_interviews():

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""
        SELECT *
        FROM interviews
    """)

    data = cursor.fetchall()

    conn.close()

    return data

# ---------------- INTERVIEW ----------------

def get_resume_files():

    conn = get_connection()

    query = """
        SELECT
            name,
            resume_path
        FROM candidates
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df
def schedule_interview(

    candidate_id,
    round_name,
    interviewer,
    interview_date,
    interview_time,
    meeting_mode,
    meeting_link,
    status="Scheduled"

):

    conn = get_connection()

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

        candidate_id,
        round_name,
        interviewer,
        interview_date,
        interview_time,
        meeting_mode,
        meeting_link,
        status

    ))

    conn.commit()
    conn.close()
def get_candidate_interviews(candidate_id):

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM interviews

        WHERE candidate_id=?

        ORDER BY interview_date

    """, conn, params=(candidate_id,))

    conn.close()

    return df
def update_interview(

    interview_id,
    technical_score,
    communication_score,
    technical_notes,
    communication_notes,
    overall_notes,
    ai_feedback,
    feedback,
    recommendation,
    status

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        UPDATE interviews

        SET

            technical_score=?,
            communication_score=?,
            technical_notes=?,
            communication_notes=?,
            overall_notes=?,
            ai_feedback=?,
            feedback=?,
            recommendation=?,
            status=?

        WHERE id=?

    """, (

        technical_score,
        communication_score,
        technical_notes,
        communication_notes,
        overall_notes,
        ai_feedback,
        feedback,
        recommendation,
        status,
        interview_id

    ))

    conn.commit()
    conn.close()
def create_employee(

    candidate_id,
    employee_code,
    name,
    email,
    phone,
    department,
    designation,
    manager,
    joining_date,
    experience,
    location,
    skills,
    status="Active"

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO employees(

            candidate_id,
            employee_code,
            name,
            email,
            phone,
            department,
            designation,
            manager,
            joining_date,
            experience,
            location,
            skills,
            status

        )

        VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)

    """, (

        candidate_id,
        employee_code,
        name,
        email,
        phone,
        department,
        designation,
        manager,
        joining_date,
        experience,
        location,
        skills,
        status

    ))

    conn.commit()
    conn.close()

# ---------------- EMPLOYEES ----------------

def get_employees():

    conn = get_connection()

    query = """
        SELECT *
        FROM employees
        ORDER BY name
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df
def get_departments():

    conn = get_connection()

    query = """
        SELECT DISTINCT department
        FROM employees
        ORDER BY department
    """

    df = pd.read_sql_query(query, conn)

    conn.close()

    return df["department"].tolist()


def get_employee(employee_name):

    conn = get_connection()

    query = """
        SELECT *
        FROM employees
        WHERE name = ?
    """

    df = pd.read_sql_query(query, conn, params=(employee_name,))
    conn.close()

    if df.empty:
        return None

    employee = df.iloc[0]

    employee["skills"] = json.loads(employee["skills"])
    employee["performance_trend"] = json.loads(employee["performance_trend"])
    employee["attendance_trend"] = json.loads(employee["attendance_trend"])
    employee["certifications"] = json.loads(employee["certifications"])
    employee["learning_progress"] = json.loads(employee["learning_progress"])
    employee["project_distribution"] = json.loads(employee["project_distribution"])

    return employee

# ---------------- JOBS ----------------
def save_job(
    job_title,
    job_description,
    required_skills,
    experience,
    salary,
    location,
    ats_cutoff,
    status,
    created_date
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO jobs(

            job_title,
            job_description,
            required_skills,
            experience,
            salary,
            location,
            ats_cutoff,
            status,
            created_date

        )

        VALUES(?,?,?,?,?,?,?,?,?)

    """, (

        job_title,
        job_description,
        required_skills,
        experience,
        salary,
        location,
        ats_cutoff,
        status,
        created_date

    ))

    conn.commit()
    conn.close()
    
def get_jobs():

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM jobs

        ORDER BY id DESC

    """, conn)

    conn.close()

    return df

def update_job(
    job_id,
    title,
    description,
    skills,
    experience,
    salary,
    location,
    cutoff
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE jobs

        SET

            job_title=?,
            job_description=?,
            required_skills=?,
            experience=?,
            salary=?,
            location=?,
            ats_cutoff=?

        WHERE id=?

    """, (

        title,
        description,
        skills,
        experience,
        salary,
        location,
        cutoff,
        job_id

    ))

    conn.commit()
    conn.close()
    
def update_job_status(job_id, status):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""

        UPDATE jobs

        SET status=?

        WHERE id=?

    """, (status, job_id))

    conn.commit()
    conn.close()
    
def get_job_applications(job_id):

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM job_applications

        WHERE job_id=?

    """, conn, params=(job_id,))

    conn.close()

    return df
def start_onboarding(candidate_id, joining_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO onboarding(
            candidate_id,
            onboarding_status,
            onboarding_progress,
            joining_date,
            hr_status
        )
        VALUES(?,?,?,?,?)
    """, (
        candidate_id,
        "Started",
        0,
        joining_date,
        "Pending"
    ))

    conn.commit()
    conn.close()
def get_onboarding_candidate(candidate_id):

    conn = get_connection()

    df = pd.read_sql_query("""
        SELECT *
        FROM onboarding
        WHERE candidate_id=?
    """, conn, params=(candidate_id,))

    conn.close()

    if df.empty:
        return None

    return df.iloc[0]

def update_onboarding_progress(
    candidate_id,
    progress,
    status
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE onboarding
        SET
            onboarding_progress=?,
            onboarding_status=?
        WHERE candidate_id=?
    """, (
        progress,
        status,
        candidate_id
    ))

    conn.commit()
    conn.close()

def update_hr_status(
    candidate_id,
    hr_status
):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE onboarding
        SET hr_status=?
        WHERE candidate_id=?
    """, (
        hr_status,
        candidate_id
    ))

    conn.commit()
    conn.close()

def get_onboarding():

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT
            o.*,
            c.name,
            c.email,
            c.phone,
            c.role_applied,
            c.resume_path

        FROM onboarding o

        JOIN candidates c
        ON o.candidate_id = c.id

        ORDER BY c.name

    """, conn)

    conn.close()

    return df
def get_selected_candidates():

    conn = get_connection()

    df = pd.read_sql_query("""

        SELECT *

        FROM candidates

        WHERE status='Selected'

        ORDER BY name

    """, conn)

    conn.close()

    return df
# =====================================================================
# CAREERS PORTAL FUNCTIONS
# Append everything below to the end of database/database.py
# (it already has `conn = get_connection()` / pandas / sqlite patterns
# used throughout the rest of the file, so no new imports are needed)
# =====================================================================

def add_job_application(
    job_id,
    candidate_name,
    candidate_email,
    resume_path,
    applied_date
):
    """
    Creates a new application record when a candidate applies
    to a job through the Careers Portal.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO job_applications(
            job_id,
            candidate_name,
            candidate_email,
            resume_path,
            applied_date,
            ats_score,
            skill_match,
            experience_match,
            status
        )
        VALUES(?,?,?,?,?,?,?,?,?)
    """, (
        job_id,
        candidate_name,
        candidate_email,
        resume_path,
        applied_date,
        0,
        0,
        0,
        "Applied"
    ))

    conn.commit()
    application_id = cursor.lastrowid
    conn.close()

    return application_id


def get_all_applications(job_id=None, search=None, status=None):
    """
    Powers the Careers Portal list view.

    Returns every application joined with its job title so the
    portal can show applications across ALL jobs, not just one,
    with optional search-by-name and filter-by-status.
    """

    conn = get_connection()

    query = """
        SELECT
            job_applications.id,
            job_applications.job_id,
            jobs.job_title,
            jobs.job_description,
            jobs.required_skills,
            jobs.ats_cutoff,
            job_applications.candidate_name,
            job_applications.candidate_email,
            job_applications.resume_path,
            job_applications.applied_date,
            job_applications.ats_score,
            job_applications.skill_match,
            job_applications.experience_match,
            job_applications.ai_report,
            job_applications.status
        FROM job_applications
        LEFT JOIN jobs ON jobs.id = job_applications.job_id
        WHERE 1=1
    """

    params = []

    if job_id:
        query += " AND job_applications.job_id = ?"
        params.append(job_id)

    if search:
        query += " AND job_applications.candidate_name LIKE ?"
        params.append(f"%{search}%")

    if status and status != "All":
        query += " AND job_applications.status = ?"
        params.append(status)

    query += " ORDER BY job_applications.id DESC"

    df = pd.read_sql_query(query, conn, params=params)

    conn.close()

    return df


def get_application_by_id(application_id):

    conn = get_connection()

    query = """
        SELECT
            job_applications.*,
            jobs.job_title,
            jobs.job_description,
            jobs.required_skills,
            jobs.ats_cutoff
        FROM job_applications
        LEFT JOIN jobs ON jobs.id = job_applications.job_id
        WHERE job_applications.id = ?
    """

    df = pd.read_sql_query(query, conn, params=(application_id,))

    conn.close()

    if len(df):
        return df.iloc[0]

    return None


def update_application_status(application_id, status):
    """
    Used by Search / Filter actions (Shortlist, Reject, Hold, etc.)
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE job_applications
        SET status=?
        WHERE id=?
    """, (status, application_id))

    conn.commit()
    conn.close()


def save_application_analysis(
    application_id,
    ats_score,
    skill_match,
    experience_match,
    ai_report
):
    """
    Stores the result of "Run AI Resume Analysis" against a
    specific application.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE job_applications
        SET
            ats_score=?,
            skill_match=?,
            experience_match=?,
            ai_report=?,
            status=?
        WHERE id=?
    """, (
        ats_score,
        skill_match,
        experience_match,
        ai_report,
        "AI Reviewed",
        application_id
    ))

    conn.commit()
    conn.close()


def add_candidate(
    name,
    email,
    phone,
    role_applied,
    experience,
    skills,
    resume_path,
    status
):
    """
    Inserts a brand-new row into the `candidates` table. Needed
    because candidates previously only ever existed via seed data —
    there was no way for a real application to become a candidate.
    """

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO candidates(
            name,
            email,
            phone,
            role_applied,
            experience,
            skills,
            resume_path,
            status
        )
        VALUES(?,?,?,?,?,?,?,?)
    """, (
        name,
        email,
        phone,
        role_applied,
        experience,
        skills,
        resume_path,
        status
    ))

    conn.commit()
    candidate_id = cursor.lastrowid
    conn.close()

    return candidate_id


def move_application_to_screening(application_id):
    """
    Implements the plan's "Move candidate to screening" function.

    job_applications and candidates were two disconnected tables —
    this is what actually bridges them: it takes an application,
    creates (or reuses) the matching candidate record, and marks
    both sides so the candidate now shows up in Candidate Screening.
    """

    application = get_application_by_id(application_id)

    if application is None:
        return None

    conn = get_connection()
    cursor = conn.cursor()

    # Reuse an existing candidate row (matched by email) if one
    # already exists, instead of creating duplicates.
    cursor.execute("""
        SELECT id FROM candidates WHERE email = ? AND email IS NOT NULL AND email != ''
    """, (application["candidate_email"],))

    existing = cursor.fetchone()

    if existing:
        candidate_id = existing[0]

        cursor.execute("""
            UPDATE candidates
            SET status=?, resume_path=?
            WHERE id=?
        """, ("Screening", application["resume_path"], candidate_id))

    else:
        cursor.execute("""
            INSERT INTO candidates(
                name, email, phone, role_applied,
                experience, skills, resume_path, status
            )
            VALUES(?,?,?,?,?,?,?,?)
        """, (
            application["candidate_name"],
            application["candidate_email"],
            "",
            application["job_title"],
            "",
            "",
            application["resume_path"],
            "Screening"
        ))

        candidate_id = cursor.lastrowid

    cursor.execute("""
        UPDATE job_applications
        SET status=?
        WHERE id=?
    """, ("Moved to Screening", application_id))

    conn.commit()
    conn.close()

    return candidate_id
def save_ai_interview_answer(

    interview_id,

    question,

    answer,

    score,

    feedback,

    strengths,

    weaknesses,

    follow_up

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO ai_interviews(

            interview_id,

            question,

            answer,

            score,

            feedback,

            strengths,

            weaknesses,

            follow_up

        )

        VALUES(?,?,?,?,?,?,?,?)

    """,(

        interview_id,

        question,

        answer,

        score,

        feedback,

        strengths,

        weaknesses,

        follow_up

    ))

    conn.commit()

    conn.close()
def save_ai_interview_summary(

    interview_id,

    report

):

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute("""

        INSERT INTO ai_interview_summary(

            interview_id,

            technical_score,

            communication_score,

            confidence_score,

            overall_score,

            recommendation,

            summary

        )

        VALUES(?,?,?,?,?,?,?)

    """,(

        interview_id,

        report["technical_score"],

        report["communication_score"],

        report["confidence_score"],

        report["overall_score"],

        report["recommendation"],

        report["summary"]

    ))

    conn.commit()

    conn.close()
def get_ai_interview(

    interview_id

):

    conn = get_connection()

    query = """

        SELECT *

        FROM ai_interviews

        WHERE interview_id=?

        ORDER BY id

    """

    df = pd.read_sql_query(

        query,

        conn,

        params=(interview_id,)

    )

    conn.close()

    return df
def get_ai_summary(

    interview_id

):

    conn = get_connection()

    query = """

        SELECT *

        FROM ai_interview_summary

        WHERE interview_id=?

    """

    df = pd.read_sql_query(

        query,

        conn,

        params=(interview_id,)

    )

    conn.close()

    return df