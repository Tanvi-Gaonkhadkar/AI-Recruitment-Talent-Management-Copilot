from backend.ollama_client import ask_llama


def generate_email(
    candidate_name,
    job_title,
    email_type,
    recommendation,
    company="ABC Technologies"
):

    prompt = f"""
You are an HR Manager.

Candidate Name:
{candidate_name}

Job Role:
{job_title}

Recommendation:
{recommendation}

Email Type:
{email_type}

Company:
{company}

Generate a professional email.

Possible Email Types:

- Interview Invitation
- Offer Letter
- Rejection
- Hold Candidate
- Follow-up

The email should include:

Subject

Greeting

Professional Body

Closing

HR Team Signature

Return only the email.
"""

    return ask_llama(prompt)