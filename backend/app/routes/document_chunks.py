from uuid import UUID

from app.db.models import DocumentChunk, JobDescription, Resume
from app.db.session import get_db
from app.schemas.document_chunk import (
    DocumentChunkCreate,
    DocumentChunkResponse,
)
from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.orm import Session

router = APIRouter(
    prefix="/document-chunks",
    tags=["Document Chunks"],
)


@router.post(
    "/",
    response_model=DocumentChunkResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_document_chunk(
    payload: DocumentChunkCreate,
    db: Session = Depends(get_db),
):
    if payload.document_type not in ["resume", "job_description"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="document_type must be either 'resume' or 'job_description'",
        )

    if payload.document_type == "resume":
        if not payload.resume_id or payload.job_description_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For resume chunks, resume_id is required and job_description_id must be null",
            )

        resume = db.query(Resume).filter(Resume.id == payload.resume_id).first()

        if not resume:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Resume not found",
            )

    if payload.document_type == "job_description":
        if not payload.job_description_id or payload.resume_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="For job description chunks, job_description_id is required and resume_id must be null",
            )

        job_description = (
            db.query(JobDescription)
            .filter(JobDescription.id == payload.job_description_id)
            .first()
        )

        if not job_description:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Job description not found",
            )

    chunk = DocumentChunk(**payload.model_dump())

    db.add(chunk)
    db.commit()
    db.refresh(chunk)

    return chunk


@router.get(
    "/",
    response_model=list[DocumentChunkResponse],
)
def get_document_chunks(
    db: Session = Depends(get_db),
    document_type: str | None = Query(default=None),
    resume_id: UUID | None = Query(default=None),
    job_description_id: UUID | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
):
    query = db.query(DocumentChunk)

    if document_type:
        query = query.filter(DocumentChunk.document_type == document_type)

    if resume_id:
        query = query.filter(DocumentChunk.resume_id == resume_id)

    if job_description_id:
        query = query.filter(DocumentChunk.job_description_id == job_description_id)

    return (
        query
        .order_by(DocumentChunk.chunk_index.asc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.get(
    "/{chunk_id}",
    response_model=DocumentChunkResponse,
)
def get_document_chunk_by_id(
    chunk_id: UUID,
    db: Session = Depends(get_db),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document chunk not found",
        )

    return chunk


@router.delete(
    "/{chunk_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_document_chunk(
    chunk_id: UUID,
    db: Session = Depends(get_db),
):
    chunk = db.query(DocumentChunk).filter(DocumentChunk.id == chunk_id).first()

    if not chunk:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Document chunk not found",
        )

    db.delete(chunk)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)
