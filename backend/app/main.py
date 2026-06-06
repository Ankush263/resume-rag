from app.db.session import get_db
from app.routes.job_description import router as job_description_router
from app.routes.resumes import router as resume_router
from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

app = FastAPI(
    title="Resume RAG API",
    version="1.0.0"
)

@app.get("/")
def healthcheck(db: Session = Depends(get_db)):
    return {
        "status": "ok"
    }

app.include_router(resume_router)
app.include_router(job_description_router)
