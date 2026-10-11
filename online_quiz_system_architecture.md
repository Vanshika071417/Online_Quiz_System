# Online Quiz System Architecture

## A Python first design for secure assessment at production scale

**Reference design | 11 October 2026**

This design covers a complete assessment platform for learners, instructors, organizations, and administrators. Start with a modular Python application backed by PostgreSQL, Redis, object storage, and background workers; split capabilities only when measured load, ownership, or reliability needs justify it. Every attempt must be durable, time bounded, auditable, and recoverable after ordinary network or process failures.

## Executive decisions

| Area | Recommendation |
|---|---|
| Application shape | Modular monolith with explicit domain boundaries first. |
| Python stack | FastAPI, Pydantic, SQLAlchemy 2, Alembic, pytest, OpenTelemetry. |
| Data | PostgreSQL is authoritative; Redis accelerates but never stores irreplaceable answers. |
| Assessment integrity | Server authoritative deadline, durable idempotent answer writes, immutable quiz snapshots. |
| Operations | Managed database, cache, object store and queue; stateless containers; recovery rehearsed. |

## 1. Product scope and quality goals

Support public and private quizzes, practice and graded modes, scheduled exams, question banks, randomized forms, accommodations, autosaved attempts, manual review, result release, cohort reporting, and administrative oversight. A tenant may be a school, company, or instructor; enforce tenant scope on every access path.

| Goal | Design response |
|---|---|
| Correctness | Never acknowledge an answer before durable commit; make retries idempotent. |
| Fairness | Deadline and policy are server owned; extensions are explicit and audited. |
| Availability | Resume in progress attempts after browser, network, API, or worker failure. |
| Privacy | Minimize collected data; define retention, export, deletion, and access rules. |
| Accessibility | Keyboard and screen reader support, contrast, alternative media, extra time settings. |
| Scale | Horizontal API replicas; independently scaled workers; isolate analytics from attempts. |

## 2. Architecture overview

The diagram describes logical boundaries, not mandatory deployment units. FastAPI domain modules may share one codebase and deployment initially; move slow or retryable work to durable workers.

See the editable [Mermaid architecture diagram](quiz_system_architecture.mmd).

### Layers and responsibilities

| Layer | Responsibilities |
|---|---|
| Client | React/Next.js learner, author, and admin applications; typed API client; clear pending, saved, and error states. |
| Edge | CDN, WAF, TLS, ingress, request limits and routing; never a substitute for authorization. |
| API | Versioned REST endpoints, Pydantic validation, auth dependencies, request IDs, idempotency, OpenAPI. |
| Identity and tenancy | Users, memberships, roles, MFA/SSO, invitations, tenant settings and access policies. |
| Authoring and catalog | Question bank, drafts, versioned immutable quiz publication, schedule, enrollment, accommodations. |
| Attempts | Eligibility, attempt state, deadline, answer upserts, autosave receipts, resume, submit and timeout. |
| Grading and results | Objective and rubric grading, moderation, appeals, grade history, feedback and release policy. |
| Admin and analytics | Support tools, audit search, tenant controls, operational dashboards, cohort reports and exports. |
| Workers | Notifications, exports, media processing and deferred work; retries, dead letters, delivery metrics. |

### Accessible and adaptable interface

Make these display and navigation options available throughout the learner, author, and admin interfaces. They are client preferences and must not change quiz content, scoring, timing, or saved answers.

| Feature | Behavior |
|---|---|
| High contrast | Offer a high contrast theme with strong text/control contrast, visible boundaries, and status indicators that do not depend on color alone. |
| Font resizing | Provide an in-app text size control and preserve browser zoom/reflow. Layouts must remain usable at 200% text size without clipping or hiding controls. |
| Keyboard navigation | Make all actions operable without a pointer. Use logical tab order, visible focus, skip links, keyboard-operable question controls, and predictable focus after dialogs and navigation. |
| Dark mode | Offer light, dark, and system preference modes. Keep contrast and focus indicators legible in every theme; avoid flashes when restoring a saved preference. |
| Minimalist layout | Provide a distraction-reduced view that hides optional navigation and decorative content while keeping instructions, progress, timer, save status, and required controls available. |

