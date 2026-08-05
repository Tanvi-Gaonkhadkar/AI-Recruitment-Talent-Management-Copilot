import sqlite3
import json
from datetime import datetime

DB_NAME = "database/recruitment.db"


def get_connection():
    return sqlite3.connect(DB_NAME)


# ==========================================================
# REQUIRED DOCUMENT CHECKLIST
# ----------------------------------------------------------
# Mirrors the "Candidate Uploads" checklist in the project plan
# (AI Document Verification module): Resume, Aadhaar, PAN, Degree,
# Experience Certificate, Payslip. Used to power "Missing Document
# Detection" (plan: Onboarding AI Features).
# ==========================================================

REQUIRED_ONBOARDING_DOCUMENTS = [
    "Resume",
    "Aadhaar",
    "PAN",
    "Degree",
    "Experience Certificate",
    "Payslip",
]


def _is_required_document_uploaded(required_name, uploaded_names):
    required_lower = required_name.strip().lower()
    for uploaded in uploaded_names:
        uploaded_lower = (uploaded or "").strip().lower()
        if not uploaded_lower:
            continue
        if required_lower in uploaded_lower or uploaded_lower in required_lower:
            return True
    return False


def get_missing_documents(candidate_id):
    """
    Returns the list of required documents (from REQUIRED_ONBOARDING_DOCUMENTS)
    that this candidate has not yet uploaded.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT document_name
        FROM candidate_documents
        WHERE candidate_id = ?
    """, (candidate_id,))

    uploaded_names = [row[0] for row in cursor.fetchall()]

    conn.close()

    return [
        required for required in REQUIRED_ONBOARDING_DOCUMENTS
        if not _is_required_document_uploaded(required, uploaded_names)
    ]


def get_missing_documents_for_all_candidates():
    """
    Bulk version of get_missing_documents(), used to power dashboard-level
    "Missing Document Detection" alerts without one query per candidate.
    Returns {candidate_id: [missing_document_name, ...]}.
    """
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT candidate_id, document_name
        FROM candidate_documents
    """)

    uploaded_by_candidate = {}
    for candidate_id, document_name in cursor.fetchall():
        uploaded_by_candidate.setdefault(candidate_id, []).append(document_name)

    cursor.execute("SELECT id FROM candidates")
    all_candidate_ids = [row[0] for row in cursor.fetchall()]

    conn.close()

    missing_by_candidate = {}
    for candidate_id in all_candidate_ids:
        uploaded_names = uploaded_by_candidate.get(candidate_id, [])
        missing = [
            required for required in REQUIRED_ONBOARDING_DOCUMENTS
            if not _is_required_document_uploaded(required, uploaded_names)
        ]
        if missing:
            missing_by_candidate[candidate_id] = missing

    return missing_by_candidate


# ==========================================================
# GET ALL ONBOARDING CANDIDATES
# ==========================================================

def get_onboarding_candidates():

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id,
            c.name,
            c.email,
            c.phone,
            c.role_applied,
            c.experience,
            c.skills,
            c.status,
            o.onboarding_status,
            o.onboarding_progress,
            o.joining_date,
            o.hr_status
        FROM candidates c
        LEFT JOIN onboarding o
        ON c.id = o.candidate_id
        ORDER BY c.id DESC
    """)

    data = cursor.fetchall()

    conn.close()

    return data


# ==========================================================
# GET SINGLE CANDIDATE
# ==========================================================

def get_candidate(candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT
            c.id,
            c.name,
            c.email,
            c.phone,
            c.role_applied,
            c.experience,
            c.skills,
            c.resume_path,
            c.status,
            o.onboarding_status,
            o.onboarding_progress,
            o.joining_date,
            o.hr_status
        FROM candidates c
        LEFT JOIN onboarding o
        ON c.id = o.candidate_id
        WHERE c.id = ?
    """, (candidate_id,))

    data = cursor.fetchone()

    conn.close()

    return data


# ==========================================================
# START ONBOARDING
# ==========================================================

def start_onboarding(candidate_id, joining_date):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO onboarding(
            candidate_id,
            onboarding_status,
            onboarding_progress,
            joining_date,
            hr_status
        )
        VALUES(?,?,?,?,?)
    """,
    (
        candidate_id,
        "Offer Accepted",
        10,
        joining_date,
        "Pending"
    ))

    conn.commit()
    conn.close()


# ==========================================================
# UPDATE PROGRESS
# ==========================================================

def update_progress(candidate_id, progress):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE onboarding
        SET onboarding_progress=?
        WHERE candidate_id=?
    """,
    (
        progress,
        candidate_id
    ))

    conn.commit()
    conn.close()


# ==========================================================
# APPROVE
# ==========================================================

def approve_candidate(candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE onboarding
        SET
            hr_status='Approved',
            onboarding_status='Approved',
            onboarding_progress=100
        WHERE candidate_id=?
    """, (candidate_id,))

    conn.commit()
    conn.close()


# ==========================================================
# REJECT
# ==========================================================

def reject_candidate(candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE onboarding
        SET
            hr_status='Rejected',
            onboarding_status='Rejected'
        WHERE candidate_id=?
    """, (candidate_id,))

    conn.commit()
    conn.close()


# ==========================================================
# COMPLETE
# ==========================================================

def complete_onboarding(candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        UPDATE onboarding
        SET onboarding_status='Completed'
        WHERE candidate_id=?
    """, (candidate_id,))

    conn.commit()
    conn.close()
