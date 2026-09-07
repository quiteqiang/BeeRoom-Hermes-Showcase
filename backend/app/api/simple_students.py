import uuid
from datetime import date

from fastapi import APIRouter, HTTPException, Query

from app.repositories.comments import REVIEW_STATUSES, list_student_comments
from app.repositories.simple_students import create_student, get_student, list_students
from app.schemas import Student, StudentCreate, Comment

router = APIRouter()


@router.post("/students", response_model=Student)
def create_student_endpoint(payload: StudentCreate) -> Student:
    try:
        return create_student(
            display_name=payload.display_name,
            student_code=payload.student_code,
            class_name=payload.class_name,
            year_level=payload.year_level,
            aliases=payload.aliases,
        )
    except ValueError as exc:
        status = 409 if "already exists" in str(exc) else 400
        raise HTTPException(status_code=status, detail=str(exc)) from exc


@router.get("/students", response_model=list[Student])
def list_students_endpoint(class_name: str | None = None) -> list[Student]:
    return list_students(class_name)


@router.get("/students/{student_id}", response_model=Student)
def get_student_endpoint(student_id: uuid.UUID) -> Student:
    student = get_student(student_id)
    if student is None:
        raise HTTPException(status_code=404, detail="student not found")
    return student


@router.get("/students/{student_id}/comments", response_model=list[Comment])
def list_student_comments_endpoint(
    student_id: uuid.UUID,
    from_: date | None = Query(None, alias="from"),
    to: date | None = None,
    category: str | None = None,
    review_status: str | None = None,
) -> list[Comment]:
    if review_status is not None and review_status not in REVIEW_STATUSES:
        raise HTTPException(status_code=400, detail="invalid review_status")
    try:
        return list_student_comments(
            student_id,
            from_date=from_,
            to_date=to,
            category=category,
            review_status=review_status,
        )
    except KeyError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
