from dataclasses import dataclass
from difflib import SequenceMatcher
from uuid import UUID

from app.schemas import Student
from app.services.transcript_normalizer import StudentSegment

_WHOLE_CLASS_LABELS = {"全班", "大家", "全体", "whole class", "whole-class", "class"}


@dataclass(frozen=True)
class StudentMatch:
    segment: StudentSegment
    student_id: UUID
    confidence: float


@dataclass(frozen=True)
class MatchCandidate:
    student_id: UUID
    display_name: str
    score: float


@dataclass(frozen=True)
class UnassignedSegment:
    segment: StudentSegment
    candidates: list[MatchCandidate]


@dataclass(frozen=True)
class MatchResult:
    assignments: list[StudentMatch]
    whole_class: list[StudentSegment]
    unassigned: list[UnassignedSegment]


def _normalize_label(label: str) -> str:
    return label.strip().lower()


def match_student_refs(segments: list[StudentSegment], roster: list[Student]) -> MatchResult:
    exact: dict[str, Student | None] = {}
    for student in roster:
        _add_exact_match(exact, student.display_name, student)
        for alias in student.aliases:
            _add_exact_match(exact, alias, student)

    assignments: list[StudentMatch] = []
    whole_class: list[StudentSegment] = []
    unassigned: list[UnassignedSegment] = []

    for segment in segments:
        label = segment.speaker_label
        if label is None:
            unassigned.append(UnassignedSegment(segment=segment, candidates=[]))
            continue

        normalized = _normalize_label(label)
        if normalized in _WHOLE_CLASS_LABELS:
            whole_class.append(segment)
            continue

        student = exact.get(normalized)
        if student is not None:
            assignments.append(StudentMatch(segment=segment, student_id=student.id, confidence=1.0))
            continue

        candidates: list[MatchCandidate] = []
        for roster_student in roster:
            names = [roster_student.display_name, *roster_student.aliases]
            score = max(SequenceMatcher(None, normalized, _normalize_label(name)).ratio() for name in names)
            if score >= 0.6:
                candidates.append(
                    MatchCandidate(student_id=roster_student.id, display_name=roster_student.display_name, score=score)
                )
        candidates.sort(key=lambda candidate: candidate.score, reverse=True)
        unassigned.append(UnassignedSegment(segment=segment, candidates=candidates[:3]))

    return MatchResult(assignments=assignments, whole_class=whole_class, unassigned=unassigned)


def _add_exact_match(index: dict[str, Student | None], label: str, student: Student) -> None:
    normalized = _normalize_label(label)
    if normalized not in index:
        index[normalized] = student
        return
    if index[normalized] is None:
        return
    if index[normalized].id != student.id:
        index[normalized] = None