Store preferences per user when signed in, with a local browser fallback for signed-out use. Apply them consistently across pages and devices where possible. Use semantic HTML, accessible labels, screen-reader announcements for save status and validation errors, and reduced-motion preferences. Validate with automated accessibility checks plus keyboard-only and screen-reader task reviews; automated checks alone are not sufficient.

## 3. Recommended Python stack

| Concern | Recommendation |
|---|---|
| API | FastAPI + Pydantic v2; typed schemas and OpenAPI. |
| Database | PostgreSQL + SQLAlchemy 2 + Alembic; reviewed migrations and explicit transactions. |
| Jobs | Celery + RabbitMQ for durable queues, or a simpler Redis backed worker for early low risk jobs. |
| Authentication | OIDC identity provider; short lived access tokens, MFA for privileged users, refresh rotation. |
| Observability | OpenTelemetry traces and metrics, structured logs, error tracking, correlation IDs. |
| Quality | pytest, Ruff, mypy/pyright, contract tests, integration and load tests. |

Keep HTTP handlers thin and business invariants in domain services. Prefer simple synchronous transactional database operations for attempt writes; use async I/O selectively where profiling and team experience support it.

## 4. Data model and persistence

PostgreSQL owns durable state. Use UUID like public IDs, UTC timestamps, foreign keys, `tenant_id`, uniqueness constraints, and indexes aligned to measured query patterns.

| Entity | Important fields and rules |
|---|---|
| Tenant, User, Membership | Organization scope; users may join multiple tenants; membership role and status. |
| Quiz, QuizVersion | Draft and published versions; duration, windows, policy, randomization. Published snapshot is immutable. |
| Question, QuestionVersion | Type, prompt, choices, rubric, tags, media reference, points. Versioning preserves old attempts. |
| Attempt | Learner, quiz version, state, `started_at`, `deadline_at`, `submitted_at`, accommodation snapshot and form seed. |
| AttemptItem, Answer | Stable item order; validated payload, revision, `saved_at`, client sequence and grading state. |
| Grade, Feedback | Earned points, policy version, grader, moderation and publication history. |
| AuditEvent, OutboxEvent | Actor, action, target, timestamp, request ID. Commit outbox with domain change before delivery. |

- Validate type specific JSON answer payloads server side and cap their size. Store media bytes in object storage and metadata in PostgreSQL.
- Use optimistic concurrency or monotonic answer revisions to identify stale writes; return accepted revision and server save time.
- Partition event heavy tables, add replicas, or export to a warehouse only when growth and query contention justify it.
- Define retention, deletion, export, backup, restore, and legal hold behavior at the data model stage.

## 5. Authentication, authorization and roles

Use an OIDC provider for login and federation where practical. Enforce authorization on every API operation with role plus resource scope; a role alone does not grant access to every tenant resource. Apply deny by default checks and tenant filters in application queries; PostgreSQL row level security can add defense in depth if pooled tenant context is handled carefully.

| Role | Typical permissions |
|---|---|
| Learner | Assigned quizzes, eligible start/resume, save, submit, released results. |
| Instructor / author | Drafts, question bank, schedule, authorized cohorts, grading and release. |
| Grader / reviewer | Assigned submissions and rubrics; no quiz policy changes without a separate grant. |
| Tenant admin | Members, roles, SSO/settings, tenant reports, retention controls. |
| Platform support | Just in time break glass access, reason capture, narrow scope and immutable audit. |

Require MFA for privileged roles, support SSO where needed, rotate/revoke refresh tokens, and never return answer keys or hidden scoring fields before release.

## 6. Quiz authoring and delivery

1. Author in draft and preview; validate completeness, accessibility, schedule, and scoring rules before publication.
2. Publish an immutable version snapshot. Editing creates a new version so active and completed attempts remain reproducible.
3. Build each form from explicit rules: fixed items, random pools, shuffled choices and a deterministic per attempt seed. Persist the seed and rendered order.
4. Check enrollment, attempt limits, availability, accommodations and prerequisites before creating an attempt.
5. Return learner safe question shapes only; question types may include choice, true/false, short answer, numeric, matching, ordering, file response and essay.

