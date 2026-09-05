from fastapi import FastAPI

app = FastAPI(
    title="AI Resume Analyzer API",
    description="API for analyzing resumes and matching them with job descriptions",
    version="1.0.0"
)


@app.get("/")
def root():
    return {
        "message": "AI Resume Analyzer API is running"
    }