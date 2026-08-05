from backend.ollama_client import ask_llama

def generate_model_answer(question):

    prompt = f"""
You are an expert technical interviewer.

Question:
{question}

Generate:

1. Ideal Answer
2. Key Points
3. Common Mistakes

Return ONLY markdown.
"""

    return ask_llama(prompt)