Use a versioned question type registry so each type owns its rendering schema, answer validation, auto grading behavior, and review requirements. Treat uploaded media as untrusted content and scan before serving.

## 7. Timed attempts, autosave and recovery

Create the attempt and deadline in one database transaction. The server calculates `deadline_at` using a trusted clock and policy, including approved accommodations. Browser countdown is display only. Every save and submit checks server time and valid state transitions.

| Action | Reliable behavior |
|---|---|
| Start / resume | Idempotent start returns existing in progress attempt when allowed; resume hydrates deadline from server. |
| Autosave | Debounce local changes; upsert with attempt/item IDs, revision and idempotency key; acknowledge only after commit. |
| Concurrent tabs | Detect revision conflicts and surface them; do not silently overwrite newer answers. |
| Network loss | Keep unsent changes locally for recovery, retry with bounded backoff, show warning. Local state is not authoritative. |
| Submit | Idempotently finalize once, set submission boundary and publish an outbox event in the same transaction. |
| Timeout | Enforce deadline during requests; scheduled worker is cleanup/notification fallback, never the only enforcement. |

Use a short autosave debounce and periodic reconciliation appropriate to expected load. Never trust client provided score or time. A transactional outbox prevents committed submissions from losing downstream grading or notification work.

## 8. Grading, results and appeals

- Auto grade deterministic items with explainable per item outcomes and the exact grading policy version. Manual grading uses rubrics, assignments, moderation and audit history.
- Separate score calculation from publication; release score, feedback, and answer key on configurable schedules.
- Use integer or decimal points with explicit rounding; retain raw points and policy version. Regrading creates a new revision with actor, reason, and impact history.
- Provide configurable review and appeal windows with status, reviewer, resolution and communications history.

## 9. Analytics, admin and notifications

Operational dashboards should cover starts, completion, save failures, timeouts, queue age, grading backlog and provider errors. Instructor reports can show participation, score distributions, item difficulty, distractors and completion time. Suppress or aggregate small sensitive cohorts. Start with indexed queries and pre aggregations; move historical analytics to a warehouse asynchronously so reports cannot block attempts.

Admin tools include members and roles, publication, moderation queues, support search, audit trail, export/deletion, feature flags and incident controls. Privileged actions require reason capture and audit; support elevation expires automatically.

Use an outbox backed worker for invitations, reminders, submission receipts, result release, and grading assignments. Make jobs idempotent, retry with backoff, dead letter failures, process bounces/suppressions, and avoid sensitive grade details in email previews.

## 10. Security and assessment integrity

- TLS in transit; encryption at rest for database, objects and backups; managed secrets and credential rotation.
- CSRF protection for cookie sessions, secure/HttpOnly/SameSite cookies, CSP, output encoding, input and upload validation, malware scanning, dependency and image scanning.
- Per user, tenant and IP rate limits for login, attempt creation, answer writes and exports. Keep bot controls proportionate to abuse risk.
- Use allowlisted learner API schemas to prevent answer key leakage. Redact tokens, passwords, and unnecessary answer content from logs.
- Audit security relevant actions with actor, target, timestamp and request ID. Provide access review, retention, backup and deletion processes.
- For high stakes exams, consider randomized forms, item pools, navigation rules, identity checks and optional proctoring only after privacy, legal and accessibility review.
- Treat focus loss, copy/paste, device changes and unusual timing as signals for human review, not proof. Do not claim a browser can prevent screenshots, external devices, collaboration or AI use; provide transparent policy and appeal paths.

## 11. Scalability, reliability and deployment

Deploy stateless API containers across availability zones behind a load balancer. Keep PostgreSQL managed with automated backups and point in time recovery; Redis may be managed but must not hold irreplaceable attempt data. Store media and exports in object storage behind signed URLs. Scale workers on queue depth and age, not CPU alone.

