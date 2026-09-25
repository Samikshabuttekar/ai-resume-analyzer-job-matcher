from fastapi import APIRouter, UploadFile, File, Form, HTTPException

from backend.app.services.resume_parser import extract_resume_text
from backend.app.services.resume_analyzer import analyze_resume
from backend.app.services.job_matcher import match_resume_to_job


router = APIRouter()


SUPPORTED_CONTENT_TYPES = {
    "application/pdf",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def validate_resume_file(file: UploadFile) -> None:
    if file.content_type not in SUPPORTED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail=(
                "Unsupported file type. "
                "Please upload a PDF or DOCX file."
            ),
        )


@router.post("/upload")
async def upload_resume(
    file: UploadFile = File(...),
):
    """
    Upload and analyze a resume.

    Supports PDF and DOCX files.
    """

    validate_resume_file(file)

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty.",
        )

    try:
        extracted_text = extract_resume_text(
            file_bytes,
            file.content_type,
        )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text from the resume. "
                    "Please upload a text-based PDF or DOCX file."
                ),
            )

        analysis = analyze_resume(extracted_text)

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while analyzing the resume.",
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Resume uploaded and analyzed successfully",
        "text": extracted_text,
        "analysis": analysis,
    }


@router.post("/match")
async def match_resume(
    file: UploadFile = File(...),
    job_description: str = Form(...),
):
    """
    Upload a resume and match it against a job description.

    Supports PDF and DOCX resumes.
    """

    validate_resume_file(file)

    if not job_description.strip():
        raise HTTPException(
            status_code=400,
            detail="Job description is required.",
        )

    file_bytes = await file.read()

    if not file_bytes:
        raise HTTPException(
            status_code=400,
            detail="The uploaded resume is empty.",
        )

    try:
        extracted_text = extract_resume_text(
            file_bytes,
            file.content_type,
        )

        if not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail=(
                    "Could not extract text from the resume. "
                    "Please upload a text-based PDF or DOCX file."
                ),
            )

        analysis = analyze_resume(extracted_text)

        match_result = match_resume_to_job(
            extracted_text,
            analysis["skills"],
            job_description,
        )

    except HTTPException:
        raise

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred while matching the resume.",
        )

    return {
        "filename": file.filename,
        "message": "Resume matched with job description successfully",
        "match": match_result,
    }
