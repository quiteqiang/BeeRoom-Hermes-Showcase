# BeeRoom × Hermes Showcase

This repository is a sanitized showcase of the BeeRoom business architecture, selected business-code modules, and its integration with Hermes Agent.

It contains no production deployment code, real user data, AI API keys, Telegram credentials, server configuration, database credentials, or local file paths.

## Business goal

Teachers often capture classroom observations as short, informal notes: a student understood a concept, helped a classmate, participated actively, or needs encouragement. BeeRoom turns these observations into reviewable student comments without requiring the teacher to stop and complete a complex form.

A teacher can write a message such as:

> Add a note for Student A: they took the initiative to help a classmate organize the materials today.

The system then:

1. Understands the teacher's natural-language intent.
2. Matches the correct student.
3. Converts the observation into a structured comment.
4. Shows a preview and asks for confirmation before writing.
5. Places the new comment in a review queue.
6. Shows the approved comment in the student's timeline.

## Architecture

```mermaid
flowchart LR
    T[Teacher] --> TG[Messaging channel]
    TG --> H[Hermes Agent\nNatural-language understanding\nand tool orchestration]
    H --> I[Integration layer\nIntent validation\nand API client]
    I --> B[BeeRoom API\nBusiness rules\nand access boundary]
    B --> D[(Business database\nStudents + comments)]
    B --> W[Teacher web interface]
    W --> B
```

Hermes understands intent and selects approved tools. The BeeRoom API validates business rules and performs data access. Hermes never connects directly to the database and never executes arbitrary SQL.

## Core data model

The business model is intentionally kept to two core tables:

| Table | Purpose |
|---|---|
| `student` | Student identity, student code, class, year level, and aliases |
| `comment` | Date, topic, category, comment text, evidence, source, and review status |

Comments reference students through `student_id`. If a name cannot be matched uniquely, the content can remain unassigned for review rather than being attached to the wrong student.

## Message flow

```text
Teacher's natural-language message
  → Hermes identifies the action, student, date, and content
  → Student lookup and uniqueness check
  → Write preview
  → Explicit teacher confirmation
  → BeeRoom business API call
  → Comment enters the review queue
  → Teacher approval
  → Comment appears in the student timeline
```

## Integration principles

- The API is the only business data read/write entry point.
- Every write operation requires explicit confirmation.
- Ambiguous student names require a follow-up question; Hermes must not guess.
- New comments enter a pending-review state by default.
- Original natural-language input can be retained as source context, but does not bypass structured validation.
- User-facing errors are understandable and do not expose internal identifiers, paths, or credentials.
- The showcase uses abstract component names and placeholders only; it does not connect to a real service.

## Documentation

- [Business and Hermes integration architecture](docs/business-architecture.md)

## Business code snapshot

The public code is organized around the business flow:

```text
backend/app/models.py          two-table persistence model
backend/app/schemas/            API contracts
backend/app/repositories/      student and comment operations
backend/app/services/           matching and text ingestion
backend/app/api/                student and comment endpoints
frontend/src/                   teacher-facing workflow pages
```

This is a reviewable business-code snapshot. Deployment files, environment files, database snapshots, provider adapters, messaging credentials, and local development server settings are intentionally excluded.

## Showcase scope

This repository explains the business problem, user flow, Hermes responsibilities, API boundary, two-table model, review workflow, and privacy principles.

It intentionally does not provide production credentials, real service endpoints, deployment scripts, database snapshots, or an unrestricted natural-language-to-SQL executor.

## Disclaimer

This is architecture material for demonstration purposes, not a deployable production system. A real deployment requires separately managed authentication, access control, secret management, logging, backups, data retention, and privacy controls. Those operational details do not belong in this public repository.
