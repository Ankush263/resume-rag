from uuid import UUID

from app.db.models import Resume
from app.db.session import get_db
from app.schemas.resume import ResumeCreate, ResumeResponse
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/resumes",
    tags=["Resumes"]
)

@router.post("/", response_model=ResumeResponse)
def create_resume(
    payload: ResumeCreate,
    db: Session = Depends(get_db)
):
    resume = Resume(
        file_name = payload.file_name,
        raw_text = payload.raw_text,
    )

    try:
        db.add(resume)
        db.commit()
        db.refresh(resume)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

    return resume

@router.get("/{resume_id}", response_model=ResumeResponse)
def get_resume_by_id(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    resume = db.query(Resume).filter(Resume.id == resume_id).first()

    if not resume:
        raise HTTPException(status_code=404, details="Resume not found")
    
    return resume
