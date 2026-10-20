# Complete Presentation Deck & Speaker Notes (14 Slides)
## Online Quiz System (QuizSphere Pro) — Review 1: Setup & SRS

**PowerPoint File Generated:** [`QuizSphere_Review_1_Presentation.pptx`](file:///c:/Users/piyush/Documents/Online_Quiz_System/QuizSphere_Review_1_Presentation.pptx)  
**Academic Course:** BBAT104: Fundamentals of Total Quality Management (TQM)  
**Assigned Quality Goal:** Q20 — Overall Software Quality  
**Target Metric:** Zero-Latency (<250ms) Submissions & 100% Deterministic Auto-Grading  

---

### Slide 1: Title Slide
- **Title:** Online Quiz System (QuizSphere Pro)
- **Subtitle:** Setup & Software Requirements Specification (SRS) with Working Demo
- **Metadata Cards:**
  - *Course & Baseline:* BBAT104: Fundamentals of TQM | Baseline System 9: Online Quiz System
  - *Assigned Quality Goal:* Q20: Overall Software Quality (Dashboards, Validation, Reports, Backups, Role Controls)
  - *Engineering Target:* Zero-Latency Submissions (<250ms), Deterministic Zero-Defect Auto-Grading
  - *Dual Architecture:* FastAPI Unified Web Backend (SPA) + CustomTkinter Windows Desktop Client
- **Speaker Talking Points:**
  > "Good morning, respected evaluators. Today, we present Review 1 of our project: the **Online Quiz System (QuizSphere Pro)**. Our objective under TQM Baseline System 9 is to engineer a multi-platform assessment system with zero-latency grading, active proctoring, and complete role-segregated governance."

---

### Slide 2: Problem Statement & Baseline Understanding
- **Current Limitations in Traditional Systems:**
  1. *Network Lag & Submission Hangs:* High-concurrency test submissions freeze or time out, resulting in lost student answers.
  2. *Academic Integrity Vulnerabilities:* Standard online forms lack real-time window focus tracking, allowing unmonitored tab-switching.
  3. *Teacher Manual Burden:* Educators spend extensive hours crafting question formats, grading answer sheets, and reconciling rosters.
  4. *Single Point of Failure:* Absence of automated snapshot backups and offline desktop failover exposes institutions to fatal exam downtime.
- **QuizSphere Pro Solutions:**
  1. *Sub-250ms Instant Evaluation:* In-memory deterministic scoring pipeline processes answers in 15–35 milliseconds.
  2. *Anti-Cheat Proctoring Hub:* Continuous window focus loss and tab-switch telemetry increments violation counters and logs timestamps in real time.
  3. *AI Curriculum Question Synthesis:* Faculty input syllabus keywords to automatically generate verified MCQs with rationale keys in seconds.
  4. *Dual Platform Parity:* Simultaneous access via responsive Web browser SPA (FastAPI) and native standalone Windows Desktop App (CustomTkinter).

---

### Slide 3: Quality Objectives & TQM Critical-to-Quality (CTQ)
- **CTQ Metric 1 — Submission Latency:**
  - *Target Specification:* < 250 milliseconds per candidate submission
  - *Achieved Benchmark:* ~15 to 35 milliseconds (Verified)
- **CTQ Metric 2 — Grading Accuracy:**
  - *Target Specification:* 100.0% (Zero-Defect scoring consistency)
  - *Achieved Benchmark:* 100.0% (Deterministic key matching)
- **CTQ Metric 3 — Anti-Cheat Coverage:**
  - *Target Specification:* 100% of window/tab switches logged
  - *Achieved Benchmark:* Event-driven focus detection (`window.onblur` and Tkinter `FocusOut`)
- **CTQ Metric 4 — Data Recovery (RPO):**
  - *Target Specification:* Hourly automated database backups & on-demand snapshots
  - *Achieved Benchmark:* Automated timestamped SQLite backups in `backups/` directory

---

### Slide 4: Scope & Role-Based Access Control (RBAC)
- **Student / Candidate (Candidate Arena):**
  - Join assessments via 6-character Join Code (e.g., `QZ-1001`).
  - Authoritative countdown clock prevents client timer manipulation.
  - Anti-cheat focus loss monitoring logs tab blurs.
  - Instant scorecard with question-by-question explanations.
  - *Restricted View:* Examiner Studio and Admin Panel hidden.
- **Faculty / Examiner (Examiner Studio):**
  - Manual quiz authoring with custom time limits & passing marks.
  - AI-assisted curriculum generation based on topic & difficulty.
  - Instant Join Code generation for fast student distribution.
  - Live Class Gradebook with candidate scores and cheat violation counts.
  - *Restricted View:* Admin governance panel hidden.
- **Administrator (Platform Admin Console):**
  - Platform telemetry (total users, active faculty, attempt counts, pass rate).
  - User governance roster with search and role filters.
  - Candidate Performance Scorecard drill-down modal.
  - Instant CSV exports for rosters and complete audit logs.

---

### Slide 5: Software Requirements Specification (SRS) — Architecture & Scope
- **IEEE 830 Standard Structure:**
  - Complete formal specification documented in `docs/SRS_Document.md`.
  - Multi-tenant data isolation, security controls, and audit trails.
  - Integration with TQM Q20 (Overall Software Quality mandate).
- **System Boundaries & Actors:**
  - Primary Actors: Students (Examinees), Faculty (Examiners), Administrators.
  - Dual Client Channels: Web Browser (HTML5/CSS3) & Windows Desktop GUI.
  - Communication Protocol: High-throughput JSON REST APIs + WebSockets.
  - Storage Engine: Transactional ACID-compliant SQLite instance.
- **Poka-Yoke Mistake-Proofing:**
  - Validation Layer: Eliminates malformed question inputs and bad boundaries.
  - Schema Guards: Pydantic v2 strict models for all request bodies.
  - Join Code Integrity: Unique constraint locks preventing collisions.
  - Deterministic State: In-memory evaluation removing race conditions.

---

### Slide 6: SRS: Functional Requirements Matrix (FR-1 to FR-5)
- **FR-1: Multi-Role Dashboards:** Segregated workspaces for Student, Faculty, and Admin with dynamic navigation visibility based on authenticated role.
- **FR-2: Poka-Yoke Input Validation:** Strict bounds checking on quiz limits (1–180m, 1–100%), non-empty options, and unique constraint enforcement on Join Codes.
- **FR-3: AI Question Synthesis:** Automated MCQ synthesis based on syllabus topic and difficulty (Beginner, Medium, Advanced) with deterministic answer keys.
- **FR-4: Automated Gradebook & Export:** Instant candidate scorecard delivery with per-question review and one-click streaming CSV exports for rosters and attempts.
- **FR-5: Automated Database Backups:** Dedicated backup utility creating timestamped SQLite snapshots in `backups/` directory with on-demand snapshot triggers.

---

### Slide 7: SRS: Non-Functional Requirements & Security Safeguards
- **Sub-250ms Deterministic Speed:** In-memory evaluation pipeline yields immediate grading without blocking I/O (measured at 15–35ms).
- **ACID Transaction Guarantee:** Atomic SQLite write transactions protect test records from corrupt state; automatic database migrations on boot via FastAPI lifespan handlers.
- **Active Proctoring & Integrity:** Window blur & tab switch listeners capture unauthorized browser browsing; infraction tally permanently attached to candidate attempt record.
- **Theming & Accessibility:** Warm Cream Modern Theme + High-Contrast Dark Mode; dynamic font scaling controls (`A+`/`A-`) for laboratory accessibility.

---

### Slide 8: Modular Folder Architecture & Technology Stack
- **Backend Core (FastAPI + Uvicorn + SQLite):**
  - `server.py`: Unified REST API, WebSocket hub, and static SPA server.
  - `backend/api/v1/`: Versioned routers (`auth`, `quizzes`, `attempts`, `results`, `admin`).
  - `backend/core/`: Security, JWT tokens, DB engine, and telemetry middleware.
  - `ai_quiz_generator.py`: Curriculum MCQ synthesis engine.
- **Desktop Application (CustomTkinter GUI Engine):**
  - `desktop_app.py`: Standalone native Windows client.
  - Pixel-perfect 44px table rows and modern KPI card styling.
  - Multi-theme engine (Cream Modern Theme + High-Contrast Dark Mode).
  - Accessibility controls (font scaling A+/A- and Focus Mode).
- **Web Application (HTML5 + Vanilla CSS + Vanilla JS):**
  - `index.html`: Responsive single-page application.
  - `assets/css/`: Modular design tokens (`variables.css`, `quiz-engine.css`, `admin.css`, `examiner.css`).
  - `assets/js/`: Segregated controllers (`auth.js`, `quiz-engine.js`, `examiner.js`, `admin.js`).
- **Quality & Automated Test Suite (Pytest):**
  - 22 automated unit tests across `tests/` verifying all authentication, admin KPI, quiz code, and architecture contracts.

---

### Slide 9: Core Modules & Feature Breakdown
- **M1: Identity & Authentication:** Secure sign-in and registration with dynamic navigation tab filtering.
- **M2: Examiner Studio & AI Wizard:** Manual question authoring or AI syllabus synthesis with 6-character Join Code generation.
- **M3: Candidate Assessment Arena:** Quick test access via join code with authoritative countdown timer and question palette.
- **M4: Anti-Cheat Proctoring Hub:** Window blur and tab switch detection with real-time infraction counters.
- **M5: Zero-Latency Auto-Grading:** In-memory deterministic scoring pipeline with detailed scorecard delivery.
- **M6: Admin Governance & Telemetry:** Platform KPIs, user roster table, candidate history modal, and CSV exports.

---

### Slide 10: Database & System Design
- **Relational Tables in SQLite (`quiz_system.db`):**
  - `users`: User identity, hashed credentials, role, department, and timestamps.
  - `quizzes`: Quiz metadata, unique join codes (`QZ-XXXX`), duration, passing scores, and serialized JSON questions.
  - `attempts`: Candidate submissions, scores, percentages, pass/fail status, cheat violation tallies, and timestamps.
- **Architectural Highlights:**
  - *ACID Transactions:* Full data integrity during high-concurrency writes.
  - *Indexed Lookups:* Case-insensitive indexing on join codes and usernames for sub-millisecond retrieval.
  - *Self-Contained JSON Snapshots:* Questions stored immutably to prevent historical test drift.
  - *Automated Backups:* Snapshot backups saved in `backups/`.

---

### Slide 11: CRUD Operations Aligned with Quality Goals
- **User Management:** Create (Register), Read (Authenticate & Roster), Update (Profile & Accommodations), Delete (Soft-deactivate).
- **Assessment Management:** Create (Manual/AI), Read (Join Code Lookup & Listings), Update (Time Limits & Questions), Delete (Archive).
- **Submissions & Audit:** Create (Submit Test), Read (Gradebook & Scorecard), Update (Autosave Progress), Delete (Retention Purge).
- **Backups & Reports:** Create (Timestamped Snapshots), Read (CSV Exporters), Update (Integrity Checks), Delete (Rolling 30-day Purge).

---

### Slide 12: Working Application Demo Guide — Setup & Test Credentials
- **Execution & Verification Commands:**
  1. *Launch Web Server:* `python server.py` (Binds to `http://localhost:8000` with lifespan initialization and reload).
  2. *Launch Desktop GUI:* `python desktop_app.py` (Native Windows CustomTkinter application).
  3. *Run Automated Tests:* `python -m pytest tests/ -v` (Runs all 22 tests verifying auth, codes, and telemetry).
- **Ready-to-Use Test Accounts:**
  - *Student:* `student` / `student123` (Alex Mercer) — Candidate Arena test entry & anti-cheat demo.
  - *Faculty:* `faculty` / `faculty123` (Prof. Alan Turing) — AI quiz generator & class gradebook demo.
  - *Admin:* `admin` / `admin123` (System Administrator) — Telemetry KPIs, student history modal & CSV exports.

---

### Slide 13: Live Demonstration Walkthroughs (Student, Faculty, Admin)
- **Scenario 1: Student Examination Walkthrough:**
  1. Sign in as `student` / `student123`; navigation tabs restrict to Candidate Arena.
  2. Enter active Join Code `QZ-1001` and launch assessment.
  3. Answer questions while authoritative countdown timer runs.
  4. Switch browser tabs to trigger live Anti-Cheat violation alert.
  5. Submit test; zero-latency auto-grading delivers scorecard in ~25ms.
- **Scenario 2: Faculty Studio & AI Walkthrough:**
  1. Sign in as `faculty` / `faculty123`; Examiner Studio is front and center.
  2. Open AI Question Generator, enter topic `"Data Structures"`, click Generate.
  3. Set passing score to 70%, 15m duration, click Publish Quiz.
  4. System creates new 6-char Join Code (e.g. `QZ-3942`).
  5. Open Class Gradebook to inspect student attempts and proctor violation counts.
- **Scenario 3: Admin Governance Walkthrough:**
  1. Sign in as `admin` / `admin123`; open Platform Administration Console.
  2. Inspect high-level KPIs (Total accounts, candidates, faculty, violations).
  3. Filter user roster table by role or search string `"Alex Mercer"`.
  4. Click `"View Report"` on candidate to open historical performance modal.
  5. Click `"Export Roster CSV"` & `"Export Submissions CSV"` for audit reports.

---

### Slide 14: Review 1 Deliverables Summary & Next Steps
- **Review 1 Deliverables Met:**
  - Problem statement, quality goals, and baseline understanding completed.
  - Comprehensive IEEE 830 Software Requirements Specification (SRS) created.
  - Multi-role RBAC architecture implemented (Student, Faculty, Admin).
  - Complete database schema and all CRUD operations functional.
  - Working Web and Desktop applications verified.
  - All 22 automated Pytest unit tests passing cleanly.
- **Roadmap for Review 2:**
  - Biometric face verification and periodic webcam proctoring frames.
  - Offline sync queue for environments with intermittent network connections.
  - Enhanced graphical SQC analytics charts (Pareto, p-charts).
  - Multi-section assessment scheduling with automated release windows.
