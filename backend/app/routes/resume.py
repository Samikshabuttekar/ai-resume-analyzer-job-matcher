from fastapi import APIRouter, UploadFile, File, HTTPException

from backend.app.services.resume_parser import extract_resume_text

router = APIRouter()


@router.post("/upload")
async def upload_resume(file: UploadFile = File(...)):
    if file.content_type not in [
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ]:
        raise HTTPException(
            status_code=400,
            detail="Unsupported file type. Please upload a PDF or DOCX file.",
        )

    file_bytes = await file.read()

    try:
        extracted_text = extract_resume_text(
            file_bytes,
            file.content_type,
        )
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )

    return {
        "filename": file.filename,
        "content_type": file.content_type,
        "message": "Resume uploaded and text extracted successfully",
        "text": extracted_text,
    }