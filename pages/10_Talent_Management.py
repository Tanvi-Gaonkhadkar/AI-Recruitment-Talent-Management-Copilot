import streamlit as st
import pandas as pd
import plotly.express as px

from database.database import (
    get_employees,
    get_departments,
    get_employee
)
if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")

if st.session_state.role != "HR":
    st.error("🚫 Access Denied. This module is available only to HR.")
    st.stop()
st.set_page_config(
    page_title="Talent Management",
    page_icon="👨‍💼",
    layout="wide"
)

st.title("👨‍💼 Talent Management")
st.caption("AI-powered Employee Performance & Talent Analytics")
employees = get_employees()
if "profile_mode" not in st.session_state:
    st.session_state.profile_mode = False

df = employees.copy()

df.rename(
    columns={
        "name":"Name",
        "employee_id":"Employee ID",
        "department":"Department",
        "designation":"Designation",
        "experience":"Experience",
        "performance_rating":"Rating"
    },
    inplace=True
)

df["Experience"] = df["Experience"].astype(str) + " Years"


c1, c2, c3 = st.columns([2,1,1.3])

with c1:
    search = st.text_input("🔍 Search Employee")

with c2:
    department = st.selectbox(
        "Department",
        ["All"] + get_departments()
    )

with c3:
    employee_name = st.selectbox(
        "Select Employee",
        df["Name"]
    )

# -----------------------------
# Apply Filters
# -----------------------------

# ==============================
# Apply Filters
# ==============================

filtered = df.copy()

if search:
    filtered = filtered[
        filtered["Name"].str.contains(
            search,
            case=False
        )
    ]

if department != "All":
    filtered = filtered[
        filtered["Department"] == department
    ]

employee = get_employee(employee_name)

# ==============================
# Employee List Screen
# ==============================

if not st.session_state.profile_mode:

    left, right = st.columns([1.4, 1])

    with left:

        st.subheader("📋 Employee List")
        filtered = filtered[
            [
                "Employee ID",
                "Name",
                "Department",
                "Designation",
                "Experience",
                "Rating"
            ]
        ]

        st.dataframe(
            filtered,
            hide_index=True,
            use_container_width=True
        )

    with right:

        st.subheader("👤 Employee Details")

        st.write(f"**Employee ID:** {employee['employee_id']}")
        st.write(f"**Designation:** {employee['designation']}")
        st.write(f"**Department:** {employee['department']}")
        st.write(f"**Manager:** {employee['manager']}")
        st.write(f"**Experience:** {employee['experience']} Years")
        st.write(f"**Location:** {employee['location']}")

        st.progress(
            int(employee["performance_rating"] * 20),
            text=f"Performance Rating {employee['performance_rating']}/5"
        )

        if st.button("👤 View Full Profile", use_container_width=True):

            st.session_state.profile_mode = True

            st.rerun()

# ==============================
# Full Profile Screen
# ==============================

else:

    if st.button("⬅ Back"):

        st.session_state.profile_mode = False

        st.rerun()

    st.title(employee["name"])

    st.caption(employee["designation"])

    a, b, c, d = st.columns(4)

    a.metric(
        "Performance",
        employee["performance_rating"]
    )

    b.metric(
        "Attendance",
        f"{employee['attendance']}%"
    )

    c.metric(
        "Projects",
        employee["projects_completed"]
    )

    d.metric(
        "Experience",
        f"{employee['experience']} Years"
    )

    t1, t2, t3, t4, t5 = st.tabs([
        "👤 Profile",
        "📈 Performance",
        "💻 Skills",
        "📚 Learning",
        "🤖 AI Insights"
    ])

    with t1:

        st.subheader("Employee Information")

        st.write(f"**Employee ID:** {employee['employee_id']}")
        st.write(f"**Department:** {employee['department']}")
        st.write(f"**Designation:** {employee['designation']}")
        st.write(f"**Manager:** {employee['manager']}")
        st.write(f"**Email:** {employee['email']}")
        st.write(f"**Phone:** {employee['phone']}")
        st.write(f"**Joining Date:** {employee['joining_date']}")
        st.write(f"**Location:** {employee['location']}")
    with t2:

        st.subheader("📈 Performance Trend")

        perf_df = pd.DataFrame({
            "Month": ["Jan","Feb","Mar","Apr","May","Jun"],
            "Rating": employee["performance_trend"]
        })

        fig = px.line(
            perf_df,
            x="Month",
            y="Rating",
            markers=True,
            title="Performance Trend"
        )

        st.plotly_chart(fig, use_container_width=True)

        st.divider()

        att_df = pd.DataFrame({
            "Month":["Jan","Feb","Mar","Apr","May","Jun"],
            "Attendance":employee["attendance_trend"]
        })

        fig2 = px.bar(
            att_df,
            x="Month",
            y="Attendance",
            title="Monthly Attendance (%)"
        )

        st.plotly_chart(fig2, use_container_width=True)
    with t3:

        st.subheader("💻 Skill Proficiency")

        skills = pd.DataFrame({

            "Skill": list(employee["skills"].keys()),

            "Score": list(employee["skills"].values())

        })

        fig = px.bar(

            skills,

            x="Skill",

            y="Score",

            color="Score",

            text="Score"

        )

        st.plotly_chart(fig, use_container_width=True)

        st.subheader("🏆 Certifications")

        for cert in employee["certifications"]:

            st.success(cert)
    with t4:

        st.subheader("📚 Learning Progress")

        for course, progress in employee["learning_progress"].items():

            st.write(course)

            st.progress(progress)

        st.divider()

        st.subheader("🥧 Project Distribution")

        project_df = pd.DataFrame({

            "Category": list(employee["project_distribution"].keys()),

            "Value": list(employee["project_distribution"].values())

        })

        fig = px.pie(

            project_df,

            names="Category",

            values="Value",

            hole=0.4

        )

        st.plotly_chart(fig, use_container_width=True)
    with t5:

        st.subheader("🤖 AI Employee Insights")

        st.info(f"""

    ### AI Summary

    • {employee['name']} has consistently demonstrated strong performance.

    • Current Performance Rating: **{employee['performance_rating']}/5**

    • Attendance: **{employee['attendance']}%**

    • Projects Completed: **{employee['projects_completed']}**

    • Recommendation:

    Employee is performing well and is suitable for high-impact projects.

    """)