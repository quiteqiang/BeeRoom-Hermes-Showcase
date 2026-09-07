import re
from dataclasses import dataclass


@dataclass(frozen=True)
class StudentSegment:
    speaker_label: str | None
    text: str
    source_span: str


@dataclass(frozen=True)
class NormalizedTranscript:
    text: str
    segments: list[StudentSegment]


_MARKER_RE = re.compile(r"([A-Za-z]+(?:[ '-][A-Za-z]+){0,2}|[\u4e00-\u9fff]{2,4})\s*[:：]")
_WHITESPACE_RE = re.compile(r"\s+")


def _collapse(text: str) -> str:
    return _WHITESPACE_RE.sub(" ", text).strip()


def split_by_student_markers(text: str) -> list[StudentSegment]:
    matches = list(_MARKER_RE.finditer(text))
    if not matches:
        cleaned = text.strip()
        return [StudentSegment(speaker_label=None, text=_collapse(cleaned), source_span=cleaned)] if cleaned else []

    segments: list[StudentSegment] = []
    if matches[0].start() > 0:
        prefix = text[: matches[0].start()].strip()
        if prefix:
            segments.append(StudentSegment(speaker_label=None, text=_collapse(prefix), source_span=prefix))

    for index, match in enumerate(matches):
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        source_span = text[match.start() : end].strip()
        body = text[match.end() : end]
        segments.append(
            StudentSegment(
                speaker_label=match.group(1).strip(),
                text=_collapse(body),
                source_span=source_span,
            )
        )
    return segments


def normalize_transcript(raw: str) -> NormalizedTranscript:
    return NormalizedTranscript(text=_collapse(raw), segments=split_by_student_markers(raw))