| Stage | Shape and exit criteria |
|---|---|
| MVP | One modular API, worker pool, managed PostgreSQL/Redis, object store, CDN/WAF, CI/CD and centralized telemetry. Prove expected pilot load and restore from backup. |
| Growth | Multiple stateless API replicas, workload specific worker queues, connection pooling, read replica, catalog cache, autoscaling on latency/saturation. Split modules only for independent scaling or ownership. |
| High stakes / large | Multi zone/failover plan, explicit tenant capacity, regional/residency design, warehouse, incident runbooks and tested recovery. Add based on agreed availability and recovery targets. |

Set SLOs for API availability, save latency and durability, submission completion and result publication. Define RPO/RTO with stakeholders, automate backups and rehearse restore. Use rolling/blue green deploys, backward compatible migrations and feature flags; do not invalidate active attempts or their quiz snapshots.

## 12. API shape and critical workflows

| Endpoint example | Contract |
|---|---|
| `POST /v1/quizzes/{id}/attempts` | Check eligibility; idempotently start/resume; return server deadline and learner safe form. |
| `PUT /v1/attempts/{id}/answers/{item_id}` | Enforce ownership, state, deadline, schema and size; idempotent upsert with revision. |
| `POST /v1/attempts/{id}/submit` | Idempotent finalization; freeze answer boundary and commit outbox event. |
| `GET /v1/attempts/{id}` | Authorized resume with server deadline and accepted answer revisions. |
| `GET /v1/results/{id}` | Return only released result under visibility policy. |
| `POST /v1/submissions/{id}/grade` | Role scoped rubric grading with revision checks, attribution and audit. |

Use consistent error envelopes, pagination, request IDs and concurrency responses. Version incompatible API changes. Idempotency is critical for start, submit, grade, publish and external integrations.

## 13. MVP to production roadmap

| Phase | Deliverables | Exit criteria |
|---|---|---|
| 0 Foundation | Policies, threat model, tenancy, accessibility, retention, API conventions, environments and CI. | Assessment rules, data ownership and risk boundaries agreed. |
| 1 MVP | OIDC, learner/instructor roles, authoring, immutable publish, objective types, timed attempts, durable autosave, objective grading, results, audit, email. | Pilot load works; acknowledged answers survive restart; access and recovery checks pass. |
| 2 Pilot hardening | Pools/randomization, accommodations, manual grading, exports, dashboards, alerts, restore drill, support tools, accessibility fixes, and high-contrast, font-size, keyboard, dark-mode, and minimalist display options. | Operators diagnose save issues, resume attempts, and release/review results; accessibility review covers every display mode and core workflow. |
| 3 Production scale | Autoscaling, worker isolation, SSO/MFA, read replicas or warehouse, lifecycle tooling, runbooks, load/soak and disaster recovery. | SLO and RPO/RTO met in rehearsals; capacity and on call owners named. |
| 4 Advanced assessment | Proctoring, item analysis, adaptive assessment, advanced accommodations, multi region. | Demand, privacy/accessibility review and measurable operating cost are established. |

## 14. Decisions to confirm before implementation

- Peak concurrent learners, attempt starts/writes per minute, quiz size and regions.
- Stakes and policies: navigation, retakes, late submissions, partial credit, randomization and result release.
- Tenant model, SSO, identity proofing and role delegation.
- Accessibility and accommodation needs, including time extensions and alternate formats.
- Privacy jurisdiction, retention, deletion/export and acceptable proctoring signals.
- Availability, recovery objectives, support coverage and incident ownership.

## Recommended first release

Build one modular FastAPI service with PostgreSQL as the durable record, Redis for acceleration and short lived coordination, object storage for media, and workers for notifications and exports. Deliver versioned quizzes, scoped access, server timed attempts, durable idempotent autosave and submission, objective grading, auditable manual grading foundations, and accessible result release. Include high contrast, adjustable text size, complete keyboard navigation, dark mode, and a minimalist learner view in the initial user interface. Prove recovery and concurrency behavior before expanding into proctoring or distributed services.
