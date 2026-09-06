from fastapi import FastAPI
from backend.app.routes.health import router as health_router
from backend.app.routes.resume import router as resume_router

app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for analyzing resumes and matching them with job descriptions",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(resume_router, prefix="/resume", tags=["Resume"])