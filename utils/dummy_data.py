import pandas as pd

def hiring_funnel():

    return pd.DataFrame({
        "Stage":[
            "Applications",
            "Screened",
            "Shortlisted",
            "Interviewed",
            "Selected",
            "Hired"
        ],
        "Candidates":[
            500,
            320,
            150,
            60,
            25,
            18
        ]
    })


def candidate_sources():

    return pd.DataFrame({
        "Source":[
            "LinkedIn",
            "Naukri",
            "Referral",
            "Website"
        ],
        "Candidates":[
            45,
            30,
            15,
            10
        ]
    })


def recent_candidates():

    return pd.DataFrame({

        "Candidate":[
            "Rahul Sharma",
            "Sneha Patil",
            "Aditi Joshi",
            "Rohan Shah"
        ],

        "Role":[
            "AI Engineer",
            "Backend Developer",
            "Data Scientist",
            "Frontend Developer"
        ],

        "Match":[
            "92%",
            "88%",
            "95%",
            "81%"
        ],

        "Status":[
            "Shortlisted",
            "Interview",
            "Selected",
            "Review"
        ]
    })