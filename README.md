# Online Quiz System (QuizSphere Pro) — BBAT104 TQM Course Project

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![TQM Project](https://img.shields.io/badge/Course-BBAT104%20TQM-purple.svg)]()
[![Quality Goal](https://img.shields.io/badge/Assigned%20Goal-Q20%20Software%20Quality-success.svg)]()
[![System](https://img.shields.io/badge/Baseline%20System-9%20Online%20Quiz-cyan.svg)]()
[![ER Diagram](https://img.shields.io/badge/Schema-ER%20Diagram%20v2.0-emerald.svg)](docs/ER_DIAGRAM.md)

An integrated, multi-platform examination platform engineered in Python for **Windows Desktop** and **Android Mobile / Web**, designed in compliance with **Total Quality Management (TQM)** principles and **Statistical Quality Control (SQC)** audits.

---

## 📌 Academic Project Allotment Details

* **Course Code & Title:** BBAT104: Fundamentals of TQM
* **Academic Session:** 2026–27 | Max Assessment: 70 Raw Marks
* **Assigned Baseline System:** **Digit 9 — Online Quiz System**
* **Core TQM Mandate:** *Ensure zero latency during submissions & auto-grading*
* **Assigned Quality Goal (Q01–Q20):** **Q20 — Overall Software Quality**
* **Implemented Q20 Features:**
  1. **Multi-Role Dashboards:** Administrator, Teacher/Faculty, and Student/Candidate workspaces.
  2. **Poka-Yoke Input Validation:** Form masking, required options checks, bounds validation.
  3. **Export Reports:** Automated CSV gradebook exports and printable achievement scorecards.
  4. **Automated Database Backups:** Automated SQLite snapshots in `backups/`.
  5. **Role Controls & Anti-Cheat:** Role-based access control (RBAC) and OS window focus tracking.

---

## 🗄️ Entity-Relationship (ER) Architecture

The database architecture is designed with strict multi-tenancy, server-authoritative deadlines, immutable quiz snapshots, monotonic answer revisions, and comprehensive forensic audit logging.

### 🖼️ High-Resolution Architecture Diagram
![QuizSphere Pro Entity-Relationship Diagram](./docs/assets/er_diagram.png)

### 📊 Interactive Mermaid ER Diagram
GitHub renders the interactive schema diagram below natively:

```mermaid
erDiagram
    TENANT ||--o{ PLATFORM_USER : "provisions (1:N)"
    TENANT ||--o{ QUIZ_V2 : "owns (1:N)"
    TENANT ||--o{ ATTEMPT_V2 : "scopes (1:N)"
    TENANT ||--o{ AUDIT_EVENT_V2 : "logs (1:N)"

    PLATFORM_USER ||--o{ ATTEMPT_V2 : "submits (1:N)"
    PLATFORM_USER ||--o{ GRADE_APPEAL_V2 : "files (1:N)"

    QUIZ_V2 ||--|{ QUIZ_VERSION : "freezes into (1:N)"
    QUIZ_V2 ||--o{ ATTEMPT_V2 : "instantiates (1:N)"

    QUIZ_VERSION ||--o{ ATTEMPT_V2 : "locks snapshot (1:N)"

    ATTEMPT_V2 ||--o{ ATTEMPT_ANSWER_V2 : "records (1:N)"
    ATTEMPT_V2 ||--|| GRADE_V2 : "produces (1:1)"

    GRADE_V2 ||--o{ GRADE_FEEDBACK_V2 : "provides (1:N)"
    GRADE_V2 ||--o{ GRADE_APPEAL_V2 : "receives (1:N)"

    CORE_QUIZ ||--o{ CORE_ATTEMPT : "records (1:N)"
    CORE_USER ||--o{ CORE_ATTEMPT : "attempts (1:N)"

    TENANT {
        string id PK "Unique tenant ID (ten-xxx)"
        string name "Organization or School name"
        string domain "Optional custom domain"
        string settings_json "Tenant policy configuration"
        datetime created_at "Registration timestamp"
    }

    PLATFORM_USER {
        string id PK "Unique user ID (usr-xxx)"
        string tenant_id FK "References tenants.id"
        string username "Unique login username"
        string email "User email address"
        string hashed_password "PBKDF2/Argon2 password hash"
        string full_name "Full legal display name"
        string role "learner | instructor | grader | admin"
        string department "Academic department"
        boolean is_active "Account status flag"
        int extra_time_percent "Time accommodation (+%)"
        datetime created_at "Account creation date"
    }

    QUIZ_V2 {
        string id PK "Unique quiz ID (qz-xxx)"
        string tenant_id FK "References tenants.id"
        string title "Assessment title"
        string category "Domain / subject category"
        string join_code "Unique 6-char join pin"
        string teacher_name "Faculty author name"
        int duration_minutes "Allotted exam duration"
        int passing_score "Passing threshold percentage"
        string status "draft | published | archived"
        string current_version_id "Latest active snapshot"
        datetime created_at "Creation timestamp"
    }

    QUIZ_VERSION {
        string id PK "Unique version ID (qv-xxx)"
        string quiz_id FK "References quizzes_v2.id"
        int version_number "Monotonic version counter"
        string snapshot_json "Immutable frozen questions & keys"
        string published_by_id "Authorizing instructor ID"
        datetime published_at "Publication timestamp"
    }

    ATTEMPT_V2 {
        string id PK "Unique attempt ID (att-xxx)"
        string tenant_id FK "References tenants.id"
        string quiz_id FK "References quizzes_v2.id"
        string quiz_version_id FK "References quiz_versions.id"
        string learner_id FK "References platform_users.id"
        string learner_name "Candidate display name"
        string state "in_progress | submitted | evaluated"
        datetime started_at "Candidate start timestamp"
        datetime deadline_at "Server-authoritative deadline"
        datetime submitted_at "Final submission timestamp"
        int form_seed "Deterministic shuffling seed"
        int cheat_violations "Tab-switch / blur counter"
        string idempotency_key "Unique client submission token"
    }

    ATTEMPT_ANSWER_V2 {
        string id PK "Unique answer record (ans-xxx)"
        string attempt_id FK "References attempts_v2.id"
        string item_id "Question ID in version snapshot"
        string answer_payload_json "Selected option payload"
        int revision "Monotonic revision counter"
        string idempotency_key "Autosave idempotency key"
        datetime saved_at "Server committed timestamp"
    }

    GRADE_V2 {
        string id PK "Unique grade ID (grd-xxx)"
        string attempt_id FK "References attempts_v2.id (1:1)"
        float score "Raw score obtained"
        float total_points "Maximum attainable marks"
        float percentage "Calculated percentage"
        boolean passed "Pass or fail decision"
        string grading_policy_ver "Scoring engine version"
        string status "provisional | released | under_appeal"
        datetime released_at "Grade publication date"
        datetime created_at "Calculation timestamp"
    }

    GRADE_FEEDBACK_V2 {
        string id PK "Unique feedback ID (fb-xxx)"
        string grade_id FK "References grades_v2.id"
        string feedback_text "Instructor or auto note"
        string item_breakdown_json "Question-by-question scoring"
        datetime created_at "Creation timestamp"
    }

    GRADE_APPEAL_V2 {
        string id PK "Unique appeal ID (apl-xxx)"
        string grade_id FK "References grades_v2.id"
        string learner_id "Appealing student user ID"
        string reason "Student justification text"
        string status "pending | approved | rejected"
        string reviewer_notes "Faculty review remarks"
        datetime resolved_at "Resolution timestamp"
    }

    AUDIT_EVENT_V2 {
        string id PK "Unique audit event (aud-xxx)"
        string tenant_id "Tenant scope boundary"
        string actor_id "User performing action"
        string actor_name "Display name of actor"
        string action "ATTEMPT_START | SUBMIT | GRADE"
        string target_resource "Resource affected"
        string request_id "Correlated request UUID"
        string payload_json "Audit metadata payload"
        datetime timestamp "Immutable event timestamp"
    }

    OUTBOX_EVENT_V2 {
        string id PK "Unique outbox event (obx-xxx)"
        string event_type "ATTEMPT_SUBMITTED | GRADE_DONE"
        string aggregate_type "Attempt | Grade | Quiz"
        string aggregate_id "Target entity ID"
        string payload_json "Serialized message payload"
        string status "pending | processed | dead_letter"
        string retry_count "Delivery attempt counter"
        datetime created_at "Enqueued timestamp"
    }

    CORE_USER {
        string id PK "User ID"
        string username "Unique login username"
        string password "Hashed credentials"
        string role "Admin | Teacher | Student"
        string full_name "User full name"
        string department "Department"
        datetime created_at "Creation date"
    }

    CORE_QUIZ {
        string id PK "Quiz ID"
        string title "Quiz title"
        string category "Topic category"
        string join_code "Unique access code"
        string teacher_name "Authoring faculty"
        int duration_minutes "Time limit"
        int passing_score "Passing percentage"
        string questions_json "Serialized questions array"
    }

    CORE_ATTEMPT {
        string id PK "Attempt ID"
        string quiz_id FK "References quizzes.id"
        string candidate_name "Student name"
        int score "Raw score"
        int total_questions "Total questions"
        int percentage "Score percentage"
        int passed "Binary 1 or 0 flag"
        int cheat_violations "Window switch count"
        datetime submitted_at "Submission date"
    }
```

> 📖 **Full Data Dictionary:** For column-by-column descriptions, foreign key constraints, indexes, and ACID guarantees, refer to [`docs/ER_DIAGRAM.md`](docs/ER_DIAGRAM.md).

---

## 📁 Repository Structure & TQM Documentation Suite

```text
Online_Quiz_System/
├── docs/
│   ├── ER_DIAGRAM.md             # Complete Entity-Relationship & Data Dictionary (CO1/CO2)
│   ├── SRS_Document.md           # Master Software Requirements Specification
│   ├── SRS.md                    # Software Requirements Specification (CO1)
│   ├── SIPOC_AND_CTQ.md          # SIPOC Process Map & Critical-to-Quality Tree (CO2)
│   ├── FMEA_MATRIX.md            # Failure Mode & Effects Analysis with RPN (CO2)
│   ├── PDCA_CYCLE.md             # Plan-Do-Check-Act Continuous Improvement Log (CO3)
│   ├── USER_MANUAL.md            # Step-by-Step User Manual for all 3 roles (CO3)
│   └── assets/                   # High-Resolution Architectural Assets (ER Diagram)
├── sqc_charts/                   # Generated Statistical Quality Control Charts
│   ├── pareto_analysis.png       # 80/20 Pareto Chart (Matplotlib)
│   └── ishikawa_fishbone.png     # Ishikawa (Fishbone) Root Cause Diagram
├── backups/                      # Automated SQLite Database Snapshots
├── reports/                      # Exported Class Gradebooks (CSV)
├── desktop_app.py                # Native Python Desktop Application (CustomTkinter)
├── server.py                     # Python FastAPI Backend & WebSocket Server
├── ai_quiz_generator.py          # AI Question Synthesizer Module
├── tqm_sqc_tools.py              # Automated SQC Chart & Backup Generator Script
├── DEMO_GUIDE.md                 # End-to-End Live Demonstration Walkthrough
├── QuizSphere_Review_Presentation.pptx # Compact 17-Slide Presentation Deck
├── Review_1_PPT_Deck.md          # Slide-by-Slide Speaker Notes & Viva Guide
├── index.html                    # Mobile/Web PWA Assessment Client
├── requirements.txt              # Core Python Dependencies
├── ARCHITECTURE.md               # Technical System Architecture Specification
└── README.md                     # Project Hub & Guidelines Mapping
```

---

## 🚀 Quick Start Guide

### 1. Installation
Clone the repository and install core dependencies:
```powershell
git clone https://github.com/Vanshika071417/Online_Quiz_System.git
cd Online_Quiz_System
pip install -r requirements.txt
```

### 2. Launching the Desktop Application (Primary)
```powershell
python desktop_app.py
```
> Select between **Student**, **Teacher**, and **Administrator** directly using the top-left sidebar menu.

### 3. Launching the Backend Server (Mobile / Android)
```powershell
python server.py
```
> Runs the FastAPI server on `http://localhost:8000`. Mobile users on the same network can access `http://<HOST_IP>:8000` from their Android devices.

### 4. Running TQM SQC Tools & Database Backup
```powershell
python tqm_sqc_tools.py
```
> Generates updated Pareto Charts, Fishbone Diagrams, and timestamped database backups.

---

## 📊 TQM Statistical Quality Control (SQC) Artefacts

### 1. Pareto Analysis (80/20 Rule)
* Located at: [`sqc_charts/pareto_analysis.png`](./sqc_charts/pareto_analysis.png)
* Isolates the vital 20% of causes driving 80% of student exam friction (window focus switches and join code typos).

### 2. Ishikawa (Fishbone) Diagram
* Located at: [`sqc_charts/ishikawa_fishbone.png`](./sqc_charts/ishikawa_fishbone.png)
* Maps root causes across **People**, **Process**, **Software Code**, and **Infrastructure**.

### 3. FMEA Risk Audit & RPN Reduction
* Located at: [`docs/FMEA_MATRIX.md`](./docs/FMEA_MATRIX.md)
* Critical failure modes audited with severity, occurrence, and detection ratings. Mitigations achieved an average **> 85% RPN reduction**.

---

## 🛡️ Key Features Checklist (Review Deliverables Mapped)

- [x] **Review 1 (Setup & SRS):** GitHub repository linked, architecture diagrams, complete ER diagram, comprehensive `docs/SRS.md`.
- [x] **Review 2 (Base System & CRUD):** Full CRUD for Quizzes, Questions, and Submissions; 5 features for Goal Q20.
- [x] **Review 3 (FMEA & Risk Audit):** SIPOC Process Map, CTQ Tree, and FMEA Matrix with calculated RPN.
- [x] **Review 4 (SQC & Continuous Improvement):** Python Pareto Analysis, Fishbone Diagram, Checksheets, and PDCA Cycle log.
- [x] **Presentation & Viva Defense:** 17-slide high-impact presentation deck ([`QuizSphere_Review_Presentation.pptx`](QuizSphere_Review_Presentation.pptx)) and speaker notes.
- [x] **Documentation & GitHub Health:** Comprehensive User Manual, organized codebase, and meaningful commit history.
