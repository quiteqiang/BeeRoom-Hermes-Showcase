from app.repositories.comments import create_comment
from app.repositories.simple_students import list_students
from app.schemas import Comment, CommentCreate, TextIngest
from app.services.roster_matcher import match_student_refs
from app.services.transcript_normalizer import normalize_transcript


def ingest_text(payload: TextIngest) -> list[Comment]:
    if not payload.text.strip():
        raise ValueError("text must not be empty")

    roster = list_students(payload.class_name)
    match = match_student_refs(normalize_transcript(payload.text).segments, roster)
    comments: list[Comment] = []

    for assignment in match.assignments:
        comments.append(
            create_comment(
                CommentCreate(
                    student_id=assignment.student_id,
                    comment_date=payload.comment_date,
                    topic=payload.topic,
                    category="general",
                    text=assignment.segment.text,
                    evidence=assignment.segment.source_span,
                    source_span=assignment.segment.source_span,
                    confidence=assignment.confidence,
                )
            )
        )
    for segment in match.whole_class:
        comments.append(
            create_comment(
                CommentCreate(
                    student_id=None,
                    comment_date=payload.comment_date,
                    topic=payload.topic,
                    category="whole_class",
                    text=segment.text,
                    evidence=segment.source_span,
                    source_span=segment.source_span,
                    confidence=1.0,
                )
            )
        )
    for unassigned in match.unassigned:
        comments.append(
            create_comment(
                CommentCreate(
                    student_id=None,
                    comment_date=payload.comment_date,
                    topic=payload.topic,
                    category="needs_review",
                    text=unassigned.segment.text,
                    evidence=unassigned.segment.source_span,
                    source_span=unassigned.segment.source_span,
                    confidence=0.0,
                )
            )
        )
    return comments
