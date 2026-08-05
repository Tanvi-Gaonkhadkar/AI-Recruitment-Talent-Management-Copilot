import os

from backend.resume_service import analyze_resume


def rank_candidates(resume_paths, jd_path):

    candidates = []

    for resume in resume_paths:

        print("=" * 50)
        print("Resume:", resume)
        print("Type:", type(resume))
        print("Exists:", os.path.exists(resume) if isinstance(resume, str) else "Not a string")

        result = analyze_resume(resume, jd_path)

        candidates.append({
            "name": os.path.splitext(os.path.basename(resume))[0],
            "match": result["matching"]["skill_score"],
            "recommendation": result["analysis"],
            "result": result
        })

    candidates.sort(
        key=lambda x: x["match"],
        reverse=True
    )

    for i, c in enumerate(candidates):
        c["rank"] = i + 1

    return candidates