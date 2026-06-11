from uuid import UUID

from app.db.models import DocumentChunk, JobDescription
from app.db.session import get_db
from app.schemas.document_chunk import DocumentChunkResponse
from app.schemas.job_description import (
    JobDescriptionCreate,
    JobDescriptionResponse,
    JobDescriptionUpdate,
)
from app.services.chunking import chunk_text_by_words
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/job-descriptions",
    tags=["Job Descriptions"],
)


@router.post(
    "/",
    response_model=JobDescriptionResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_job_description(
    payload: JobDescriptionCreate,
    db: Session = Depends(get_db),
):
    job_description = JobDescription(**payload.model_dump())

    db.add(job_description)
    db.commit()
    db.refresh(job_description)

    return job_description


@router.get(
    "/",
    response_model=list[JobDescriptionResponse],
)
def get_job_descriptions(
    db: Session = Depends(get_db),
    q: str | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=20, ge=1, le=100),
):
    query = db.query(JobDescription)

    if q:
        search = f"%{q}%"
        query = query.filter(
            or_(
                JobDescription.title.ilike(search),
                JobDescription.company_name.ilike(search),
                JobDescription.raw_text.ilike(search),
            )
        )

    return (
        query
        .order_by(JobDescription.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/{jd_id}",
    response_model=JobDescriptionResponse,
)
def get_job_description_by_id(
    jd_id: UUID,
    db: Session = Depends(get_db),
):
    job_description = (
        db.query(JobDescription)
        .filter(JobDescription.id == jd_id)
        .first()
    )

    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    return job_description


@router.patch(
    "/{jd_id}",
    response_model=JobDescriptionResponse,
)
def update_job_description(
    jd_id: UUID,
    payload: JobDescriptionUpdate,
    db: Session = Depends(get_db),
):
    job_description = (
        db.query(JobDescription)
        .filter(JobDescription.id == jd_id)
        .first()
    )

    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    update_data = payload.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        setattr(job_description, key, value)

    db.commit()
    db.refresh(job_description)

    return job_description


@router.delete(
    "/{jd_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_job_description(
    jd_id: UUID,
    db: Session = Depends(get_db),
):
    job_description = (
        db.query(JobDescription)
        .filter(JobDescription.id == jd_id)
        .first()
    )

    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    db.delete(job_description)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{jd_id}/chunks/generate",
    response_model=list[DocumentChunkResponse],
)
def generate_job_description_chunks(
    jd_id: UUID,
    db: Session = Depends(get_db),
):
    job_description = (
        db.query(JobDescription)
        .filter(JobDescription.id == jd_id)
        .first()
    )

    if not job_description:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Job description not found",
        )

    chunks = chunk_text_by_words(
        text=job_description.raw_text,
        max_words=180,
        overlap_words=40,
    )

    if not chunks:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Job description raw_text is empty",
        )

    # Delete old chunks for this JD before regenerating
    db.query(DocumentChunk).filter(
        DocumentChunk.job_description_id == jd_id
    ).delete(synchronize_session=False)

    created_chunks = []

    for chunk in chunks:
        document_chunk = DocumentChunk(
            document_type="job_description",
            resume_id=None,
            job_description_id=jd_id,
            chunk_index=chunk["chunk_index"],
            chunk_text=chunk["chunk_text"],
            token_count=chunk["token_count"],
            embedding=None,
            embedding_model=None,
            chunk_metadata={
                "source": "job_description",
                "chunking_strategy": "word_overlap",
                "max_words": 180,
                "overlap_words": 40,
            },
            content_hash=chunk["content_hash"],
        )

        db.add(document_chunk)
        created_chunks.append(document_chunk)

    db.commit()

    for chunk in created_chunks:
        db.refresh(chunk)

    return created_chunks