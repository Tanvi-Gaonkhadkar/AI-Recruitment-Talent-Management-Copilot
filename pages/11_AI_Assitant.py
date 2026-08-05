import os
import streamlit as st

from backend.ai_assistant import ai_assistant
from backend.pdf_parser import extract_resume_text

if "logged_in" not in st.session_state or not st.session_state.logged_in:
    st.switch_page("Login.py")
st.set_page_config(
    page_title="AI Recruitment Assistant",
    page_icon="🤖",
    layout="wide"
)

st.title("AI Recruitment Assistant")
st.caption(
    "Chat with AI for recruitment, hiring guidance, interview questions and HR email generation."
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

if "assistant_history" not in st.session_state:
    st.session_state.assistant_history = []

if "document_context" not in st.session_state:
    st.session_state.document_context = ""

# ----------------------------
# Sidebar
# ----------------------------

with st.sidebar:

    st.header("📂 Upload Documents")

    uploaded_files = st.file_uploader(
        "Upload Recruitment Documents",
        type=["pdf"],
        accept_multiple_files=True
    )

    if st.button("Load Documents", width="stretch"):

        context = ""

        if uploaded_files:

            with st.spinner("Reading documents..."):

                for file in uploaded_files:

                    path = os.path.join(
                        UPLOAD_DIR,
                        file.name
                    )

                    with open(path, "wb") as f:
                        f.write(file.getbuffer())

                    context += (
                        f"\n\n===== {file.name} =====\n"
                    )

                    context += extract_resume_text(path)

            st.session_state.document_context = context

            st.success("Documents loaded successfully.")

        else:

            st.warning("Upload at least one PDF.")

    st.divider()

    st.info(
"""
The assistant supports:

• Recruitment Questions

• HR Email Generation

• Interview Questions

• Hiring Guidance

• Resume & JD Context

Only recruitment-related questions are answered.
"""
    )

# ----------------------------
# Show Uploaded Files
# ----------------------------

if st.session_state.document_context:

    with st.expander("📄 Loaded Document Context"):

        st.text(
            st.session_state.document_context[:3000]
        )

# ----------------------------
# Chat
# ----------------------------

for role, msg in st.session_state.assistant_history:

    with st.chat_message(role):

        st.markdown(msg)

question = st.chat_input(
    "Ask a recruitment-related question..."
)

if question:

    st.session_state.assistant_history.append(
        ("user", question)
    )

    with st.chat_message("user"):

        st.markdown(question)

    with st.spinner("Thinking..."):

        answer = ai_assistant(
            question=question,
            document_context=st.session_state.document_context,
            chat_history=st.session_state.assistant_history
        )

    st.session_state.assistant_history.append(
        ("assistant", answer)
    )

    with st.chat_message("assistant"):

        st.markdown(answer)

st.divider()

col1, col2 = st.columns(2)

with col1:

    if st.button("🗑 Clear Chat", width="stretch"):

        st.session_state.assistant_history = []

        st.rerun()

with col2:

    if st.button("🧹 Clear Documents", width="stretch"):

        st.session_state.document_context = ""

        st.success("Uploaded document context removed.")