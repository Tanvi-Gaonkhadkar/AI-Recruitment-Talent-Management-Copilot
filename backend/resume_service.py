import os

from backend.pdf_parser import extract_resume_text
from backend.jd_parser import extract_jd_text

from backend.ai_parser import (
    extract_resume_info,
    extract_jd_info
)

from backend.matching_engine import compare
from backend.resume_analyzer_ai import analyze_candidate


def analyze_resume(resume_pdf, jd_pdf):
    """
    Complete Resume Analysis Pipeline
    """

    # Step 1 - Extract text
    print("Step 1: Extract Resume")
    resume_text = extract_resume_text(resume_pdf)
    print("Resume extracted")

    print("Step 2: Extract JD")
    jd_text = extract_jd_text(jd_pdf)
    print("JD extracted")

    print("Step 3: Resume JSON")
    resume_json = extract_resume_info(resume_text)
    print("Resume JSON done")

    print("Step 4: JD JSON START")
    jd_json = extract_jd_info(jd_text)
    print("Step 4: JD JSON END")
    
    print("Step 5 START")
    matching = compare(resume_json, jd_json)
    print("Step 5 END")

    print("Step 6: AI Summary")
    ai_summary = analyze_candidate(
        resume_text,
        jd_text,
        matching
    )
    print("AI Summary done")

    return {
        "resume_text": resume_text,
        "jd_text": jd_text,
        "resume_json": resume_json,
        "jd_json": jd_json,
        "matching": matching,
        "analysis": ai_summary
    }