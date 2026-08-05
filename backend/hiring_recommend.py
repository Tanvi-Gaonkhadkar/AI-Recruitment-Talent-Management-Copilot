from backend.ollama_client import ask_llama


def hiring_recommendation(result):
    score = result["matching"]["skill_score"]

    if score >= 85:
        recommendation = "HR Interview"

    elif score >= 70:
        recommendation = "Technical Interview"

    elif score >= 50:
        recommendation = "Hold"

    else:
        recommendation = "Reject"

    prompt = fprompt = f"""
You are a Senior HR Recruiter.

The ATS system has already evaluated the candidate.

==================================================
ATS RESULT
==================================================

ATS Match Score:
{score}%

Final Recommendation:
{recommendation}

Matched Skills:
{result["matching"]["matched"]}

Missing Skills:
{result["matching"]["missing"]}

==================================================
RESUME ANALYSIS
==================================================

{result["analysis"]}

==================================================
YOUR TASK
==================================================

The ATS recommendation is FINAL.

DO NOT change the recommendation.

Your job is ONLY to explain why the ATS produced this decision.

Return your answer in the following format:

## ATS Evaluation Summary

### Candidate Match Score
{score}%

### Final Recommendation
{recommendation}

### Hiring Confidence
(0-100%)

### Risk Level
(Low / Medium / High)

### Top Strengths
- ...
- ...
- ...

### Top Weaknesses
- ...
- ...
- ...

### Suggested Salary Level
(Entry / Junior / Mid / Senior)

### HR Explanation
Explain in 3-5 professional sentences why this recommendation is appropriate.

Do NOT recommend a different outcome.
"""

    return ask_llama(prompt)