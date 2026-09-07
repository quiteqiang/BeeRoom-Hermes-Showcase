import uuid

from fastapi import APIRouter, HTTPException
from fastapi import Query

from app.db import get_session
from app.models import Comment as CommentModel
from app.models import Student as StudentModel
from app.repositories.comments import (
    COMMENT_CATEGORIES,
    REVIEW_STATUSES,
    create_comment,
    list_comments,
    list_review_queue,
)
from app.schemas import Comment, CommentCreate, CommentEdit, TextIngest
from app.services.simple_ingest import ingest_text

router = APIRouter()


def _serialize(model: CommentModel) -> Comment:
    return Comment.model_validate(model)


@router.post("/comments", response_model=Comment)
def create_comment_endpoint(payload: CommentCreate) -> Comment:
    try:
        return create_comment(payload)
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/comments/ingest-text", response_model=list[Comment])
def ingest_text_endpoint(payload: TextIngest) -> list[Comment]:
    try:
        return ingest_text(payload)
    except (KeyError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/comments", response_model=list[Comment])
def list_comments_endpoint(
    class_name: str | None = None,
    review_status: str | None = Query(None),
    category: str | None = Query(None),
) -> list[Comment]:
    if review_status is not None and review_status not in REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="invalid review_status")
    if category is not None and category not in COMMENT_CATEGORIES:
        raise HTTPException(status_code=400, detail="invalid category")
    return list_comments(class_name=class_name, review_status=review_status, category=category)


@router.get("/comments/review-queue", response_model=list[Comment])
def review_queue_endpoint(class_name: str | None = None) -> list[Comment]:
    return list_review_queue(class_name)


@router.post("/comments/{comment_id}/approve", response_model=Comment)
def approve_comment(comment_id: uuid.UUID) -> Comment:
    with get_session() as session:
        model = session.get(CommentModel, comment_id)
        if model is None:
            raise HTTPException(status_code=404, detail="comment not found")
        model.review_status = "approved"
        session.commit()
        session.refresh(model)
        return _serialize(model)


@router.post("/comments/{comment_id}/edit", response_model=Comment)
def edit_comment(comment_id: uuid.UUID, payload: CommentEdit) -> Comment:
    if payload.category is not None and payload.category not in COMMENT_CATEGORIES:
        raise HTTPException(status_code=400, detail="invalid category")
    with get_session() as session:
        model = session.get(CommentModel, comment_id)
        if model is None:
            raise HTTPException(status_code=404, detail="comment not found")
        if (
            "student_id" in payload.model_fields_set
            and payload.student_id is not None
            and session.get(StudentModel, payload.student_id) is None
        ):
            raise HTTPException(status_code=404, detail="student not found")
        if payload.text is not None:
            if not payload.text.strip():
                raise HTTPException(status_code=400, detail="text must not be empty")
            model.text = payload.text.strip()
        if payload.evidence is not None:
            if not payload.evidence.strip():
                raise HTTPException(status_code=400, detail="evidence must not be empty")
            model.evidence = payload.evidence.strip()
        if payload.source_span is not None:
            model.source_span = payload.source_span.strip() or None
        if payload.category is not None:
            model.category = payload.category
        if "student_id" in payload.model_fields_set:
            model.student_id = payload.student_id
        model.review_status = "edited"
        session.commit()
        session.refresh(model)
        return _serialize(model)


@router.post("/comments/{comment_id}/reject", response_model=Comment)
def reject_comment(comment_id: uuid.UUID) -> Comment:
    with get_session() as session:
        model = session.get(CommentModel, comment_id)
        if model is None:
            raise HTTPException(status_code=404, detail="comment not found")
        model.review_status = "rejected"
        session.commit()
        session.refresh(model)
        return _serialize(model)
