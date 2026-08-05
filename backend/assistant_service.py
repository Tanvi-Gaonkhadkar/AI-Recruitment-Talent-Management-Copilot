from backend.assistant_chat import chat_with_assistant


from backend.assistant_chat import chat_with_assistant


def build_context():
    """
    Build recruitment context for the AI assistant.

    Later this function will fetch data from:
    - Resume Analyzer
    - Candidate Screening
    - Interview Copilot
    """

    context = """
Current Recruitment Status

Top Candidates

1. Rahul Sharma
ATS Score: 92
Recommendation: Technical Interview

Skills:
Python
Machine Learning
SQL

--------------------------------------

2. Sneha Patil
ATS Score: 84
Recommendation: Technical Interview

Skills:
Python
React
MongoDB

--------------------------------------

3. Aditi Joshi
ATS Score: 68
Recommendation: Hold

Interview Focus

• Verify Docker knowledge.
• Discuss AI Recruitment Copilot project.
• Evaluate problem-solving ability.

Recruitment Summary

Total Candidates: 4

Shortlisted: 2

Hold: 1

Rejected: 1
"""

    return context


def assistant_service(user_prompt):

    context = build_context()

    answer = chat_with_assistant(
        user_prompt=user_prompt,
        context=context
    )

    return {
        "question": user_prompt,
        "answer": answer
    }