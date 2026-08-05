import json
from backend.ollama_client import ask_llama

import json
import re


def parse_json(response):

    print("\n========== BEFORE JSON PARSE ==========")
    print(response)
    print("=======================================\n")

    # keep your existing code below

    response = response.replace("```json", "")
    response = response.replace("```", "")
    response = response.strip()

    start = response.find("{")
    end = response.rfind("}")

    if start == -1:
        raise ValueError("No JSON object found.")

    # If the model forgot the final brace, add it
    if end == -1 or end < start:
        response = response[start:] + "}"
    else:
        response = response[start:end + 1]

    return json.loads(response)

def extract_resume_info(text):

    prompt = f"""
You are an expert ATS Resume Parser.

Extract information ONLY from the resume.

Do NOT invent or assume anything.

Extract the following:

1. Programming Languages
2. Frameworks
3. Libraries
4. Databases
5. Cloud Technologies
6. Tools
7. Experience
8. Education
9. Projects

Return ONLY valid JSON.

Example:

{{
    "skills": [
        "Python",
        "Java",
        "FastAPI",
        "React",
        "SQL",
        "MongoDB"
    ],

    "experience":[
        "Software Development Intern",
        "Open Source Contributor"
    ],

    "education":[
        "Bachelor of Engineering in Computer Science"
    ],

    "projects":[
        "Newsroom AI Co-Writer",
        "Wonderland",
        "Sales Forecasting"
    ]
}}
IMPORTANT:

Return ONLY valid JSON.

Do not write:

- Here is the JSON
- Explanation
- Notes
- Markdown
- ```json

Return ONLY the JSON object.
Resume

{text}
"""

    response = ask_llama(prompt)

    return parse_json(response)

def extract_jd_info(text):

    prompt = f"""
You are an ATS Job Description Parser.

Extract ONLY the required information.

Do NOT explain anything.

Return ONLY valid JSON.

Example

{{
    "required_skills":[
        "Python",
        "FastAPI",
        "Docker",
        "AWS",
        "SQL"
    ],

    "experience":"3-5 Years",

    "education":"B.E./B.Tech"
}}
IMPORTANT:

Return ONLY valid JSON.

Do not write:

- Here is the JSON
- Explanation
- Notes
- Markdown
- ```json

Return ONLY the JSON object.

Job Description

{text}
"""

    response = ask_llama(prompt)

    # print("\n========== RAW JD RESPONSE ==========\n")
    # print(response)
    # print("\n=====================================\n")

    return parse_json(response)