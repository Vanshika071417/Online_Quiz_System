# Master Presentation Deck & Speaker Notes (42 Slides)
## Online Quiz System (QuizSphere Pro) — Review 1 & 2: Process + Quality

**Generated PowerPoint Files:**
- Primary Master Deck: [`QuizSphere_Master_Review_1_and_2.pptx`](file:///c:/Users/piyush/Documents/Online_Quiz_System/QuizSphere_Master_Review_1_and_2.pptx)
- Review Deck Copy: [`QuizSphere_Review_1_and_2_Deck.pptx`](file:///c:/Users/piyush/Documents/Online_Quiz_System/QuizSphere_Review_1_and_2_Deck.pptx)

**Academic Course:** BBAT104: Fundamentals of Total Quality Management (TQM)  
**Baseline System:** Baseline System 9 — Online Quiz System  
**Assigned Quality Goal:** Q20 — Overall Software Quality (Zero Latency Submissions & 100% Deterministic Auto-Grading)  

---

### Table of Contents (42 Slides)
- **Part 1: Process & Quality Fundamentals (Slides 1–12)**
  1. Title Slide: Process Map, Stakeholders, Measurable Requirements, Quality Goals
  2. Vision, Mission, Quality Objective
  3. Three Quality Ideas Behind the Software (Error Prevention, Process Control, Monitoring)
  4. Process Map & Controls Sitting on This Process
  5. SIPOC of the Examination Process
  6. Stakeholders and Their Needs
  7. Measurable Requirements (Viva): Need $\rightarrow$ Number We Can Count
  8. Measurable Quality Objectives (O1 to O5)
  9. Assigned Quality Goal Q20: Overall Software Quality
  10. Feature $\rightarrow$ Quality Idea Mapping
  11. Crucial Mapping (Say This in Viva)
  12. One-Line Viva
- **Part 2: Modular Architecture & Folder System (Slides 13–26)**
  13. CASE: Online Quiz System Architecture Overview
  14. What Each Folder Means
  15. Why This Folder Structure?
  16. The One Rule to Remember: UI Never Talks Directly to Database
  17. What You Must Be Able to Explain
  18. Full Modular Folder Structure (ASCII Tree)
  19. What Each File Does: Start + Config + Database
  20. What Each File Does: Models
  21. What Each File Does: Services (The Work Happens Here)
  22. What Each File Does: UI Screens (What the Person Sees)
  23. What Each File Does: Reports + Utils + Assets
  24. How a Click Uses These Files (Candidate Submit Walkthrough)
  25. Architecture 1: Request Goes Down (Multi-Tier Layers)
  26. Architecture 2: Quality Loop (Data into TQM Tools)
- **Part 3: Database & Schema Design (Slides 27–31)**
  27. `database/schema.py`: Tables We Create
  28. `users` Table: Live Data & Security Schema
  29. `quizzes` and `attempts` Tables: Live Data & Scorecard Telemetry
  30. `audit_logs` and `error_logs`: Traceability & Feeding FMEA
  31. Why `migrations.py` Matters
- **Part 4: TQM Quality Tools for Review 2 (Slides 32–39)**
  32. Software Feature $\rightarrow$ TQM Concept Matrix
  33. Quality Dashboard (Real-Time Quality Metrics)
  34. Pareto Analysis: 80/20 Rule from Error Logs
  35. Fishbone (Ishikawa) Diagram: Why Exam Submission Errors Happen
  36. FMEA Matrix: Severity $\times$ Occurrence $\times$ Detection with Revised RPNs
  37. How Logs Feed FMEA
  38. PDCA Continuous Improvement Cycle on Exam Proctoring
  39. Build This Much First: Review 1 vs Later Reviews
- **Part 5: Live Working Application Demo & Closing (Slides 40–42)**
  40. Working Application Demo Guide: Setup & Execution Commands
  41. Live Demonstration Walkthroughs (Student, Faculty, Admin)
  42. One Sentence for Viva (The Perfect Closing)

---

### Detailed Slide Transcripts & Speaker Notes

#### Slide 1: Title Slide
- **Header:** SRS REVIEW 1 & 2 · PROCESS + QUALITY
- **Title:** Process map, stakeholders, measurable requirements, quality goals
- **Subtitle:** Online Quiz System (QuizSphere Pro) — Baseline System 9 | Q20 Overall Software Quality
- **Speaker Note:** *"Good morning respected evaluators. Today we present our comprehensive Review 1 & 2 presentation for the Online Quiz System under course BBAT104. We demonstrate how TQM principles, measurable quality objectives, and modular architecture ensure zero-latency examination and zero undetected infractions."*

#### Slide 2: Vision, mission, quality objective
- **Vision:** An examination environment where zero unrecorded answers, zero grading latency, and zero undetected academic infractions occur.
- **Mission:** Build a high-performance assessment system (Web & Desktop) that records student attempts, blocks cheating via active proctoring, auto-grades in <250ms, and shows who did what.
- **Quality Objective:** Prevent the error at the source (Poka-yoke). Control the examination process. Monitor every attempt and infraction with logs.
- **Speaker Note:** *"Our vision is zero lost answers and zero cheating. Our mission is delivering a dual Web and Desktop app that auto-grades in under 250 milliseconds with full audit trails."*

#### Slide 3: Three quality ideas behind the software
- **Error prevention at source (Poka-yoke):** Blank question prompt blocked; missing correct choice blocked; duration $\le 0$ or $>180$m blocked; duplicate Join Code blocked.
- **Process control (One path for work):** Quiz Authoring $\rightarrow$ Join Code $\rightarrow$ Timed Exam $\rightarrow$ Scorecard. UI cannot skip rules; student cannot bypass countdown.
- **Monitoring (See and trace):** Dashboard KPI alerts; proctor infraction audit log; student attempt telemetry; error log $\rightarrow$ FMEA integration.
- **Speaker Note:** *"Our software is governed by three quality ideas: Error prevention at source stops bad data before it enters the database; Process control enforces a strict step-by-step workflow; Monitoring provides continuous traceability."*

#### Slide 4: Process map & controls sitting on this process
- **Process Pipeline:** Teacher $\rightarrow$ Quiz Creation $\rightarrow$ Join Code $\rightarrow$ Student $\rightarrow$ Exam Execution $\rightarrow$ Report.
- **Controls Sitting on This Process:**
  - *On Quiz Creation:* Title, passing score (1–100%), duration, and question choices must be valid.
  - *On Join Code:* Normalization to uppercase, SQL uniqueness check, sub-25ms resolution.
  - *On Exam Execution:* Authoritative server timer countdown + window blur focus loss tracking.
  - *On Report / Submission:* Measure latency (<250ms), grade deterministically, and record cheat flags.
- **Speaker Note:** *"Notice the controls sitting on each step of the pipeline. At no point can a user skip a quality check."*

#### Slide 5: SIPOC of the examination process
- **S (Suppliers):** Teacher / Faculty, Curriculum Subject Matter Experts, AI Question Engine, Database.
- **I (Inputs):** Question Prompts, Answer Key, Duration Bounds, Candidate Code, Student Credentials.
- **P (Process):** Validate Entry $\rightarrow$ Generate Code $\rightarrow$ Host Timed Exam $\rightarrow$ Track Window Blur $\rightarrow$ Auto-grade & Save.
- **O (Outputs):** Instant Scorecard, Question Breakdown, Class Gradebook, Violation Audit Log.
- **C (Customers):** Student / Examinee, Teacher / Examiner, System Admin, Academic Auditor.
- **Speaker Note:** *"The SIPOC matrix establishes the end-to-end boundary of our examination system from supplier input to customer value."*

#### Slide 6: Stakeholders and their need
- **Student / Candidate:** Zero latency during submission. Transparent scorecard. Fair countdown timer.
- **Teacher / Examiner:** Fast quiz creation (manual & AI). Quick join code. Live class gradebook.
- **Administrator / Owner:** User governance, platform telemetry numbers, CSV audit exports.
- **Academic Auditor:** Who submitted what, exact timestamps, and proctoring violation logs.
- **Institution:** Zero exam downtime. High academic integrity. Automated database backups.

#### Slide 7: Measurable requirements (viva)
- **Zero lost submissions:** Submission loss count = 0 (100% recorded).
- **Zero grading latency:** Submission turnaround time < 250 ms (achieved ~25 ms).
- **100% grading accuracy:** Score calculation consistency = 100.0% (Zero Defect).
- **Trace academic dishonesty:** 100% of window/tab switches logged with timestamp.
- **Find assessment fast:** Join Code resolution time < 25 milliseconds.
- **Protect institutional data:** Hourly automated database snapshot in `backups/` = 100%.

#### Slide 8: Measurable quality objectives (O1 to O5)
- **O1:** Zero lost submissions on any student attempt under peak concurrency.
- **O2:** Every test submission either saves fully (ACID) or not at all.
- **O3:** Every user action and proctoring violation is captured in audit logs.
- **O4:** Automated database backup file created at least once a day in `backups/`.
- **O5:** Login and code validation fail safely. App does not crash.

#### Slide 9: Assigned quality goal Q20: Overall Software Quality
- **Auto Backup:** Automated timestamped copy of `quiz_system.db` saved in `backups/`.
- **Audit Log:** User ID, action, join code, score, cheat violation tally, submission time.
- **Input Validation:** Poka-yoke prevents blank questions, negative limits, duplicate codes.
- **Error Recovery:** ACID transactions: if save fails, show error. No half-graded attempt.
- **User Roles:** Student / Faculty / Admin only see their dedicated workflows.

#### Slide 10: Feature $\rightarrow$ quality idea
- *Input Validation* $\rightarrow$ Error prevention at source (Poka-yoke)
- *User Roles* $\rightarrow$ Process control + accountability
- *Audit Log & Violation Tracker* $\rightarrow$ Monitoring + traceability
- *Error Recovery (ACID)* $\rightarrow$ Reliability (no broken test submission)
- *Auto Backup* $\rightarrow$ Reliability (data is never lost)

#### Slide 11: Crucial mapping (say this)
- **Customer need:** Honest, fast, zero-latency assessment.
- **Measurable requirement:** Turnaround latency < 250ms, zero lost answers.
- **Process control:** Assessment cannot skip proctor check or code validation.
- **Monitoring:** Audit log + violation tracker + admin dashboard.
- **Quality goal:** Q20 Overall Software Quality features above.

#### Slide 12: One-line viva
- **Requirement:** Zero latency, zero cheating undetected.
- **Objective:** Submissions graded < 250ms, 100% tab switches logged.
- **How:** Validate at entry, control the exam path, monitor with audit and violation logs.

#### Slide 13: CASE: Online Quiz System Architecture
- *"Every folder, every screen, every table. Simple enough to explain from the last row."*
- Quality-oriented system | Modular design | TQM controls.

#### Slide 14: What each folder means
- `ui/`: What the user sees (Web SPA & CustomTkinter Desktop).
- `services/`: Business rules (auth, quiz, grading, proctoring).
- `models/`: What a User / Quiz / Attempt / Question is.
- `database/`: How data is stored (SQLite connection, schema, migrations).
- `reports/`: Numbers for decisions (gradebook, telemetry, CSV).
- `server.py`: Starts the program only (FastAPI lifespan, zero raw SQL in UI).

#### Slide 15: Why this folder structure?
- One job per folder. Easy to explain.
- A bug in grading does not hide inside `server.py` or `desktop_app.py`.
- Validation and anti-cheat audit have a dedicated home.
- You can build and test one layer at a time (Pytest unit tests pass independently).

#### Slide 16: The one rule to remember
- **The screen must not talk to the database.**
- `UI` $\rightarrow$ `Service` $\rightarrow$ `Model / Database`
- No `SELECT * FROM quizzes` or `INSERT INTO attempts` inside UI buttons.

#### Slide 17: What you must be able to explain
1. What each folder is for.
2. How a click travels: UI $\rightarrow$ Service $\rightarrow$ Database.
3. What data sits in each table (`users`, `quizzes`, `attempts`, `audit_logs`).
4. How this is TQM, not only CRUD (Poka-yoke, CTQ, FMEA, Pareto, PDCA).

#### Slide 18: Full modular folder structure
- Displays the complete project tree across Core, Database, Services, Models, UI, Utils, Reports, and Tests.

#### Slide 19: What each file does — start + config + database
- `server.py` / `desktop_app.py`, `config/settings.py`, `database/db.py`, `database/schema.py`, `database/migrations.py`.

#### Slide 20: What each file does — models
- `models/user.py`, `models/quiz.py`, `models/question.py`, `models/attempt.py`, `models/violation.py`.

#### Slide 21: What each file does — services
- `auth_service.py`, `quiz_service.py`, `ai_service.py`, `grading_service.py`, `proctor_service.py`, `report_service.py`.

#### Slide 22: What each file does — UI screens
- `ui/login.py / auth.js`, `ui/candidate_arena`, `ui/examiner_studio`, `ui/gradebook`, `ui/admin_panel`.

#### Slide 23: What each file does — reports + utils + assets
- `reports/gradebook.py`, `reports/tqm_report.py`, `utils/validators.py`, `utils/logger.py`, `utils/security.py`, `assets/`.

#### Slide 24: How a click uses these files (Candidate Submit Walkthrough)
1. **Screen:** `candidate_arena` takes answers and user clicks Submit.
2. **Service:** `grading_service` checks answers against the key.
3. **Extra service:** `proctor_service` packages violation counts and timestamps.
4. **Utils:** `validators.py` rejects malformed or corrupted payloads.
5. **Database:** `db.py` saves attempt, score, and violations in one ACID transaction.
6. **Proof:** `audit_logs` and `attempts` get a permanent row (<25ms).
7. **Later:** `tqm_report`, Pareto chart, and FMEA matrix read those logs.

#### Slide 25: Architecture 1 — request goes down
- Layer stack: User/Admin $\rightarrow$ UI Layer $\rightarrow$ Service Layer $\rightarrow$ Model & Utility Layer $\rightarrow$ Database Layer $\rightarrow$ Reports/Analytics.

#### Slide 26: Architecture 2 — quality loop
- Real-time exam transaction data feeds the TQM analysis and continuous improvement loop.

#### Slide 27: database / schema.py — tables we create
- Detailed specifications for `users`, `quizzes`, `attempts`, `audit_logs`, `error_logs`, and `backups/`.

#### Slide 28: users table — example rows & schema
- Live sample rows (`admin`, `faculty`, `student`) and security attributes (`password_hash`, `role`, `department`, `created_at`).

#### Slide 29: quizzes and attempts tables — live examples
- Sample assessment records (`QZ-1001`, `QZ-2045`, `QZ-3942`) and student attempt scorecards.

#### Slide 30: audit_logs & error_logs — feeding FMEA
- Sample trace logs (`CREATE_QUIZ`, `SUBMIT_EXAM`, `TAB_BLUR`) and error code frequencies (`E01` to `E04`).

#### Slide 31: Why migrations.py matters
- Preserving student test history when table schemas evolve; ensuring zero data loss during feature upgrades.

#### Slide 32: Software feature $\rightarrow$ TQM concept
- 10-point cross-reference mapping software components to fundamental TQM concepts.

#### Slide 33: Quality dashboard (Real-time telemetry)
- Live quality metrics: 100% grading accuracy, 24.8ms average latency, 0.4% proctor violation rate, zero defect rate.

#### Slide 34: Pareto — from error_logs and violation telemetry
- 80/20 root cause prioritization: Focus loss / tab switch accounts for 68% of candidate infractions, followed by code typos (18%).

#### Slide 35: Fishbone — why exam submission errors happen
- Ishikawa diagram mapping potential causes across People, Process, Software, Data, and Machine.

#### Slide 36: FMEA — from automated error logs
- Initial RPN scores up to 336 driven down below 50 via Poka-yoke dialogs, local caching, and focus listeners (86% average risk reduction).

#### Slide 37: How logs feed FMEA
- 5-step data path converting logged error frequencies directly into the FMEA occurrence metric.

#### Slide 38: PDCA on the same problem (Continuous Improvement)
- Plan: Target zero unmonitored infractions.
- Do: Implement `<FocusOut>` and tab switch listeners.
- Check: Audit violation rates and drop RPN from 336 to 48.
- Act: Standardize proctor monitoring across Web and Desktop.

#### Slide 39: Build this much first — Review 1 vs Later Reviews
- Review 1 delivers: Authentication, join codes, timed exam with 3 checks, zero-latency grading, audit logs, working Web and Desktop apps.
- Later reviews deliver: Full FMEA scoring marks, automated Pareto charts, complete Ishikawa fishbone, and biometric proctoring.

#### Slide 40: Working Application Demo Guide — Setup & Commands
- Commands to launch Web Server (`python server.py`), Desktop GUI (`python desktop_app.py`), and Unit Tests (`pytest tests/ -v`).
- Test credentials table for Student (`student`/`student123`), Faculty (`faculty`/`faculty123`), and Admin (`admin`/`admin123`).

#### Slide 41: Live demonstration walkthroughs (Student, Faculty, Admin)
- Step-by-step examination scenario, faculty AI quiz creation scenario, and admin telemetry governance scenario.

#### Slide 42: One sentence for viva (The Perfect Closing)
- *"The UI never writes SQL.
Validation stops bad data at the source.
Audit records who submitted what and when.
Cheating is tracked and timeouts cannot corrupt grades.
Logs become Pareto, Fishbone, FMEA, and PDCA."*

---
**Prepared For:** Academic Review 1 & 2 Evaluation  
**Project:** Online Quiz System (QuizSphere Pro)  
**Status:** Complete, Verified & Available in `.pptx` and `.md` formats.
