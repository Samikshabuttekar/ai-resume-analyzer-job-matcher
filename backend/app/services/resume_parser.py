from io import BytesIO

import pdfplumber
from docx import Document
from pypdf import PdfReader


def extract_text_from_pdf(file_bytes: bytes) -> str:
    """
    Extract text from a PDF while preserving the visual
    reading order as much as possible.
    """

    text = ""

    with pdfplumber.open(BytesIO(file_bytes)) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text(
                x_tolerance=3,
                y_tolerance=3,
            )

            if page_text:
                text += page_text + "\n"

    return text.strip()


def extract_text_from_pdf_fallback(file_bytes: bytes) -> str:
    """
    Fallback PDF extraction using pypdf.
    """

    pdf = PdfReader(BytesIO(file_bytes))

    text = ""

    for page in pdf.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text.strip()


def extract_text_from_docx(file_bytes: bytes) -> str:
    """
    Extract text from a DOCX file.
    """

    document = Document(BytesIO(file_bytes))

    text = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            text.append(paragraph.text.strip())

    return "\n".join(text)


def extract_resume_text(
    file_bytes: bytes,
    content_type: str,
) -> str:
    """
    Extract resume text from PDF or DOCX.
    """

    if content_type == "application/pdf":
        try:
            extracted_text = extract_text_from_pdf(file_bytes)

            if extracted_text:
                return extracted_text

        except Exception:
            pass

        return extract_text_from_pdf_fallback(file_bytes)

    if content_type == (
        "application/vnd.openxmlformats-officedocument"
        ".wordprocessingml.document"
    ):
        return extract_text_from_docx(file_bytes)

    raise ValueError(
        "Unsupported file type. Please upload a PDF or DOCX file."
    )
