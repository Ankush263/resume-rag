import uuid

from app.db.session import Base
from pgvector.sqlalchemy import VECTOR
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func


class Resume(Base):
    __tablename__ = "resumes"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    file_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    raw_text: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

class JobDescription(Base):
    __tablename__ = "jobdescription"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    company_name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    location: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True
    )

    employee_type: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    experience_level: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    source_url: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    raw_text: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    summary: Mapped[str | None] = mapped_column(
        Text,
        nullable=True
    )

    required_skills = mapped_column(
        JSONB,
        nullable=True
    )

    preferred_skills = mapped_column(
        JSONB,
        nullable=True
    )

    responsibilities = mapped_column(
        JSONB,
        nullable=True
    )

    jd_metadata = mapped_column(
        JSONB,
        nullable=True,
    )

    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False
    )

class DocumentChunk(Base):
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    document_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    resume_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="CASCADE"),
        nullable=True,
    )

    job_description_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("jobdescription.id", ondelete="CASCADE"),
        nullable=True,
    )

    chunk_index: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    chunk_text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    token_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    # Use 1536 if you use OpenAI text-embedding-3-small.
    # If your embedding model has a different dimension, change this now. 
    embedding: Mapped[list[float] | None] = mapped_column(
        VECTOR(3072),
        nullable=True,
    )

    embedding_model: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
    )

    chunk_metadata = mapped_column(
        JSONB,
        nullable=True,
    )

    content_hash: Mapped[str | None] = mapped_column(
        String(64),
        nullable=True,
    )

    created_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint(
            "document_type IN ('resume', 'job_description')",
            name="ck_document_chunks_document_type",
        ),
        CheckConstraint(
            """
            (
                document_type = 'resume'
                AND resume_id IS NOT NULL
                AND job_description_id IS NULL
            )
            OR
            (
                document_type = 'job_description'
                AND job_description_id IS NOT NULL
                AND resume_id IS NULL
            )
            """,
            name="ck_document_chunks_valid_document_reference",
        ),
        UniqueConstraint(
            "resume_id",
            "chunk_index",
            name="uq_document_chunks_resume_chunk_index",
        ),
        UniqueConstraint(
            "job_description_id",
            "chunk_index",
            name="uq_document_chunks_jd_chunk_index",
        ),
    )
