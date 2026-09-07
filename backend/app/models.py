import json
import uuid
from datetime import date, datetime, timezone

from sqlalchemy import Boolean, Date, DateTime, Float, ForeignKey, Index, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.db import Base


class Student(Base):
    __tablename__ = "student"
    __table_args__ = (
        UniqueConstraint("class_name", "student_code", name="uq_student_class_code"),
        Index("ix_student_class_active", "class_name", "active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    display_name: Mapped[str] = mapped_column(String, nullable=False)
    student_code: Mapped[str] = mapped_column(String, nullable=False)
    class_name: Mapped[str] = mapped_column(String, nullable=False)
    year_level: Mapped[int] = mapped_column(Integer, nullable=False)
    aliases_json: Mapped[str] = mapped_column(String, nullable=False, default="[]")
    active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )

    @property
    def aliases(self) -> list[str]:
        return json.loads(self.aliases_json or "[]")


class Comment(Base):
    __tablename__ = "comment"
    __table_args__ = (
        Index("ix_comment_student_date", "student_id", "comment_date"),
        Index("ix_comment_status_date", "review_status", "comment_date"),
    )

    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    student_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid, ForeignKey("student.id", ondelete="RESTRICT"), nullable=True
    )
    comment_date: Mapped[date] = mapped_column(Date, nullable=False)
    topic: Mapped[str | None] = mapped_column(String, nullable=True)
    category: Mapped[str] = mapped_column(String, nullable=False, default="general")
    text: Mapped[str] = mapped_column(String, nullable=False)
    evidence: Mapped[str] = mapped_column(String, nullable=False)
    source_span: Mapped[str | None] = mapped_column(String, nullable=True)
    confidence: Mapped[float] = mapped_column(Float, nullable=False, default=1.0)
    review_status: Mapped[str] = mapped_column(String, nullable=False, default="pending_review")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
