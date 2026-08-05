from backend.question_generator import generate_questions


class AIInterviewer:
    """
    AI Interview Session Manager.

    Handles:
    - Question generation
    - Interview flow
    - Question navigation
    """

    def __init__(self, resume_data, jd_data):

        self.resume_data = resume_data
        self.jd_data = jd_data

        generated = generate_questions(
            resume_data,
            jd_data
        )

        # Merge all question categories
        self.questions = (
            generated["technical"] +
            generated["hr"] +
            generated["behavioral"]
        )

        self.current_index = 0
        self.answers = []

    # ----------------------------------------------------
    # Current Question
    # ----------------------------------------------------

    def get_current_question(self):

        if self.current_index >= len(self.questions):
            return None

        return self.questions[self.current_index]

    # ----------------------------------------------------
    # Save Candidate Answer
    # ----------------------------------------------------

    def submit_answer(self, answer):

        question = self.questions[self.current_index]

        self.answers.append({

            "question": question,

            "answer": answer

        })

        self.current_index += 1

    # ----------------------------------------------------
    # Interview Finished?
    # ----------------------------------------------------

    def interview_completed(self):

        return self.current_index >= len(self.questions)

    # ----------------------------------------------------
    # Progress
    # ----------------------------------------------------

    def progress(self):

        if len(self.questions) == 0:
            return 0

        return round(
            (self.current_index / len(self.questions)) * 100
        )

    # ----------------------------------------------------
    # Return Entire Conversation
    # ----------------------------------------------------

    def get_interview_data(self):

        return self.answers