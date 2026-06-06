from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class JobDescriptionCreate(BaseModel):
    title: str | None = None
    company_name: str | None = None
    location: str | None = None
    employee_type: str | None = None
    experience_level: str | None = None
    source_url: str | None = None

    raw_text: str

    summary: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    responsibilities: list[str] | None = None
    jd_metadata: dict[str, Any] | None = None

class JobDescriptionUpdate(BaseModel):
    title: str | None = None
    company_name: str | None = None
    location: str | None = None
    employee_type: str | None = None
    experience_level: str | None = None
    source_url: str | None = None

    raw_text: str | None = None

    summary: str | None = None
    required_skills: list[str] | None = None
    preferred_skills: list[str] | None = None
    responsibilities: list[str] | None = None
    jd_metadata: dict[str, Any] | None = None


class JobDescriptionResponse(BaseModel):
    id: UUID

    title: str | None
    company_name: str | None
    location: str | None
    employee_type: str | None
    experience_level: str | None
    source_url: str | None

    raw_text: str

    summary: str | None
    required_skills: list[str] | None
    preferred_skills: list[str] | None
    responsibilities: list[str] | None
    jd_metadata: dict[str, Any] | None

    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
