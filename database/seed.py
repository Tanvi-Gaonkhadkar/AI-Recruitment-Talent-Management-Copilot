import sqlite3
import json

DB_NAME = "database/recruitment.db"

conn = sqlite3.connect(DB_NAME)
cursor = conn.cursor()

# -----------------------------
# USERS
# -----------------------------
users = [

(
    "Recruiter",
    "recruiter@talenthire.com",
    "Recruit@123",
    "Recruiter"
),

(
        "HR",
        "hr@talenthire.com",
        "HR@123",
        "HR"
)

]

cursor.executemany("""

INSERT OR IGNORE INTO users
(name,email,password,role)

VALUES (?,?,?,?)

""", users)

# -----------------------------
# CANDIDATES
# -----------------------------
candidates = [

(
"Rahul Sharma",
"rahul@gmail.com",
"9876543210",
"AI Engineer",
"2 Years",
"Python, Machine Learning, SQL",
"uploads/Rahul_Sharma.pdf",
"Shortlisted"
),

(
"Sneha Patil",
"sneha@gmail.com",
"9876543211",
"Backend Developer",
"1 Year",
"Java, Spring Boot, MySQL",
"uploads/Sneha_Patil.pdf",
"Interview"
),

(
"Aditi Joshi",
"aditi@gmail.com",
"9876543212",
"Data Scientist",
"3 Years",
"Python, Pandas, TensorFlow",
"uploads/Aditi_Joshi.pdf",
"Selected"
),

(
"Rohan Shah",
"rohan@gmail.com",
"9876543213",
"Frontend Developer",
"2 Years",
"React, JavaScript, CSS",
"uploads/Rohan_Shah.pdf",
"Review"
)

]

cursor.executemany("""

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

""", candidates)

# -----------------------------
# RESUME ANALYSIS
# -----------------------------

resume_analysis = [

(
"Rahul_Sharma.pdf",
"AI_EngineerJD.pdf",
92,
"Python, Machine Learning, SQL",
"Cloud Computing",
"Strong AI Engineer profile",
"Highly Recommended",
"Excellent technical match with required AI skills."
),

(
"Sneha_Patil.pdf",
"AI_EngineerJD.pdf",
88,
"Java, Spring Boot",
"Docker",
"Good Backend Developer",
"Recommended",
"Strong backend skills with minor skill gaps."
),

(
"Aditi_Joshi.pdf",
"AI_EngineerJD.pdf",
95,
"Python, TensorFlow",
"Azure",
"Excellent Data Scientist",
"Highly Recommended",
"Outstanding candidate with excellent ML knowledge."
),

(
"Rohan_Shah.pdf",
"AI_EngineerJD.pdf",
81,
"React, JavaScript",
"NextJS",
"Frontend Developer",
"Recommended",
"Good frontend profile with some missing skills."
)

]

cursor.executemany("""

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

""", resume_analysis)

# -----------------------------
# INTERVIEWS
# -----------------------------
interviews = [

(
1,
"Technical Round",
"Mr. Amit",
"2026-08-05",
"10:00 AM",
"Online",
"https://meet.google.com/demo1",
8.5,
8.0,
"Strong DSA",
"Good communication",
"Overall impressive",
"Recommended by AI",
"Good technical knowledge",
"Proceed",
1,
"Scheduled"
),

(
2,
"HR Round",
"Ms. Priya",
"2026-08-06",
"11:30 AM",
"Offline",
"",
7.5,
8.5,
"Average Java",
"Excellent communication",
"Good personality",
"Suitable candidate",
"Good communication",
"Round 2",
0,
"Completed"
)

]

cursor.executemany("""

INSERT INTO interviews(

candidate_id,
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
ai_feedback,
feedback,
recommendation,
invitation_sent,
status

)

VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

""", interviews)

# -----------------------------
# EMPLOYEES
# -----------------------------
employees = [

(
    None,
    "EMP001",
    "Ananya Kulkarni",
    "ananya@gmail.com",
    "9876543210",
    "AI",
    "ML Engineer",
    "Rakesh Kumar",
    "2025-01-10",
    3,
    "Pune",
    json.dumps({
        "Python":90,
        "SQL":85,
        "Machine Learning":95
    }),
    4.6,
    97,
    json.dumps([4.1,4.2,4.3,4.5,4.4,4.6]),
    json.dumps([95,96,97,98,97,99]),
    12,
    json.dumps([
        "AWS Cloud Practitioner",
        "NPTEL Java"
    ]),
    json.dumps({
        "Docker":80,
        "AWS":60
    }),
    json.dumps({
        "AI":60,
        "Backend":25,
        "Research":15
    }),
    "Active"
),

(
    None,
    "EMP002",
    "Sagar Patil",
    "sagar@gmail.com",
    "9876543211",
    "Backend",
    "Software Engineer",
    "Priya Shah",
    "2024-06-15",
    4,
    "Mumbai",
    json.dumps({
        "Java":95,
        "Spring Boot":90,
        "SQL":88
    }),
    4.3,
    94,
    json.dumps([4.0,4.1,4.2,4.3,4.3,4.3]),
    json.dumps([92,93,94,95,94,96]),
    18,
    json.dumps([
        "Oracle Java",
        "AWS Developer"
    ]),
    json.dumps({
        "Microservices":75,
        "Docker":85
    }),
    json.dumps({
        "Backend":70,
        "API":20,
        "Support":10
    }),
    "Active"
)

]

