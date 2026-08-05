import pdfplumber

def extract_resume_text(pdf_path):

    print("Opening:", pdf_path)

    text = ""

    with pdfplumber.open(pdf_path) as pdf:

        print("Pages:", len(pdf.pages))

        for i, page in enumerate(pdf.pages):

            print("Reading page", i + 1)

            page_text = page.extract_text()

            print("Characters:", len(page_text) if page_text else 0)

            if page_text:
                text += page_text + "\n"

    print("Finished PDF")

    return text