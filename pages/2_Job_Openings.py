import streamlit as st
import pandas as pd
from datetime import datetime

from database.database import get_job_applications, get_jobs, save_job, update_job, update_job_status


# PAGE CONFIG

st.set_page_config(
    page_title="Job Openings",
    page_icon="💼",
    layout="wide"
)

# AI FUNCTIONS

def generate_job_description(title, skills, experience, location):
    return f"""
We are looking for a motivated {title} to join our team in {location}.

The ideal candidate should have {experience} of experience and strong
knowledge of {skills}.

Responsibilities:
• Work on projects related to {title}
• Develop and implement effective solutions
• Collaborate with cross-functional teams
• Analyze requirements and deliver high-quality results
• Follow industry best practices

Requirements:
• {skills}
• Strong problem-solving and communication skills
• Ability to work effectively in a team environment

Location: {location}
Experience: {experience}
"""


def suggest_skills(title):
    title_lower = title.lower()

    if "data scientist" in title_lower:
        return "Python, Machine Learning, SQL, Pandas, NumPy, Scikit-learn, Data Visualization"

    elif "machine learning" in title_lower:
        return "Python, Machine Learning, NumPy, Pandas, Scikit-learn, TensorFlow, SQL"

    elif "java" in title_lower:
        return "Java, OOP, DSA, SQL, Spring Boot, Git, REST APIs"

    elif "web" in title_lower or "frontend" in title_lower:
        return "HTML, CSS, JavaScript, React, Git, REST APIs"

    elif "backend" in title_lower:
        return "Python, Java, Node.js, SQL, REST APIs, Git"

    elif "data analyst" in title_lower:
        return "SQL, Python, Excel, Power BI, Tableau, Data Visualization"

    else:
        return "Communication, Problem Solving, Teamwork, Python, SQL, Git"


def improve_jd(jd):
    return f"""
{jd.strip()}

The selected candidate should demonstrate strong communication,
problem-solving abilities, teamwork, adaptability, and a commitment
to delivering high-quality work.
"""


# HEADER

st.title("💼 Job Openings")
st.caption("Create, manage and monitor your organization's job openings.")


# TABS

tab1, tab2 = st.tabs([
    "➕ Create Job",
    "📋 Manage Jobs"
])


# CREATE JOB

