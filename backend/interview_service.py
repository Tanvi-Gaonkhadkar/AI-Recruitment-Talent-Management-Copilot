from backend.question_generator import generate_questions
from backend.topic_generator import generate_focus_topics
from backend.ai_interviewer import AIInterviewer
from backend.answer_evaluator import (
    evaluate_answer,
    generate_final_report
)

def get_evaluation_checklist():
    """
    Standard interview evaluation checklist.
    """

    return {
        "technical": [
            "Technical Knowledge",
            "Problem Solving",
            "Coding Quality"
        ],

        "soft_skills": [
            "Communication",
            "Leadership",
            "Teamwork"
        ],

        "professional": [
            "Culture Fit",
            "Learning Ability"
        ]
    }


def interview_service(resume_data, jd_data):
    """
    Generate complete interview kit.
    """

    questions = generate_questions(
        resume_data,
        jd_data
    )

    topics = generate_focus_topics(
        resume_data,
        jd_data
    )

    checklist = get_evaluation_checklist()

    return {
        "questions": questions,
        "topics": topics,
        "checklist": checklist,
        "ai_interviewer": AIInterviewer(
            resume_data,
            jd_data
        )
    }
    
def evaluate_candidate_answer(

    interviewer,

    resume_data,

    jd_data,

    answer

):
    """
    Evaluate current answer
    and move interview forward.
    """

    question = interviewer.get_current_question()

    evaluation = evaluate_answer(

        resume_data,

        jd_data,

        question,

        answer

    )

    interviewer.submit_answer(answer)

    return evaluation

def complete_ai_interview(ai_interviewer):

    return generate_final_report(

        ai_interviewer.get_interview_data()

    )
    