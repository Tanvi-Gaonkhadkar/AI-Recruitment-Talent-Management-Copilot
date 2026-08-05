"""
Candidate Screening Service

This service combines all AI modules:

1. Candidate Ranking
2. Hiring Recommendation
3. Resume Comparison
4. Email Generator
"""

import os

from backend.candidate_ranking import rank_candidates
from backend.hiring_recommend import hiring_recommendation
from backend.resume_comparison import compare_candidates
from backend.email_generator import generate_email


def candidate_service(
    resume_paths,
    jd_path,
    job_title="AI Engineer",
    company="ABC Technologies"
):
    """
    Complete Candidate Screening Pipeline

    Parameters
    ----------
    resume_paths : list
        List of resume PDF paths

    jd_path : str
        Job Description PDF

    Returns
    -------
    dict
    """

    # -----------------------------
    # Rank Candidates
    # -----------------------------
    print(resume_paths)
    print(type(resume_paths))
    resume_paths = [
        path
        for path in resume_paths
        if isinstance(path, str) and os.path.exists(path)
    ]

    ranking = rank_candidates(
        resume_paths,
        jd_path
    )

    # -----------------------------
    # Hiring Recommendation
    # -----------------------------

    recommendations = []

    for candidate in ranking:

        report = hiring_recommendation(
            candidate["result"]
        )

        recommendations.append({

            "candidate": candidate["name"],

            "match_score": candidate["match"],

            "recommendation": report

        })

    # -----------------------------
    # Compare Top 2 Candidates
    # -----------------------------

    comparison = None

    if len(ranking) >= 2:

        comparison = compare_candidates(

            ranking[0]["result"],

            ranking[1]["result"]

        )

    # -----------------------------
    # Generate Email
    # -----------------------------

    emails = []

    for candidate in ranking:

        # Simple rule based on score

        if candidate["match"] >= 85:

            email_type = "Interview Invitation"

        elif candidate["match"] >= 60:

            email_type = "Hold Candidate"

        else:

            email_type = "Rejection"

        email = generate_email(

            candidate_name=candidate["name"],

            job_title=job_title,

            email_type=email_type,

            recommendation=email_type,

            company=company

        )

        emails.append({

            "candidate": candidate["name"],

            "email_type": email_type,

            "email": email

        })

    # -----------------------------
    # Final Output
    # -----------------------------

    return {

        "ranking": ranking,

        "recommendations": recommendations,

        "comparison": comparison,

        "emails": emails

    }