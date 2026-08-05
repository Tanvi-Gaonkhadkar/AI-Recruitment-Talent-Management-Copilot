from backend.ollama_client import ask_llama


def analyze_candidate(resume_text, jd_text, matching_result):
    """
    Generate AI explanation based on resume, job description
    and matching results.
    """

    prompt = f"""
You are an experienced HR Recruiter.

Below is the candidate's resume.

=========================
RESUME
=========================

{resume_text}

=========================
JOB DESCRIPTION
=========================

{jd_text}

=========================
MATCHING RESULT
=========================

Matched Skills:
{matching_result["matched"]}

Missing Skills:
{matching_result["missing"]}

Extra Skills:
{matching_result["extra"]}

Skill Match Score:
{matching_result["skill_score"]}%

=========================
TASK

Generate a professional hiring report.

Return in Markdown.

Include:

## Candidate Summary

(3-4 lines)

## Technical Strengths

## Soft Skills

## Missing Skills

## Suitable Roles

## Hiring Recommendation

Choose ONE:

- Reject
- Hold
- HR Interview
- Technical Interview
- Final Interview

## Reason

Explain your recommendation in 3-4 lines.
"""

    return ask_llama(prompt)