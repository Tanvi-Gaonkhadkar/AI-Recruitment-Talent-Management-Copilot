
"""
AI Recruitment Assistant
"""

import streamlit as st

from backend.ollama_client import ask_llama
from backend.scope_guard import is_in_scope, OUT_OF_SCOPE_MESSAGE


# ----------------------------------------------------------
# Build Recruitment Context
# ----------------------------------------------------------

def build_context(
    candidate_rankings=None,
    hiring_summary=None,
    analytics=None
):
    """
    Build recruitment context.

    If no live data is available, sample recruitment data is used.
    """

    # -------------------------
    # Sample Data
    # -------------------------

    if candidate_rankings is None:
        candidate_rankings = [
            {
                "name": "Rahul Sharma",
                "score": 92,
                "recommendation": "Technical Interview",
                "skills": ["Python", "Machine Learning", "SQL"],
            },
            {
                "name": "Sneha Patil",
                "score": 84,
                "recommendation": "Technical Interview",
                "skills": ["Python", "React", "MongoDB"],
            },
            {
                "name": "Aditi Joshi",
                "score": 68,
                "recommendation": "Hold",
                "skills": ["Java", "HTML", "CSS"],
            },
        ]

    if hiring_summary is None:
        hiring_summary = {
            "total": 4,
            "shortlisted": 2,
            "hold": 1,
            "rejected": 1,
        }

    if analytics is None:
        analytics = """
Interview Focus

• Verify Docker knowledge.
• Discuss AI Recruitment Copilot project.
• Evaluate problem-solving ability.
"""

    # -------------------------
    # Build Context
    # -------------------------
    # NOTE: the summary/analytics append and the return used to live INSIDE
    # this loop, so build_context() was returning after the first candidate
    # only (Rahul), and Sneha/Aditi never reached the model. Fixed by
    # dedenting them to run once, after the loop finishes.

    context = "Current Recruitment Status\n\n"
    context += "Top Candidates\n\n"

    for i, candidate in enumerate(candidate_rankings, start=1):
        context += f"""
{i}. {candidate['name']}

ATS Score: {candidate['score']}

Recommendation: {candidate['recommendation']}

Skills:
{", ".join(candidate["skills"])}

--------------------------------

"""

    context += f"""
Recruitment Summary

Total Candidates: {hiring_summary['total']}

Shortlisted: {hiring_summary['shortlisted']}

Hold: {hiring_summary['hold']}

Rejected: {hiring_summary['rejected']}

"""

    context += analytics

    return context

def needs_candidate_context(question):
    question = question.lower()

    keywords = [
        "candidate",
        "candidates",
        "ats",
        "score",
        "ranking",
        "rank",
        "compare",
        "comparison",
        "recommendation",
        "shortlist",
        "best candidate",
        "top candidate",
        "weakest candidate",
        "recruitment summary",
        "hold",
        "rejected"
    ]

    return any(k in question for k in keywords)
# ----------------------------------------------------------
# Main Assistant
# ----------------------------------------------------------

def ai_assistant(
    question,
    document_context="",
    chat_history=None,
    candidate_rankings=None,
    hiring_summary=None,
    analytics=None
):
    chat_history = chat_history or []

    if not is_in_scope(question, chat_history, document_context):
        
        return OUT_OF_SCOPE_MESSAGE

    # -------------------------
    # Recruitment Context
    # -------------------------
    if needs_candidate_context(question):
        project_context = build_context(
            candidate_rankings,
            hiring_summary,
            analytics
        )
    else:
        project_context = ""

    uploaded_context = (
        document_context.strip()
        if document_context.strip()
        else "No uploaded documents provided."
    )

    # -------------------------
    # Chat History (rendered as text for the prompt)
    # -------------------------
    history = ""
    for role, msg in chat_history:
        history += f"{role.upper()}: {msg}\n"

    # -------------------------
    # AI Prompt
    # -------------------------
    prompt = f"""
You are an AI Recruitment & Talent Acquisition Assistant.

Your role is to assist recruiters throughout the hiring process.

You answer ONLY Recruitment & Talent Acquisition related questions.

You can help with:

• Resume Analysis
• Candidate Screening
• Candidate Ranking
• Candidate Comparison
• ATS Matching
• Skill Gap Analysis
• Hiring Recommendations
• Interview Planning
• HR Email Generation
• Recruitment Analytics
• Job Descriptions
• Recruitment Best Practices

==================================================

PRIORITY RULES

1. If the user's question is about candidates, rankings, ATS scores, hiring decisions, or recruitment analytics, use the Recruitment Context as the primary source.

2. If uploaded documents (Resume, JD, HR Policy, etc.) contain relevant information, use them together with the Recruitment Context.

3. If the question is a GENERAL recruitment question (such as hiring strategy, interview process, onboarding, ATS, recruitment trends, HR best practices, etc.) and it is NOT answered by the Recruitment Context, answer using your recruitment knowledge.

4. If both Recruitment Context and uploaded documents partially answer the question, combine both with your recruitment knowledge.

5. Never invent candidate names, ATS scores, recommendations, skills, or experience that are not present in the Recruitment Context or uploaded documents.

6. If the requested information is unavailable, clearly state that it is unavailable.

==================================================

WHEN ANSWERING ABOUT CANDIDATES

If the question is about:

• Best candidate
• Top candidates
• Weakest candidate
• Least skilled candidate
• Highest ATS score
• Lowest ATS score
• Candidate ranking
• Candidate comparison
• Shortlisting
• Rejection
• Hiring recommendation

Always explain your reasoning using:

• ATS Score
• Skills
• Recommendation
• Experience (if available)
• Job fit

Do not return only candidate names unless the user specifically asks for names only.

==================================================

RECRUITMENT CONTEXT

{project_context}

IMPORTANT:

Use the Recruitment Context ONLY when the user's question is about:
- Candidates
- ATS Scores
- Rankings
- Candidate Comparison
- Hiring Recommendations
- Recruitment Summary

For general recruitment questions (such as interview preparation, HR best practices, recruitment strategies, onboarding, etc.), answer directly without mentioning or summarizing the Recruitment Context.

==================================================

UPLOADED DOCUMENTS

{uploaded_context}

==================================================

CHAT HISTORY

{history}

==================================================

USER QUESTION

{question}

Use the Recruitment Context whenever applicable.

Use Uploaded Documents whenever applicable.

If both are relevant, combine both.

If neither contains the answer but the question is recruitment-related, answer using recruitment and HR best practices.

Never invent candidate information.

Provide a professional, concise, recruiter-focused response.

Return only the answer."""

    answer = ask_llama(prompt)

    return answer