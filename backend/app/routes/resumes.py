from uuid import UUID

from app.db.models import DocumentChunk, Resume
from app.db.session import get_db
from app.schemas.document_chunk import DocumentChunkResponse
from app.schemas.resume import ResumeCreate, ResumeResponse
from app.services.chunking import chunk_text_by_words
from fastapi import APIRouter, Depends, HTTPException, status
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

@router.post(
    "/{resume_id}/chunks/generate",
    response_model=list[DocumentChunkResponse],
)
def generate_resume_chunk(
    resume_id: UUID,
    db: Session = Depends(get_db)
):
    resume = (
        db.query(Resume)
        .filter(Resume.id == resume_id)
        .first()
    )

    if not resume:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="resume not found",
        )
    
    chunks = chunk_text_by_words(
        text=resume.raw_text,
        max_words=180,
        overlap_words=40
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="resume description raw text is empty"
        )
    
    db.query(DocumentChunk).filter(
        DocumentChunk.resume_id == resume_id
    ).delete(synchronize_session=False)

    created_chunks = []

    for chunk in chunks:
        resume_chunk = DocumentChunk(
            document_type="resume",
            resume_id=resume_id,
            job_description_id=None,
            chunk_index=chunk["chunk_index"],
            chunk_text=chunk["chunk_text"],
            token_count=chunk["token_count"],
            embedding=None,
            embedding_model=None,
            chunk_metadata={
                "source": "resume",
                "chunking_strategy": "word_overlap",
                "max_words": 180,
                "overlap_words": 40,
            },
            content_hash=chunk["content_hash"],
        )

        db.add(resume_chunk)
        created_chunks.append(resume_chunk)

    db.commit()

    for chunk in created_chunks:
        db.refresh(chunk)

    return created_chunks
