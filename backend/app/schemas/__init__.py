from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentCreate(BaseModel):
    display_name: str
    student_code: str
    class_name: str
    year_level: int
    aliases: list[str] = Field(default_factory=list)


class Student(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    display_name: str
    student_code: str
    class_name: str
    year_level: int
    aliases: list[str]
    active: bool
    created_at: datetime


_COMMENT_CATEGORIES = {
    "behaviour",
    "interaction",
    "encouragement",
    "learning",
    "general",
    "whole_class",
    "needs_review",
}


class CommentCreate(BaseModel):
    student_id: UUID | None = None
    comment_date: date
    topic: str | None = None
    category: str = "general"
    text: str
    evidence: str
    source_span: str | None = None
    confidence: float = Field(default=1.0, ge=0.0, le=1.0)


class CommentEdit(BaseModel):
    text: str | None = None
    evidence: str | None = None
    source_span: str | None = None
    category: str | None = None
    student_id: UUID | None = None


class Comment(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    student_id: UUID | None
    comment_date: date
    topic: str | None
    category: str
    text: str
    evidence: str
    source_span: str | None
    confidence: float
    review_status: str
    created_at: datetime
    updated_at: datetime


class TextIngest(BaseModel):
    comment_date: date
    class_name: str | None = None
    topic: str | None = None
    text: str
