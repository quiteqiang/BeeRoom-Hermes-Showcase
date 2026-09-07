import json
import uuid

from sqlalchemy import select

from app.db import get_session
from app.models import Student as StudentModel
from app.schemas import Student


def _to_student(model: StudentModel) -> Student:
    return Student.model_validate(model)


def create_student(
    *,
    display_name: str,
    student_code: str,
    class_name: str,
    year_level: int,
    aliases: list[str] | None = None,
) -> Student:
    name = display_name.strip()
    code = student_code.strip()
    group = class_name.strip()
    cleaned_aliases = [alias.strip() for alias in (aliases or []) if alias.strip()]
    if not name or not code or not group:
        raise ValueError("display_name, student_code, and class_name must not be empty")
    if year_level < 1 or year_level > 5:
        raise ValueError("year_level must be between 1 and 5")

    with get_session() as session:
        existing = session.scalar(
            select(StudentModel).where(
                StudentModel.class_name == group,
                StudentModel.student_code == code,
            )
        )
        if existing is not None:
            if (
                existing.display_name == name
                and existing.year_level == year_level
                and existing.aliases == cleaned_aliases
            ):
                return _to_student(existing)
            raise ValueError("student_code already exists in class")

        model = StudentModel(
            id=uuid.uuid4(),
            display_name=name,
            student_code=code,
            class_name=group,
            year_level=year_level,
            aliases_json=json.dumps(cleaned_aliases, ensure_ascii=False),
        )
        session.add(model)
        session.commit()
        session.refresh(model)
        return _to_student(model)


def list_students(class_name: str | None = None) -> list[Student]:
    with get_session() as session:
        query = select(StudentModel).where(StudentModel.active.is_(True)).order_by(
            StudentModel.class_name, StudentModel.student_code
        )
        if class_name is not None:
            query = query.where(StudentModel.class_name == class_name.strip())
        return [_to_student(model) for model in session.scalars(query).all()]


def get_student(student_id: uuid.UUID) -> Student | None:
    with get_session() as session:
        model = session.get(StudentModel, student_id)
        return _to_student(model) if model is not None else None