with tab1:

    st.subheader("Create New Job Opening")

    col1, col2 = st.columns(2)

    with col1:

        job_title = st.text_input(
            "Job Title",
            placeholder="e.g. Data Scientist"
        )

        experience = st.text_input(
            "Experience",
            placeholder="e.g. 0-2 Years"
        )

        salary = st.text_input(
            "Salary",
            placeholder="e.g. ₹6 - ₹10 LPA"
        )

    with col2:

        location = st.text_input(
            "Location",
            placeholder="e.g. Hyderabad / Remote"
        )

        ats_cutoff = st.number_input(
            "ATS Cutoff (%)",
            min_value=0,
            max_value=100,
            value=70
        )

        st.write("")


    # REQUIRED SKILLS

    st.markdown("### 🛠️ Required Skills")

    skills = st.text_area(
        "Skills",
        placeholder="Python, SQL, Machine Learning...",
        height=100
    )

    if st.button("✨ Suggest Required Skills"):

        if job_title.strip():

            suggested = suggest_skills(job_title)

            st.session_state.suggested_skills = suggested

            st.success("AI suggested skills successfully!")

        else:
            st.warning("Please enter a Job Title first.")

    if "suggested_skills" in st.session_state:

        st.info(
            f"🤖 AI Suggestion:\n\n"
            f"{st.session_state.suggested_skills}"
        )

        if st.button("Use Suggested Skills"):

            skills = st.session_state.suggested_skills

            st.rerun()


    # JOB DESCRIPTION

    st.markdown("### 📝 Job Description")

    job_description = st.text_area(
        "Description",
        placeholder="Write the job description here...",
        height=220
    )

    ai_col1, ai_col2 = st.columns(2)

    with ai_col1:

        if st.button(
            "✨ Generate Job Description",
            use_container_width=True
        ):

            if not job_title:
                st.warning("Please enter Job Title.")

            elif not skills:
                st.warning("Please enter Required Skills.")

            else:

                generated = generate_job_description(
                    job_title,
                    skills,
                    experience,
                    location
                )

                st.session_state.generated_jd = generated

                st.success("AI generated the Job Description!")

    with ai_col2:

        if st.button(
            "✨ Improve JD Language",
            use_container_width=True
        ):

            if not job_description.strip():

                st.warning(
                    "Please enter a Job Description first."
                )

            else:

                improved = improve_jd(job_description)

                st.session_state.improved_jd = improved

                st.success("JD language improved!")


    # GENERATED JD

    if "generated_jd" in st.session_state:

        st.markdown("#### 🤖 AI Generated Job Description")

        st.text_area(
            "Generated JD",
            value=st.session_state.generated_jd,
            height=250,
            key="generated_jd_display"
        )

        if st.button("Use Generated JD"):

            st.session_state.final_jd = (
                st.session_state.generated_jd
            )

            st.success("Generated JD selected!")


    # IMPROVED JD

    if "improved_jd" in st.session_state:

        st.markdown("#### ✨ Improved Job Description")

        st.text_area(
            "Improved JD",
            value=st.session_state.improved_jd,
            height=250,
            key="improved_jd_display"
        )

        if st.button("Use Improved JD"):

            st.session_state.final_jd = (
                st.session_state.improved_jd
            )

            st.success("Improved JD selected!")


    # FINAL JD

    final_description = st.session_state.get(
        "final_jd",
        job_description
    )

    st.divider()


    # PUBLISH JOB

    if st.button(
        "🚀 Publish Job",
        type="primary",
        use_container_width=True
    ):

        if not job_title:
            st.error("Job Title is required.")

        elif not final_description:
            st.error("Job Description is required.")

        elif not skills:
            st.error("Required Skills are required.")

        else:

            save_job(
                job_title,
                final_description,
                skills,
                experience,
                salary,
                location,
                ats_cutoff,
                "Open",
                datetime.now().strftime("%d-%m-%Y")
            )

            st.success(f"🎉 {job_title} has been published successfully!")
            st.balloons()
            st.rerun()


# MANAGE JOBS

