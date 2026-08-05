from backend.ollama_client import ask_llama
from backend.ai_parser import parse_json


def evaluate_answer(
    resume_data,
    jd_data,
    question,
    answer
):
    """
    Evaluate a single interview answer.
    """

    prompt = f"""
You are an experienced Technical Interviewer.

Candidate Resume:
{resume_data}

Job Description:
{jd_data}

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate the answer.

Return ONLY valid JSON.

{{
    "score": 8,
    "confidence": 85,
    "feedback": "Good answer with minor improvements.",
    "strengths": [
        "...",
        "..."
    ],
    "weaknesses": [
        "...",
        "..."
    ],
    "follow_up": "Ask about scalability."
}}
"""

    response = ask_llama(prompt)

    print("\n========== RAW LLM RESPONSE ==========")
    print(response)
    print("=====================================\n")

    return parse_json(response)

def generate_final_report(interview_data):

    prompt = f"""
You are an HR Interview Panel.

Interview Conversation:

{interview_data}

Generate the final assessment.

Return ONLY JSON.

{{
    "technical_score":85,
    "communication_score":80,
    "confidence_score":88,
    "overall_score":84,
    "recommendation":"Recommended",
    "summary":"Candidate performed well overall."
}}
"""

    response = ask_llama(prompt)

    return parse_json(response)