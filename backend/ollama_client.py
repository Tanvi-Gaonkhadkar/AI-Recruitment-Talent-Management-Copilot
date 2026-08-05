import ollama

MODEL_NAME = "llama3.2:latest"

def ask_llama(prompt: str) -> str:
    """
    Send a prompt to the local Llama model.
    """

    response = ollama.chat(
        model=MODEL_NAME,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ],
        format="json"        # <-- ADD THIS
    )

    return response["message"]["content"]