with tab2:

    st.subheader("📋 Manage Job Openings")

    jobs = get_jobs()

    if jobs.empty:

        st.info(
            "No job openings available yet. "
            "Create your first job opening."
        )

    else:

        for _, job in jobs.iterrows():

            with st.container(border=True):

                top1, top2, top3 = st.columns([3, 2, 1])

                with top1:

                    st.markdown(
                        f"### 💼 {job['job_title']}"
                    )

                    st.caption(
                        f"📍 {job['location']}  •  "
                        f"💰 {job['salary']}"
                    )

                with top2:

                    if job["status"] == "Open":
                        st.success("🟢 OPEN")
                    else:
                        st.error("🔴 CLOSED")

                    st.write(
                        f"ATS Cutoff: **{job['ats_cutoff']}%**"
                    )

                with top3:

                    st.write(
                        f"**Experience**\n"
                        f"{job['experience']}"
                    )

                st.divider()

                st.write(
                    f"**Required Skills:** "
                    f"{job['required_skills']}"
                )

                st.write(
                    f"**Created:** {job['created_date']}"
                )

                action1, action2, action3 = st.columns(3)


                # VIEW APPLICATIONS

                with action1:

                    if st.button(
                        "👥 View Applications",
                        key=f"view_{job['id']}",
                        use_container_width=True
                    ):

                        st.session_state.selected_job = (
                            job["id"]
                        )


                # EDIT JOB

                with action2:

                    if st.button(
                        "✏️ Edit Job",
                        key=f"edit_{job['id']}",
                        use_container_width=True
                    ):

                        st.session_state[
                            f"editing_{job['id']}"
                        ] = True


                # CLOSE JOB

                with action3:

                    if job["status"] == "Open":

                        if st.button(
                            "🔒 Close Job",
                            key=f"close_{job['id']}",
                            use_container_width=True
                        ):

                            update_job_status(job["id"], "Closed")

                            st.success(
                                "Job opening closed."
                            )

                            st.rerun()

                    else:

                        st.button(
                            "🔒 Closed",
                            key=f"closed_{job['id']}",
                            disabled=True,
                            use_container_width=True
                        )


                # EDIT FORM

                if st.session_state.get(
                    f"editing_{job['id']}",
                    False
                ):

                    st.markdown("#### ✏️ Edit Job")

                    new_title = st.text_input(
                        "Job Title",
                        value=job["job_title"],
                        key=f"title_edit_{job['id']}"
                    )

                    new_description = st.text_area(
                        "Job Description",
                        value=job["job_description"],
                        height=200,
                        key=f"desc_edit_{job['id']}"
                    )

                    new_skills = st.text_input(
                        "Required Skills",
                        value=job["required_skills"],
                        key=f"skills_edit_{job['id']}"
                    )

                    edit_col1, edit_col2 = st.columns(2)

                    with edit_col1:

                        new_experience = st.text_input(
                            "Experience",
                            value=job["experience"],
                            key=f"exp_edit_{job['id']}"
                        )

                        new_salary = st.text_input(
                            "Salary",
                            value=job["salary"],
                            key=f"salary_edit_{job['id']}"
                        )

                    with edit_col2:

                        new_location = st.text_input(
                            "Location",
                            value=job["location"],
                            key=f"location_edit_{job['id']}"
                        )

                        new_cutoff = st.number_input(
                            "ATS Cutoff",
                            min_value=0,
                            max_value=100,
                            value=int(job["ats_cutoff"]),
                            key=f"cutoff_edit_{job['id']}"
                        )

                    save_col, cancel_col = st.columns(2)

                    with save_col:

                        if st.button(
                            "💾 Save Changes",
                            key=f"save_{job['id']}",
                            type="primary"
                        ):

                            update_job(
                                job["id"],               # Primary key from database
                                new_title,
                                new_description,
                                new_skills,
                                new_experience,
                                new_salary,
                                new_location,
                                new_cutoff
                            )

                            st.success(
                                "Job updated successfully!"
                            )

                            st.session_state[
                                f"editing_{job['id']}"
                            ] = False

                            st.rerun()

                    with cancel_col:

                        if st.button(
                            "Cancel",
                            key=f"cancel_{job['id']}"
                        ):

                            st.session_state[
                                f"editing_{job['id']}"
                            ] = False

                            st.rerun()


                # APPLICATIONS

                if st.session_state.get(
                    "selected_job"
                ) == job["id"]:

                    st.divider()

                    st.markdown("### 👥 Applications")

                    applications = get_job_applications(job["id"])

                    if applications.empty:

                        st.info("No applications found for this job.")

                    else:

                        for _, app in applications.iterrows():

                            score = app["ats_score"]

                            if score >= job["ats_cutoff"]:
                                status = "🟢 Meets ATS Cutoff"
                            else:
                                status = "🔴 Below ATS Cutoff"

                            c1, c2, c3, c4 = st.columns(4)

                            with c1:

                                st.write(
                                    f"**{app['candidate_name']}**"
                                )

                            with c2:

                                st.metric(
                                    "ATS Score",
                                    f"{score}%"
                                )

                            with c3:

                                st.write(
                                    f"Skill Match: "
                                    f"**{app['skill_match']}%**"
                                )

                                st.write(
                                    f"Experience: "
                                    f"**{app['experience_match']}%**"
                                )

                            with c4:

                                st.write(status)

                                if score >= job["ats_cutoff"]:

                                    if st.button(
                                        "✅ Shortlist",
                                        key=(
                                            f"shortlist_"
                                            f"{job['id']}_"
                                            f"{app['candidate_name']}"
                                        )
                                    ):

                                        st.success(
                                            f"{app['candidate_name']} shortlisted!"
                                        )

                                else:

                                    st.button(
                                        "Below Cutoff",
                                        key=(
                                            f"below_"
                                            f"{job['id']}_"
                                            f"{app['candidate_name']}"
                                        ),
                                        disabled=True
                                    )