from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentChunkCreate(BaseModel):
    document_type: str  # "resume" or "job_description"

    resume_id: UUID | None = None
    job_description_id: UUID | None = None

    chunk_index: int
    chunk_text: str

    token_count: int | None = None
    embedding: list[float] | None = None
    embedding_model: str | None = None

    chunk_metadata: dict[str, Any] | None = None
    content_hash: str | None = None


class DocumentChunkResponse(BaseModel):
    id: UUID
    document_type: str

    resume_id: UUID | None
    job_description_id: UUID | None

    chunk_index: int
    chunk_text: str

    token_count: int | None
    embedding_model: str | None

    chunk_metadata: dict[str, Any] | None
    content_hash: str | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)