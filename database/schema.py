import sqlite3

DB_NAME = "database/recruitment.db"

def create_tables():

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()

    # ---------------- USERS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        role TEXT NOT NULL
    )
    """)

    # ---------------- CANDIDATES ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS candidates(
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        email TEXT,
        phone TEXT,
        role_applied TEXT,
        experience TEXT,
        skills TEXT,
        resume_path TEXT,
        status TEXT
    )
    """)

    # ---------------- RESUME ANALYSIS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS resume_analysis(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        resume_name TEXT,

        jd_name TEXT,

        ats_score INTEGER,

        matched_skills TEXT,

        missing_skills TEXT,

        summary TEXT,

        recommendation TEXT,

        analysis TEXT,

        analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

    )
    """)

    # ---------------- INTERVIEWS ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS interviews(
        id INTEGER PRIMARY KEY AUTOINCREMENT,

        candidate_id INTEGER,

        round_name TEXT,

        interviewer TEXT,

        interview_date TEXT,

        interview_time TEXT,

        meeting_mode TEXT,

        meeting_link TEXT,

        technical_score REAL,

        communication_score REAL,

        technical_notes TEXT,

        communication_notes TEXT,

        overall_notes TEXT,

        ai_feedback TEXT,

        feedback TEXT,

        recommendation TEXT,

        invitation_sent INTEGER DEFAULT 0,

        status TEXT,

        FOREIGN KEY(candidate_id)
        REFERENCES candidates(id)

    )
    """)
    # ---------------- AI INTERVIEW ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS ai_interviews(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        interview_id INTEGER,

        question TEXT,

        answer TEXT,

        score REAL,

        feedback TEXT,

        strengths TEXT,

        weaknesses TEXT,

        follow_up TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(interview_id)
        REFERENCES interviews(id)

    )

    """)
    # ---------------- AI INTERVIEW SUMMARY ----------------

    cursor.execute("""

    CREATE TABLE IF NOT EXISTS ai_interview_summary(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        interview_id INTEGER,

        technical_score REAL,

        communication_score REAL,

        confidence_score REAL,

        overall_score REAL,

        recommendation TEXT,

        summary TEXT,

        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(interview_id)
        REFERENCES interviews(id)

    )

    """)

    # ---------------- EMPLOYEES ----------------
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS employees(
        employee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        candidate_id INTEGER,
        employee_code TEXT,
        name TEXT NOT NULL,
        email TEXT,
        phone TEXT,
        department TEXT,
        designation TEXT,
        manager TEXT,
        joining_date TEXT,
        experience INTEGER,
        location TEXT,
        skills TEXT,
        performance_rating REAL,
        attendance INTEGER,
        performance_trend TEXT,
        attendance_trend TEXT,
        projects_completed INTEGER,
        certifications TEXT,
        learning_progress TEXT,
        project_distribution TEXT,
        status TEXT
    )
    """)
    # ---------------- JOBS ----------------
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        job_title TEXT,
        job_description TEXT,
        required_skills TEXT,
        experience TEXT,
        salary TEXT,
        location TEXT,
        ats_cutoff INTEGER,
        status TEXT,
        created_date TEXT
        )
        """)
    # ---------------- JOB APPLICATIONS (CAREERS PORTAL) ----------------
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS job_applications(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            job_id INTEGER,

            candidate_name TEXT,

            candidate_email TEXT,

            resume_path TEXT,

            applied_date TEXT,

            ats_score INTEGER,

            skill_match INTEGER,

            experience_match INTEGER,

            ai_report TEXT,

            status TEXT,

            FOREIGN KEY(job_id) REFERENCES jobs(id)

        )
        """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS candidate_documents(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        candidate_id INTEGER,

        employee_id INTEGER,

        document_name TEXT,

        file_path TEXT,

        upload_status TEXT DEFAULT 'Uploaded',

        verification_status TEXT DEFAULT 'Pending',

        uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

        FOREIGN KEY(candidate_id)
        REFERENCES candidates(id)

    );
    """)
    # ---------------- ONBOARDING ----------------

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS onboarding(

        id INTEGER PRIMARY KEY AUTOINCREMENT,

        candidate_id INTEGER UNIQUE,

        onboarding_status TEXT,

        onboarding_progress INTEGER,

        joining_date TEXT,

        hr_status TEXT,

        FOREIGN KEY(candidate_id)
        REFERENCES candidates(id)

    )
    """)
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS document_verification(

            id INTEGER PRIMARY KEY AUTOINCREMENT,

            candidate_id INTEGER,

            document_name TEXT,

            trust_score REAL,

            fraud_probability REAL,

            ai_result TEXT,

            remarks TEXT,

            verified_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

            FOREIGN KEY(candidate_id)
            REFERENCES candidates(id)

        );
        """)
    
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS onboarding_timeline(

                id INTEGER PRIMARY KEY AUTOINCREMENT,

                candidate_id INTEGER,

                event_name TEXT,

                event_status TEXT,

                event_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

                FOREIGN KEY(candidate_id)
                REFERENCES candidates(id)

            );
            """)

    conn.commit()

    # ---------------- CAREERS PORTAL MIGRATION ----------------
    # job_applications was created before the Careers Portal existed, so
    # older databases won't have these columns yet. Add them if missing
    # instead of dropping/recreating the table (keeps existing rows).
    migrate_job_applications(cursor)

    conn.commit()
    conn.close()

    print("Database and tables created successfully!")


def migrate_job_applications(cursor):
    """
    Adds the columns the Careers Portal needs to job_applications
    if they don't already exist (safe to run every startup).
    """

    cursor.execute("PRAGMA table_info(job_applications)")
    existing_columns = {row[1] for row in cursor.fetchall()}

    new_columns = {
        "candidate_email": "TEXT",
        "resume_path": "TEXT",
        "applied_date": "TEXT",
        "ai_report": "TEXT"
    }

    for column_name, column_type in new_columns.items():

        if column_name not in existing_columns:

            cursor.execute(f"""
                ALTER TABLE job_applications
                ADD COLUMN {column_name} {column_type}
            """)


if __name__ == "__main__":
    create_tables()