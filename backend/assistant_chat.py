from backend.ollama_client import ask_llama


def chat_with_assistant(user_prompt, context=""):
    """
    AI Recruitment Assistant

    Parameters
    ----------
    user_prompt : str
        Recruiter's question.

    context : str
        Optional recruitment context from previous modules.

    Returns
    -------
    str
        AI response.
    """

    prompt = f"""
You are an experienced AI Recruitment Copilot.

Your job is to assist recruiters professionally.

You can answer questions about:

- Resume Screening
- Candidate Ranking
- ATS Scores
- Interview Planning
- Hiring Recommendations
- Recruitment Best Practices

Recruitment Context

{context}

Recruiter's Question

{user_prompt}

Instructions

- Be concise.
- Give practical recruiter-focused advice.
- If the answer exists in the recruitment context,
  use it.
- If context is unavailable,
  answer using HR and recruitment best practices.

Return only the answer.
"""

    return ask_llama(prompt)