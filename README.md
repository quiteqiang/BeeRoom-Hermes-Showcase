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

## Hermes feature integration notes

The following notes record how selected Hermes capabilities could be integrated into BeeRoom. Each feature is evaluated at the system boundary first; the public code snapshot remains intentionally provider-neutral and does not contain operational Hermes configuration.

### 1. Tools and toolsets

**Capability.** Hermes groups callable tools into toolsets that can be enabled or disabled per platform. The documented tool categories include web, terminal and file operations, orchestration, memory, automation, and integrations.

**BeeRoom integration.** Add a small, dedicated BeeRoom toolset containing only business-safe operations such as `find_students`, `preview_comment`, `submit_comment`, and `list_review_queue`. Hermes can use read-only tools for lookup and preview; the write tool should be exposed only after an explicit confirmation turn. The integration layer remains an API client, so Hermes never receives database credentials and never generates executable SQL.

**End-to-end flow.** Telegram message → Hermes intent extraction → student lookup tool → disambiguation if needed → preview tool → teacher confirmation → submit tool → BeeRoom API validation → pending comment. The API should enforce the same rules even if a tool is called incorrectly.

**Interfaces and feasibility.** Define stable JSON schemas for tool inputs and outputs, include an idempotency key for writes, and return user-safe error codes. This is highly feasible because it fits the existing API boundary; the main dependency is a Hermes adapter that registers the allowlisted tools.

**Security decision.** Do not enable general terminal, filesystem, or arbitrary database tools for the production BeeRoom conversation. Keep business tools narrowly scoped, log tool names and request IDs rather than raw student content, and require confirmation for every mutation.

Source: [Hermes Tools & Toolsets](https://hermes-agent.nousresearch.com/docs/user-guide/features/tools) and [Hermes feature overview](https://hermes-agent.nousresearch.com/docs/user-guide/features/overview).

### 2. Skills system

**Capability.** Hermes skills are on-demand knowledge and workflow documents. They are loaded when relevant instead of being placed into every prompt, and can encode repeatable procedures, domain rules, and tool usage.

**BeeRoom integration.** Provide a sanitized `beeroom-comment-workflow` skill for the Hermes agent. It should describe how to recognize an observation, map it to the two-table model, resolve aliases, ask for clarification, create a preview, and request confirmation. The skill should contain examples and validation rules, but no student roster, secret, local path, or provider credential.

**End-to-end flow.** A teacher message activates the skill → the skill selects the allowlisted BeeRoom tools → the API returns candidate students or a preview → Hermes follows the confirmation protocol → the API stores the pending comment. The skill improves consistency, while the API remains authoritative for validation.

**Interfaces and feasibility.** Version the skill with the public business contract and test it against representative ambiguous-name and duplicate-name cases. Keep the tool names and JSON fields aligned with `backend/app/schemas/`; no database change is required for the first version. This is feasible and is a low-risk way to keep natural-language behavior maintainable.

**Security decision.** Treat skills as instructions, not as a trust boundary. Never place credentials or real student data in a skill. The integration layer must reject tool calls that violate authorization, confirmation, class scope, or field constraints, even when the skill suggests them.

Source: [Hermes Skills System](https://hermes-agent.nousresearch.com/docs/user-guide/features/skills).

### 3. Persistent memory

**Capability.** Hermes keeps bounded, curated memory across sessions, with separate space for agent notes and user preferences. The documentation also warns that memory is scoped to an agent profile and should not be shared casually by multiple agent processes.

**BeeRoom integration.** Use memory only for low-risk teacher preferences: a default class, preferred language, preferred comment tone, or whether previews should include evidence. Do not use it as the source of truth for student identity, safeguarding information, grades, or comment history; those belong behind the BeeRoom API.

**End-to-end flow.** Teacher sets a preference → Hermes stores a minimal preference entry → later message is interpreted with that preference → the integration layer still sends explicit class and student identifiers to the API → the API applies authorization and business validation. A preference must never silently select among two students with the same name.

**Interfaces and feasibility.** Add a profile-scoped preference adapter with `get_preferences` and `update_preferences`, or start with Hermes-managed memory and keep the BeeRoom API stateless. The first option is feasible for a single teacher; a multi-teacher deployment should move shared preferences into an authenticated service with tenant isolation.

**Security decision.** Apply data minimization, retention limits, and an exclusion list for sensitive student data. Provide a reset path and show the teacher when a stored preference affects a preview. Memory failures should degrade to an explicit question, not to a guessed class or student.

Source: [Hermes Persistent Memory](https://hermes-agent.nousresearch.com/docs/user-guide/features/memory).

### 4. Context files

**Capability.** Hermes discovers project context files and uses them to shape behavior, including project instructions, conventions, architecture notes, and personality guidance. The discovery and priority rules make repository-level instructions reusable across sessions.

**BeeRoom integration.** Maintain a sanitized project context document that describes the BeeRoom domain vocabulary, two-table model, API boundary, review states, confirmation rules, and examples of safe responses. This gives Hermes a stable contract for natural-language orchestration without embedding operational configuration in the public code snapshot.

**End-to-end flow.** Hermes loads the project context at session start → teacher sends an observation → the agent applies the domain rules → selected tools perform lookup and preview → BeeRoom validates and persists the result. When the contract changes, update the context document and the API schemas together.

**Interfaces and feasibility.** Add a versioned context contract beside the business documentation and test it with the same sample messages used by the API tests. Keep deployment-specific instructions in a private, untracked override rather than in the showcase repository. This is immediately feasible and does not require a schema change.

**Security decision.** Context files are prompt inputs, not access control. They must not contain credentials, private endpoints, local machine paths, real student records, or instructions that bypass API validation. A repository scan should run before publishing changes.

Source: [Hermes Context Files](https://hermes-agent.nousresearch.com/docs/user-guide/features/context-files).

## Showcase scope

This repository explains the business problem, user flow, Hermes responsibilities, API boundary, two-table model, review workflow, and privacy principles.

It intentionally does not provide production credentials, real service endpoints, deployment scripts, database snapshots, or an unrestricted natural-language-to-SQL executor.

## Disclaimer

This is architecture material for demonstration purposes, not a deployable production system. A real deployment requires separately managed authentication, access control, secret management, logging, backups, data retention, and privacy controls. Those operational details do not belong in this public repository.