cursor.executemany("""

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
performance_rating,
attendance,
performance_trend,
attendance_trend,
projects_completed,
certifications,
learning_progress,
project_distribution,
status

)

VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)

""", employees)

documents = [

(
    1,
    None,
    "Resume",
    "uploads/Rahul_Sharma.pdf",
    "Uploaded",
    "Verified"
),

(
    2,
    None,
    "Resume",
    "uploads/Sneha_Patil.pdf",
    "Uploaded",
    "Verified"
),

(
    3,
    None,
    "Resume",
    "uploads/Aditi_Joshi.pdf",
    "Uploaded",
    "Verified"
),

(
    4,
    None,
    "Resume",
    "uploads/Rohan_Shah.pdf",
    "Uploaded",
    "Pending"
)

]

cursor.executemany("""

INSERT INTO candidate_documents(

candidate_id,
employee_id,
document_name,
file_path,
upload_status,
verification_status

)

VALUES(?,?,?,?,?,?)

""", documents)

# -----------------------------
# JOBS
# -----------------------------

jobs = [

(
    "AI Engineer",
    "Develop and deploy AI/ML models for intelligent recruitment solutions.",
    "Python, Machine Learning, SQL, FastAPI",
    "2-4 Years",
    "₹10-15 LPA",
    "Pune",
    80,
    "Open",
    "2026-08-01"
),

(
    "Backend Developer",
    "Develop REST APIs and scalable backend services.",
    "Java, Spring Boot, MySQL",
    "1-3 Years",
    "₹8-12 LPA",
    "Bangalore",
    75,
    "Open",
    "2026-08-02"
),

(
    "Data Scientist",
    "Analyze data, build predictive models and create dashboards.",
    "Python, Pandas, TensorFlow, SQL",
    "2-5 Years",
    "₹12-18 LPA",
    "Hyderabad",
    85,
    "Open",
    "2026-08-03"
),

(
    "Frontend Developer",
    "Develop responsive React applications.",
    "React, JavaScript, CSS",
    "1-3 Years",
    "₹7-10 LPA",
    "Mumbai",
    70,
    "Closed",
    "2026-07-28"
)

]

cursor.executemany("""

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

""", jobs)

# -----------------------------
# JOB APPLICATIONS
# -----------------------------

applications = [

(
1,
"Rahul Sharma",
"rahul@gmail.com",
"uploads/Rahul_Sharma.pdf",
"2026-08-01",
92,
95,
85,
"",
"Shortlisted"
),

(
1,
"Aditi Joshi",
"aditi@gmail.com",
"uploads/Aditi_Joshi.pdf",
"2026-08-02",
96,
97,
90,
"",
"Interview"
),

(
2,
"Sneha Patil",
"sneha@gmail.com",
"uploads/Sneha_Patil.pdf",
"2026-08-03",
88,
90,
80,
"",
"Shortlisted"
),

(
4,
"Rohan Shah",
"rohan@gmail.com",
"uploads/Rohan_Shah.pdf",
"2026-08-04",
81,
84,
75,
"",
"Review"
)

]
cursor.executemany("""

INSERT INTO job_applications(

job_id,
candidate_name,
candidate_email,
resume_path,
applied_date,
ats_score,
skill_match,
experience_match,
ai_report,
status

)

VALUES(?,?,?,?,?,?,?,?,?,?)

""", applications)

# -----------------------------
# ONBOARDING
# -----------------------------

onboarding = [

(
    1,
    "Offer Accepted",
    40,
    "2026-08-15",
    "Pending"
),

(
    2,
    "Documents Submitted",
    70,
    "2026-08-18",
    "Approved"
),

(
    3,
    "Completed",
    100,
    "2026-08-10",
    "Approved"
)

]

cursor.executemany("""

INSERT INTO onboarding(

candidate_id,
onboarding_status,
onboarding_progress,
joining_date,
hr_status

)

VALUES(?,?,?,?,?)

""", onboarding)

# -----------------------------
# DOCUMENT VERIFICATION
# -----------------------------

verification = [

(
    1,
    "Resume",
    98.5,
    1.2,
    "Verified",
    "No issues detected"
),

(
    2,
    "Resume",
    95.0,
    2.8,
    "Verified",
    "Looks authentic"
),

(
    3,
    "Resume",
    99.1,
    0.5,
    "Verified",
    "Excellent quality"
),
(
    4,
    "Resume",
    82.0,
    12.5,
    "Pending",
    "Awaiting verification"
)

]

cursor.executemany("""

INSERT INTO document_verification(

candidate_id,
document_name,
trust_score,
fraud_probability,
ai_result,
remarks

)

VALUES(?,?,?,?,?,?)

""", verification)

# -----------------------------
# ONBOARDING TIMELINE
# -----------------------------

timeline = [

(
    1,
    "Offer Sent",
    "Completed"
),

(
    1,
    "Documents Uploaded",
    "Completed"
),

(
    1,
    "Background Verification",
    "Pending"
),

(
    2,
    "Offer Sent",
    "Completed"
),

(
    2,
    "Joining Scheduled",
    "Completed"
)

]

cursor.executemany("""

INSERT INTO onboarding_timeline(

candidate_id,
event_name,
event_status

)

VALUES(?,?,?)

""", timeline)
conn.commit()

conn.close()

print("Dummy Data Inserted Successfully!")

