"""
Careers Portal Service

Runs "Run AI Resume Analysis" for a single job application.

This mirrors backend/resume_service.py's analyze_resume() pipeline,
but a Job Opening's description is stored as plain text in the
`jobs` table (not a PDF), so this version accepts job_description_text
directly instead of a second PDF path.
"""

from backend.pdf_parser import extract_resume_text

from backend.ai_parser import (
    extract_resume_info,
    extract_jd_info
)

from backend.matching_engine import compare
from backend.resume_analyzer_ai import analyze_candidate


def analyze_application(resume_path, job_description_text):
    """
    Complete Careers Portal Resume Analysis Pipeline

    Parameters
    ----------
    resume_path : str
        Path to the candidate's uploaded resume PDF.

    job_description_text : str
        The job's job_description text, straight from the jobs table.

    Returns
    -------
    dict with ats_score, skill_match, experience_match,
    matching details and the AI-generated report.
    """

    # Step 1 - Extract resume text
    resume_text = extract_resume_text(resume_path)

    # Step 2 - Convert resume + JD to structured JSON
    resume_json = extract_resume_info(resume_text)
    jd_json = extract_jd_info(job_description_text)

    # Step 3 - Compare resume against JD requirements
    matching = compare(resume_json, jd_json)

    # Step 4 - AI-generated hiring report
    ai_report = analyze_candidate(
        resume_text,
        job_description_text,
        matching
    )

    skill_match = matching["skill_score"]

    # The matching engine only produces a skill-based score today —
    # there is no separate experience-matching model yet, so both
    # figures are derived from the same skill match for now. Swap
    # this out once a dedicated experience-scoring module exists.
    experience_match = skill_match
    ats_score = skill_match

    return {
        "resume_text": resume_text,
        "resume_json": resume_json,
        "jd_json": jd_json,
        "matching": matching,
        "ats_score": ats_score,
        "skill_match": skill_match,
        "experience_match": experience_match,
        "ai_report": ai_report
    }