# ==========================================================
# GENERATE EMPLOYEE ID
# ----------------------------------------------------------
# Plan (Onboarding > Functions) calls for "Generate Employee ID"
# alongside offer letters and joining dates. Format is
# EMP-<year>-<zero-padded candidate id>, e.g. EMP-2026-0042.
# ==========================================================

# def generate_employee_id(candidate_id):
#     year = datetime.now().year
#     return f"EMP-{year}-{int(candidate_id):04d}"


# ==========================================================
# GET EMPLOYEE BY CANDIDATE
# ----------------------------------------------------------
# Lets the UI show the generated Employee ID / assigned manager
# right after create_employee() runs, without guessing at values
# it didn't compute itself.
# ==========================================================

def get_employee_by_candidate(candidate_id):

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT email FROM candidates WHERE id=?", (candidate_id,))
    candidate_row = cursor.fetchone()

    if candidate_row is None:
        conn.close()
        return None

    email = candidate_row[0]

    cursor.execute("PRAGMA table_info(employees)")
    available_columns = [row[1] for row in cursor.fetchall()]

    select_columns = [
        c for c in (
            "employee_id",
            "employee_code",
            "department",
            "designation",
            "manager",
            "joining_date"
        )
        if c in available_columns
    ]

    if not select_columns:
        conn.close()
        return None

    cursor.execute(
        f"SELECT {','.join(select_columns)} FROM employees WHERE email=?",
        (email,)
    )
    employee_row = cursor.fetchone()

    conn.close()

    if employee_row is None:
        return None

    return dict(zip(select_columns, employee_row))


# ==========================================================
# CREATE EMPLOYEE
# ==========================================================

def create_employee(candidate_id, manager=""):

    conn = get_connection()
    cursor = conn.cursor()

    # Get candidate details
    cursor.execute("""
        SELECT
            name,
            email,
            role_applied,
            skills,
            phone,
            experience
        FROM candidates
        WHERE id=?
    """, (candidate_id,))

    candidate = cursor.fetchone()

    if candidate is None:

        conn.close()
        return False

    name = candidate[0]
    email = candidate[1]
    designation = candidate[2]
    skills = candidate[3]
    phone = candidate[4]
    experience = candidate[5]

    # Prevent duplicate employee records if this action is triggered
    # more than once for the same candidate (e.g. a double click).
    cursor.execute("""
        SELECT employee_id FROM employees WHERE email=?
    """, (email,))

    existing_employee = cursor.fetchone()

    if existing_employee is not None:

        cursor.execute("""
            UPDATE onboarding
            SET
                onboarding_status='Completed',
                onboarding_progress=100,
                hr_status='Approved'
            WHERE candidate_id=?
        """, (candidate_id,))

        conn.commit()
        conn.close()

        return True

    # Get joining date
    cursor.execute("""
        SELECT joining_date
        FROM onboarding
        WHERE candidate_id=?
    """, (candidate_id,))

    onboarding = cursor.fetchone()

    joining_date = ""

    if onboarding:
        joining_date = onboarding[0]

    # Only include the newer analytics columns (phone, experience) if
    # this database has already run migrate_employees_table.py. This
    # keeps create_employee working even before that migration runs.
    cursor.execute("PRAGMA table_info(employees)")
    available_columns = {row[1] for row in cursor.fetchall()}

    insert_columns = [
        "candidate_id",
        "name",
        "email",
        "phone",
        "department",
        "designation",
        "manager",
        "joining_date",
        "experience",
        "location",
        "skills",
        "performance_rating",
        "attendance",
        "performance_trend",
        "attendance_trend",
        "projects_completed",
        "certifications",
        "learning_progress",
        "project_distribution",
        "status"
    ]
    try:
        years = int(str(experience).split()[0])
    except:
        years = 0

    insert_values = [
        candidate_id,
        name,
        email,
        phone,
        "Not Assigned",
        designation,
        manager or "",
        joining_date,
        years,
        "",
        skills,
        0.0,
        0,
        json.dumps([]),
        json.dumps([]),
        0,
        json.dumps([]),
        json.dumps({}),
        json.dumps({}),
        "Active"
    ]

    # optional_columns = {
    #     "phone": phone,
    #     "experience": experience,
    #     "employee_id": generate_employee_id(candidate_id),
    # }

    # for column, value in optional_columns.items():
    #     if column in available_columns:
    #         insert_columns.append(column)
    #         insert_values.append(value)

    placeholders = ",".join("?" for _ in insert_columns)
    column_list = ",".join(insert_columns)

    cursor.execute(
        f"INSERT INTO employees({column_list}) VALUES({placeholders})",
        insert_values
    )
    employee_id = cursor.lastrowid
    employee_code = f"EMP{employee_id:03d}"

    cursor.execute("""
    UPDATE employees
    SET employee_code = ?
    WHERE employee_id = ?
    """, (employee_code, employee_id))

    # Link all candidate documents with this employee
    cursor.execute("""
    UPDATE candidate_documents
    SET employee_id = ?
    WHERE candidate_id = ?
    """, (
        employee_id,
        candidate_id
    ))

    # Update onboarding
    cursor.execute("""
        UPDATE onboarding
        SET
            onboarding_status='Completed',
            onboarding_progress=100,
            hr_status='Approved'
        WHERE candidate_id=?
    """, (candidate_id,))

    conn.commit()
    conn.close()

    return True