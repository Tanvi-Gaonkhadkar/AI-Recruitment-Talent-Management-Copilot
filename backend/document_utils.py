import os
import tempfile

from backend.pdf_parser import extract_resume_text


def is_ocr_available():
    """
    Returns whether OCR is available.

    Current project supports only PDF parsing,
    so OCR is disabled.
    """
    return False


def extract_text_from_document(uploaded_file):
    """
    Extract text from an uploaded document.

    Supports:
    - Streamlit UploadedFile (.pdf)

    Returns:
        str : extracted text
    """

    if uploaded_file is None:
        return ""

    extension = os.path.splitext(uploaded_file.name)[1].lower()

    # Currently only PDF is supported
    if extension == ".pdf":

        with tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".pdf"
        ) as tmp:

            tmp.write(uploaded_file.getbuffer())
            temp_path = tmp.name

        try:
            text = extract_resume_text(temp_path)
        finally:
            if os.path.exists(temp_path):
                os.remove(temp_path)

        return text

    raise ValueError(
        f"Unsupported document type: {extension}"
    )