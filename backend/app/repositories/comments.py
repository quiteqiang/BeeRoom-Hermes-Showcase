import uuid
from datetime import date

from sqlalchemy import select

from app.db import get_session
from app.models import Comment as CommentModel
from app.models import Student as StudentModel
from app.schemas import Comment, CommentCreate

COMMENT_CATEGORIES = {
    "behaviour",
    "interaction",
    "encouragement",
    "learning",
    "general",
    "whole_class",
    "needs_review",
}
REVIEW_STATUSES = {"pending_review", "approved", "edited", "rejected"}


def _to_comment(model: CommentModel) -> Comment:
    return Comment.model_validate(model)


def _validate_text(value: str, field_name: str) -> str:
    cleaned = value.strip()
    if not cleaned:
        raise ValueError(f"{field_name} must not be empty")
    return cleaned


def create_comment(payload: CommentCreate) -> Comment:
    if payload.category not in COMMENT_CATEGORIES:
        raise ValueError("invalid category")
    text = _validate_text(payload.text, "text")
    evidence = _validate_text(payload.evidence, "evidence")
    source_span = payload.source_span.strip() if payload.source_span else None

    with get_session() as session:
        if payload.student_id is not None and session.get(StudentModel, payload.student_id) is None:
            raise KeyError("student not found")
        model = CommentModel(
            id=uuid.uuid4(),
            student_id=payload.student_id,
            comment_date=payload.comment_date,
            topic=payload.topic.strip() if payload.topic else None,
            category=payload.category,
            text=text,
            evidence=evidence,
            source_span=source_span,
            confidence=payload.confidence,
            review_status="pending_review",
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        return _to_comment(model)


def get_comment(comment_id: uuid.UUID) -> CommentModel | None:
    with get_session() as session:
        return session.get(CommentModel, comment_id)


def list_comments(
    *,
    class_name: str | None = None,
    review_status: str | None = None,
    category: str | None = None,
) -> list[Comment]:
    with get_session() as session:
        query = select(CommentModel).outerjoin(
            StudentModel, CommentModel.student_id == StudentModel.id
        ).order_by(CommentModel.comment_date, CommentModel.created_at)
        if class_name is not None:
            query = query.where(StudentModel.class_name == class_name.strip())
        if review_status is not None:
            query = query.where(CommentModel.review_status == review_status)
        if category is not None:
            query = query.where(CommentModel.category == category)
        return [_to_comment(model) for model in session.scalars(query).all()]


def list_student_comments(
    student_id: uuid.UUID,
    *,
    from_date: date | None = None,
    to_date: date | None = None,
    category: str | None = None,
    review_status: str | None = None,
) -> list[Comment]:
    with get_session() as session:
        if session.get(StudentModel, student_id) is None:
            raise KeyError("student not found")
        query = (
            select(CommentModel)
            .where(CommentModel.student_id == student_id)
            .order_by(CommentModel.comment_date, CommentModel.created_at)
        )
        if from_date is not None:
            query = query.where(CommentModel.comment_date >= from_date)
        if to_date is not None:
            query = query.where(CommentModel.comment_date <= to_date)
        if category is not None:
            query = query.where(CommentModel.category == category)
        if review_status is not None:
            query = query.where(CommentModel.review_status == review_status)
        return [_to_comment(model) for model in session.scalars(query).all()]


def list_review_queue(class_name: str | None = None) -> list[Comment]:
    with get_session() as session:
        query = (
            select(CommentModel)
            .outerjoin(StudentModel, CommentModel.student_id == StudentModel.id)
            .where(CommentModel.review_status == "pending_review")
            .order_by(CommentModel.comment_date, CommentModel.created_at)
        )
        if class_name is not None:
            query = query.where(StudentModel.class_name == class_name.strip())
        return [_to_comment(model) for model in session.scalars(query).all()]
