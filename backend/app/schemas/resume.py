from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class ResumeCreate(BaseModel):
    file_name: str
    raw_text: str

class ResumeResponse(BaseModel):
    id: UUID
    file_name: str
    raw_text: str
    created_at: datetime

    class Config:
        from_attributes = True
