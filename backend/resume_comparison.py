from backend.ollama_client import ask_llama


def compare_candidates(candidate1, candidate2):

    prompt = f"""
You are a Senior Technical Recruiter.

Compare these two candidates for the same job.

=========================
Candidate 1
=========================

Match Score:
{candidate1["matching"]["skill_score"]}%

Matched Skills:
{candidate1["matching"]["matched"]}

Missing Skills:
{candidate1["matching"]["missing"]}

Resume Analysis:

{candidate1["analysis"]}


=========================
Candidate 2
=========================

Match Score:
{candidate2["matching"]["skill_score"]}%

Matched Skills:
{candidate2["matching"]["matched"]}

Missing Skills:
{candidate2["matching"]["missing"]}

Resume Analysis:

{candidate2["analysis"]}



Compare Candidate 1 and Candidate 2.

Rules:

1. ATS Match Score is the primary deciding factor.

2. Matched Skills are the second factor.

3. Missing required skills should reduce the recommendation.

4. Only recommend both candidates if they are nearly equal.

Provide:

- Candidate 1 Strengths

- Candidate 2 Strengths

- Better Candidate

- Reason

- Final Recommendatio

Return the answer in professional Markdown.
"""

    return ask_llama(prompt)