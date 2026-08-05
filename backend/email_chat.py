from backend.ollama_client import ask_llama



def email_chat(
    message,
    candidate_name,
    job_role,
    match_score,
    recommendation,
    resume_analysis,
    chat_history=None
):
    """
    AI Email Assistant
    """

    history = ""

    if chat_history:
        for role, msg in chat_history:
            history += f"{role.upper()}: {msg}\n"

    prompt = f"""
You are an expert HR Recruiter and Email Writing Assistant.

Candidate Details

Candidate Name:
{candidate_name}

Job Role:
{job_role}

ATS Match Score:
{match_score}%

Hiring Recommendation:
{recommendation}

Resume Analysis:
{resume_analysis}

Previous Conversation:
{history}

Recruiter Request:
{message}

Instructions:

- Generate or modify ONLY the email.
- Use the candidate details automatically.
- If the recruiter asks to rewrite, rewrite the previous email.
- If asked to make it shorter, longer, friendlier, or more formal, do exactly that.
- Keep the email professional.
- Include a proper Subject line.
- Return only the email.
"""

    return ask_llama(prompt)