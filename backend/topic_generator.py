from backend.ollama_client import ask_llama
from backend.ai_parser import parse_json


def generate_focus_topics(resume_data, jd_data):
    """
    Generate AI-suggested interview focus topics based on
    parsed resume and job description.

    Parameters
    ----------
    resume_data : dict
        Output from extract_resume_info()

    jd_data : dict
        Output from extract_jd_info()

    Returns
    -------
    dict
        {
            "strong_areas": [],
            "weak_areas": [],
            "project_discussion": [],
            "missing_skill_verification": []
        }
    """

    prompt = f"""
You are a Senior Technical Interviewer.

Your task is to analyze the candidate's resume and the job description.

Candidate Resume

Skills:
{resume_data.get("skills", [])}

Projects:
{resume_data.get("projects", [])}

Experience:
{resume_data.get("experience", [])}

Education:
{resume_data.get("education", [])}


Job Description

Required Skills:
{jd_data.get("required_skills", [])}

Required Experience:
{jd_data.get("experience", "")}

Required Education:
{jd_data.get("education", "")}


Instructions

Analyze the candidate and generate interview focus areas.

Return exactly four sections.

1. strong_areas
- Skills matching the job description.
- Technologies the candidate appears comfortable with.
- Areas requiring only moderate verification.

Generate exactly 5 points.

2. weak_areas
- Skills that seem weak or insufficient.
- Areas where evidence is limited.
- Technologies requiring deeper questioning.

Generate exactly 5 points.

3. project_discussion
Suggest important project-related discussion points.

Focus on:
- Architecture
- Technologies used
- Challenges faced
- Candidate contribution
- Outcomes

Generate exactly 5 points.

4. missing_skill_verification
List important job skills that are missing or not clearly demonstrated in the resume.

Generate exactly 5 points.

Return ONLY valid JSON.

Example

{{
    "strong_areas": [
        "Python Programming",
        "Machine Learning",
        "SQL",
        "REST APIs",
        "Problem Solving"
    ],

    "weak_areas": [
        "Docker",
        "AWS",
        "Kubernetes",
        "CI/CD",
        "System Design"
    ],

    "project_discussion": [
        "Explain the architecture of the AI Recruitment Copilot.",
        "Describe challenges faced during development.",
        "Discuss database design decisions.",
        "Explain model integration.",
        "Discuss project scalability."
    ],

    "missing_skill_verification": [
        "Cloud Deployment",
        "Containerization",
        "DevOps",
        "Caching",
        "Microservices"
    ]
}}

IMPORTANT

Return ONLY valid JSON.

Do NOT write explanations.

Do NOT use markdown.

Do NOT use ```json.

Every key and string must use double quotes.
"""

    response = ask_llama(prompt)

    return parse_json(response)