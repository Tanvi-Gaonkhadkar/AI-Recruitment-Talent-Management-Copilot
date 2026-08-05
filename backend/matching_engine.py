def compare(resume, jd):

    resume_skills = set()

    # Combine all technical skill categories
    for key in [
        "programmingLanguages",
        "frameworks",
        "libraries",
        "databases",
        "cloudTechnologies",
        "tools"
    ]:

        values = resume.get(key)

        # Handle null values
        if values is None:
            values = []

        # Handle single string
        if isinstance(values, str):
            values = [values]

        resume_skills.update(values)

    jd_skills = jd.get("required_skills")

    if jd_skills is None:
        jd_skills = []

    if isinstance(jd_skills, str):
        jd_skills = [jd_skills]

    jd_skills = set(jd_skills)

    matched = sorted(resume_skills & jd_skills)
    missing = sorted(jd_skills - resume_skills)
    extra = sorted(resume_skills - jd_skills)

    if len(jd_skills) == 0:
        skill_score = 0
    else:
        skill_score = round(
            len(matched) / len(jd_skills) * 100
        )

    return {
        "matched": matched,
        "missing": missing,
        "extra": extra,
        "skill_score": skill_score,
        "matched_count": len(matched),
        "required_count": len(jd_skills),
        "resume_skill_count": len(resume_skills)
    }