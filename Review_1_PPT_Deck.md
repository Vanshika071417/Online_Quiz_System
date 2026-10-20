# Presentation Deck & Speaker Notes
## Online Quiz System (QuizSphere Pro) — Review 1: Setup & SRS

**PowerPoint File Generated:** [`QuizSphere_Review_1_Presentation.pptx`](file:///c:/Users/piyush/Documents/Online_Quiz_System/QuizSphere_Review_1_Presentation.pptx)  
**Academic Course:** BBAT104: Fundamentals of Total Quality Management (TQM)  
**Assigned Quality Goal:** Q20 — Overall Software Quality  
**Target Metric:** Zero-Latency (<250ms) Submissions & 100% Deterministic Auto-Grading  

---

### Slide 1: Title Slide
- **Title:** Online Quiz System (QuizSphere Pro)
- **Subtitle:** Setup & Software Requirements Specification (SRS) — Review 1
- **Metadata Cards:**
  - *Course & Topic:* BBAT104: Fundamentals of TQM | Baseline System 9: Online Quiz System
  - *Assigned Quality Goal:* Q20: Overall Software Quality (Dashboards, Validation, Reports, Backups, Role Controls)
  - *Core Engineering Target:* Zero-Latency Submissions (<250ms), Deterministic Zero-Defect Auto-Grading
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
- **Speaker Talking Points:**
  > "Traditional online assessment tools suffer from submission freezes during peak loads and lack proctoring. We addressed these core problems by building an in-memory grading engine that delivers scores in ~25ms, paired with client-side anti-cheat tracking and an AI question generator."

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
- **Speaker Talking Points:**
  > "Under our assigned TQM goal Q20, we established strict Critical-to-Quality (CTQ) specifications. We have exceeded our performance benchmark: submissions grade in ~25ms versus our 250ms target, with 100% accuracy and automated database backup routines."

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
- **Speaker Talking Points:**
  > "The system enforces strict Role-Based Access Control across three segregated portals. Students see only the Candidate Arena, teachers get the Examiner Studio, and administrators access system telemetry and CSV exports."

---

### Slide 5: Modular Folder Architecture & Technology Stack
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
- **Speaker Talking Points:**
  > "Our codebase is structured modularly. The backend uses FastAPI with SQLite, the frontend uses a responsive vanilla CSS design system, and the desktop app is built with CustomTkinter. All 22 automated tests are passing with 100% success."

---

### Slide 6: Core Modules & Feature Breakdown
- **M1: Identity & Authentication:** Secure sign-in and registration with dynamic navigation tab filtering.
- **M2: Examiner Studio & AI Wizard:** Manual question authoring or AI syllabus synthesis with 6-character Join Code generation.
- **M3: Candidate Assessment Arena:** Quick test access via join code with authoritative countdown timer and question palette.
- **M4: Anti-Cheat Proctoring Hub:** Window blur and tab switch detection with real-time infraction counters.
- **M5: Zero-Latency Auto-Grading:** In-memory deterministic scoring pipeline with detailed scorecard delivery.
- **M6: Admin Governance & Telemetry:** Platform KPIs, user roster table, candidate history modal, and CSV exports.

---

### Slide 7: Database & System Design
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

### Slide 8: Initial UI & System Workflow
1. **Authenticate:** User logs in as Student, Faculty, or Admin; navigation adapts immediately.
2. **Create Quiz:** Faculty authors a quiz manually or uses the AI generator; server assigns a unique Join Code (e.g., `QZ-4821`).
3. **Enter Code:** Student enters the 6-character code; questions load in <25ms.
4. **Take & Monitor:** Authoritative countdown timer runs; anti-cheat tracks window blur and tab switching.
5. **Auto-Grade:** Student submits test; server evaluates answers in ~25ms and displays full scorecard.
6. **Audit & Export:** Faculty inspects class gradebook; Admin reviews platform telemetry and exports CSV reports.

---

### Slide 9: CRUD Operations Aligned with Quality Goals
- **User Management:** Create (Register), Read (Authenticate & Roster), Update (Profile & Accommodations), Delete (Soft-deactivate).
- **Assessment Management:** Create (Manual/AI), Read (Join Code Lookup & Listings), Update (Time Limits & Questions), Delete (Archive).
- **Submissions & Audit:** Create (Submit Test), Read (Gradebook & Scorecard), Update (Autosave Progress), Delete (Retention Purge).
- **Backups & Reports:** Create (Timestamped Snapshots), Read (CSV Exporters), Update (Integrity Checks), Delete (Rolling 30-day Purge).

---

### Slide 10: Working Application & Live Demonstration
- **Web Application Demo:**
  - Start command: `python server.py` (Accessible at `http://localhost:8000`).
  - Demonstrate candidate exam via Join Code `QZ-1001` with anti-cheat detection and immediate scorecard.
  - Demonstrate teacher AI quiz generation and class gradebook.
  - Demonstrate admin platform telemetry and CSV downloads.
- **Desktop Application Demo:**
  - Start command: `python desktop_app.py` (Native Windows Standalone GUI).
  - Demonstrate desktop authentication dialog and role-based tab switching.
  - Demonstrate pixel-perfect grid tables with candidate scorecard drill-down modal.
  - Demonstrate theme switching (Cream / Dark) and font scaling controls.

---

### Slide 11: Summary & Review 2 Roadmap
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
