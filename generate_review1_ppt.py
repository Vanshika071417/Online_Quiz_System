"""
Generate a professional, high-impact PowerPoint presentation (.pptx)
for Review 1: Setup & SRS (Online Quiz System - QuizSphere Pro).
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Color Palette
    BG_COLOR = RGBColor(15, 23, 42)         # #0f172a Dark Slate
    CARD_BG = RGBColor(30, 41, 59)          # #1e293b Container Slate
    CARD_BORDER = RGBColor(51, 65, 85)      # #334155
    ACCENT_BLUE = RGBColor(59, 130, 246)    # #3b82f6 Primary Blue
    ACCENT_GREEN = RGBColor(16, 185, 129)   # #10b981 Emerald
    ACCENT_AMBER = RGBColor(245, 158, 11)   # #f59e0b Amber
    ACCENT_PURPLE = RGBColor(139, 92, 246)  # #8b5cf6 Purple
    TEXT_LIGHT = RGBColor(255, 255, 255)    # White
    TEXT_MUTED = RGBColor(203, 213, 225)    # #cbd5e1 Light Slate
    TEXT_DIM = RGBColor(148, 163, 184)      # #94a3b8 Dim

    def apply_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background() # No border
        return bg

    def add_header(slide, title_text, category_text="REVIEW 1 — SETUP & SRS"):
        # Category badge / subhead
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = category_text.upper()
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = ACCENT_BLUE

        # Main Title
        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT

    def add_card(slide, left, top, width, height, stripe_color=None):
        card = slide.shapes.add_shape(MSO_SHAPE.ROUNDED_RECTANGLE, left, top, width, height)
        card.fill.solid()
        card.fill.fore_color.rgb = CARD_BG
        card.line.color.rgb = CARD_BORDER
        card.line.width = Pt(1)

        if stripe_color:
            stripe = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, Inches(0.08))
            stripe.fill.solid()
            stripe.fill.fore_color.rgb = stripe_color
            stripe.line.fill.background()
        return card

    # ==========================================
    # SLIDE 1: Title Slide
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_background(s1)

    # Accent decorative banner
    banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(1.8), Inches(0.35))
    banner.fill.solid()
    banner.fill.fore_color.rgb = ACCENT_BLUE
    banner.line.fill.background()
    p_b = banner.text_frame.paragraphs[0]
    p_b.text = "ACADEMIC REVIEW 1"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = TEXT_LIGHT
    p_b.alignment = PP_ALIGN.CENTER

    # Main Title
    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.5), Inches(1.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Online Quiz System (QuizSphere Pro)"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_LIGHT

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Setup & Software Requirements Specification (SRS)"
    p1_sub.font.size = Pt(20)
    p1_sub.font.color.rgb = ACCENT_BLUE
    p1_sub.space_before = Pt(8)

    # Metadata Cards
    cards_data = [
        ("Course & Project Topic", "BBAT104: Fundamentals of TQM\nBaseline System 9: Online Quiz System", ACCENT_BLUE),
        ("Assigned Quality Goal", "Q20: Overall Software Quality\nDashboards, Validation, Export & Backups", ACCENT_GREEN),
        ("Core Engineering Target", "Zero-Latency Submissions (<250ms)\nDeterministic Zero-Defect Auto-Grading", ACCENT_AMBER),
        ("Implementation Parity", "FastAPI Unified Web Backend + SPA\nNative CustomTkinter Desktop Client", ACCENT_PURPLE)
    ]

    for i, (head, val, col) in enumerate(cards_data):
        c_left = Inches(0.8 + i * 2.95)
        add_card(s1, c_left, Inches(3.8), Inches(2.8), Inches(2.4), stripe_color=col)
        box = s1.shapes.add_textbox(c_left + Inches(0.15), Inches(4.0), Inches(2.5), Inches(2.0))
        tf = box.text_frame
        tf.word_wrap = True
        ph = tf.paragraphs[0]
        ph.text = head.upper()
        ph.font.size = Pt(10)
        ph.font.bold = True
        ph.font.color.rgb = col
        ph.space_after = Pt(8)
        
        pv = tf.add_paragraph()
        pv.text = val
        pv.font.size = Pt(12)
        pv.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 2: Problem Statement & Baseline
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_background(s2)
    add_header(s2, "Problem Statement & Baseline Understanding")

    # Left Card: The Problem
    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), stripe_color=RGBColor(239, 68, 68))
    b2_left = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf2_l = b2_left.text_frame
    tf2_l.word_wrap = True
    
    p = tf2_l.paragraphs[0]
    p.text = "CRITICAL LIMITATIONS IN EXISTING SYSTEMS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = RGBColor(239, 68, 68)
    p.space_after = Pt(12)

    problems = [
        ("Network Lag & Submission Hangs", "High-concurrency test submissions freeze or time out, resulting in unrecorded candidate answers and data loss."),
        ("Academic Integrity Vulnerabilities", "Standard online forms lack real-time window focus detection, allowing rampant tab-switching and external lookup."),
        ("Teacher Manual Burden", "Educators spend hours formulating questions, creating multiple choice formats, calculating scores, and tabulating spreadsheets."),
        ("Single Point of Failure", "Lack of automated snapshot backups and offline desktop failover exposes institutions to fatal exam downtime.")
    ]
    for title, desc in problems:
        pt = tf2_l.add_paragraph()
        pt.text = f"• {title}:"
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = TEXT_LIGHT
        pt.space_before = Pt(6)
        pd = tf2_l.add_paragraph()
        pd.text = f"  {desc}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_MUTED

    # Right Card: The Solution (QuizSphere Pro)
    add_card(s2, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    b2_right = s2.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf2_r = b2_right.text_frame
    tf2_r.word_wrap = True

    p = tf2_r.paragraphs[0]
    p.text = "QUIZSPHERE PRO ARCHITECTURAL SOLUTION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(12)

    solutions = [
        ("Sub-250ms Instant Evaluation", "In-memory deterministic scoring pipeline processes answers and yields full scorecards in 15-35 milliseconds."),
        ("Anti-Cheat Proctoring Hub", "Continuous window focus loss and tab-switch telemetry increments violation counters and logs timestamps in real time."),
        ("AI Curriculum Question Synthesis", "Faculty input syllabus keywords to automatically generate 5-20 verified MCQs with rationale keys in seconds."),
        ("Dual Platform Deployment", "Simultaneous access via responsive Web browser SPA (FastAPI) and native standalone Windows Desktop App (CustomTkinter).")
    ]
    for title, desc in solutions:
        pt = tf2_r.add_paragraph()
        pt.text = f"✔ {title}:"
        pt.font.bold = True
        pt.font.size = Pt(11)
        pt.font.color.rgb = ACCENT_GREEN
        pt.space_before = Pt(6)
        pd = tf2_r.add_paragraph()
        pd.text = f"  {desc}"
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 3: Quality Objectives & CTQ Metrics
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_background(s3)
    add_header(s3, "Quality Objectives & TQM Critical-to-Quality (CTQ)")

    # 4 CTQ Metric Cards
    ctqs = [
        ("SUBMISSION LATENCY", "< 250 ms", "Achieved: ~25 ms", "Turnaround time from student submission to verified database scorecard.", ACCENT_BLUE),
        ("GRADING ACCURACY", "100.0%", "Zero Defect", "Scoring consistency between expected cryptographic key and calculated result.", ACCENT_GREEN),
        ("ANTI-CHEAT COVERAGE", "100%", "Full Telemetry", "Focus blur events and unauthorized window switches logged with infraction counts.", ACCENT_AMBER),
        ("DATA RECOVERY (RPO)", "Hourly Snapshots", "Automated Backups", "Timestamped SQLite snapshots saved to backups/ with one-click restore.", ACCENT_PURPLE)
    ]

    for i, (title, target, status, desc, col) in enumerate(ctqs):
        c_left = Inches(0.8 + i * 2.95)
        add_card(s3, c_left, Inches(1.8), Inches(2.8), Inches(4.9), stripe_color=col)
        box = s3.shapes.add_textbox(c_left + Inches(0.15), Inches(2.0), Inches(2.5), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(10)

        p_t = tf.add_paragraph()
        p_t.text = target
        p_t.font.size = Pt(22)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_LIGHT

        p_s = tf.add_paragraph()
        p_s.text = status
        p_s.font.size = Pt(11)
        p_s.font.bold = True
        p_s.font.color.rgb = col
        p_s.space_after = Pt(12)

        p_d = tf.add_paragraph()
        p_d.text = desc
        p_d.font.size = Pt(10)
        p_d.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 4: Scope & User Roles (RBAC)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_background(s4)
    add_header(s4, "Scope & Role-Based Access Control (RBAC)")

    roles = [
        ("STUDENT / CANDIDATE", "Candidate Arena", [
            "Join assessments using 6-character Join Code (e.g. QZ-1001)",
            "Authoritative countdown timer with zero client drift",
            "Active Anti-Cheat window focus & blur detection",
            "Instant scorecards with question-by-question explanations",
            "Restricted view: Examiner Studio & Admin Panel hidden"
        ], ACCENT_BLUE),
        ("FACULTY / EXAMINER", "Examiner Studio", [
            "Manual quiz authoring with custom time limits & passing marks",
            "AI-assisted curriculum generation based on topic & difficulty",
            "Instant Join Code generation for fast student distribution",
            "Live Class Gradebook with candidate scores & cheat violation counts",
            "Restricted view: Admin governance panel hidden"
        ], ACCENT_GREEN),
        ("ADMINISTRATOR", "Platform Admin Console", [
            "Platform telemetry (total users, active faculty, attempt counts)",
            "User governance roster with search & role filters",
            "Candidate Performance Scorecard drill-down modal",
            "Instant CSV exports for rosters and complete audit logs",
            "Database integrity monitoring and backup snapshot triggers"
        ], ACCENT_PURPLE)
    ]

    for i, (role_name, portal, perms, col) in enumerate(roles):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s4, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s4.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = role_name
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = col

        p_sub = tf.add_paragraph()
        p_sub.text = f"Portal: {portal}"
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = TEXT_LIGHT
        p_sub.space_after = Pt(12)

        for perm in perms:
            pp = tf.add_paragraph()
            pp.text = f"• {perm}"
            pp.font.size = Pt(10)
            pp.font.color.rgb = TEXT_MUTED
            pp.space_before = Pt(4)

    # ==========================================
    # SLIDE 5: Modular Folder Architecture
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_header(s5, "Modular Folder Architecture & Technology Stack")

    arch_sections = [
        ("BACKEND CORE", "FastAPI + Uvicorn + SQLite", [
            "server.py: Unified REST API and WebSocket connection manager",
            "backend/api/v1/: Enterprise modular routers (auth, quizzes, attempts, admin)",
            "backend/core/: Database session factory, security JWT, telemetry middleware",
            "backend/models/: Declarative multi-tenant SQLAlchemy domain models",
            "ai_quiz_generator.py: Curriculum MCQ generation engine"
        ], ACCENT_BLUE),
        ("DESKTOP APPLICATION", "CustomTkinter GUI Engine", [
            "desktop_app.py: Standalone native Windows client",
            "DatabaseManager: Direct transactional SQLite integration",
            "Strict Grid Alignment: Pixel-perfect 44px table rows and KPI cards",
            "Theme Engine: Cream Modern Theme + High-Contrast Dark Mode",
            "Accessibility: Dynamic font scaling (A+/A-) and focus modes"
        ], ACCENT_GREEN),
        ("WEB APPLICATION", "HTML5 + Vanilla CSS + JS", [
            "index.html: High-performance single page assessment portal",
            "assets/css/: Modular design tokens (variables, quiz-engine, admin, examiner)",
            "assets/js/: Segregated controllers (auth.js, app.js, quiz-engine.js, admin.js)",
            "sw.js & manifest.json: Mobile progressive web app enablement"
        ], ACCENT_AMBER),
        ("QUALITY & TEST HARNESS", "Pytest Automated Suite", [
            "tests/test_web_auth.py: Web API contract verification",
            "tests/test_desktop_auth.py: Desktop authentication & RBAC tabs",
            "tests/test_admin_panel.py: Admin telemetry and user report verification",
            "tests/test_join_code_workflow.py: End-to-end quiz code workflow",
            "22 / 22 Tests Passing with 0 errors"
        ], ACCENT_PURPLE)
    ]

    for i, (title, tech, items, col) in enumerate(arch_sections):
        row = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * 5.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s5, c_left, c_top, Inches(5.7), Inches(2.35), stripe_color=col)
        box = s5.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(5.3), Inches(2.0))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        p_t = tf.add_paragraph()
        p_t.text = f"Stack: {tech}"
        p_t.font.size = Pt(10)
        p_t.font.bold = True
        p_t.font.color.rgb = TEXT_LIGHT
        p_t.space_after = Pt(4)

        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"▪ {it}"
            pi.font.size = Pt(9)
            pi.font.color.rgb = TEXT_MUTED
            pi.space_before = Pt(1)

    # ==========================================
    # SLIDE 6: Modules and Features
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_background(s6)
    add_header(s6, "Core Modules & Feature Breakdown")

    modules = [
        ("M1: Identity & Authentication", "Role-based sign-in and registration for Student, Faculty, and Admin. Dynamically alters client navigation tabs according to authenticated persona.", ACCENT_BLUE),
        ("M2: Examiner Studio & AI Wizard", "Faculty test creator supporting manual MCQ authoring or AI syllabus synthesis. Configures duration, passing score, category, and deterministic 6-character Join Code.", ACCENT_GREEN),
        ("M3: Candidate Assessment Arena", "Quick test join via code. Delivers questions with interactive palette, authoritative server countdown timer, and automatic submission upon deadline expiry.", ACCENT_AMBER),
        ("M4: Anti-Cheat Proctoring Hub", "Active focus tracking monitors window blur and tab switching during exams. Violations increment in real time and are permanently audited into submission records.", RGBColor(239, 68, 68)),
        ("M5: Zero-Latency Auto-Grading", "In-memory evaluation engine compares answers against key in ~25ms. Displays immediate percentage, pass/fail status, and per-question rationale explanations.", ACCENT_PURPLE),
        ("M6: Admin Governance & Telemetry", "Platform telemetry KPIs, filterable user roster, candidate performance scorecard drill-down modal, and instant one-click CSV export streams.", RGBColor(14, 165, 233))
    ]

    for i, (m_title, m_desc, col) in enumerate(modules):
        row = i // 3
        col_idx = i % 3
        c_left = Inches(0.8 + col_idx * 3.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s6, c_left, c_top, Inches(3.8), Inches(2.35), stripe_color=col)
        box = s6.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.2), Inches(3.4), Inches(1.95))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = m_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(6)

        pd = tf.add_paragraph()
        pd.text = m_desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: Database & System Design
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_background(s7)
    add_header(s7, "Database & System Design (ACID SQLite Persistence)")

    # Left: Database Tables
    tables = [
        ("TABLE: users", "id (PK), username (UNIQUE), password, role, full_name, department, created_at", ACCENT_BLUE),
        ("TABLE: quizzes", "id (PK), join_code (UNIQUE), teacher_name, title, category, duration_minutes, passing_score, tags, questions_json, created_at", ACCENT_GREEN),
        ("TABLE: attempts", "id (PK), quiz_id (FK), join_code, quiz_title, teacher_name, student_name, score, total_questions, percentage, passed, cheat_violations, submitted_at", ACCENT_PURPLE)
    ]

    for i, (t_name, t_schema, col) in enumerate(tables):
        top_pos = Inches(1.8 + i * 1.65)
        add_card(s7, Inches(0.8), top_pos, Inches(6.8), Inches(1.5), stripe_color=col)
        box = s7.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.15), Inches(6.4), Inches(1.2))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = t_name
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(4)

        ps = tf.add_paragraph()
        ps.text = t_schema
        ps.font.size = Pt(9)
        ps.font.color.rgb = TEXT_LIGHT

    # Right: Architectural Highlights
    add_card(s7, Inches(7.8), Inches(1.8), Inches(4.7), Inches(4.8), stripe_color=ACCENT_AMBER)
    r_box = s7.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.3), Inches(4.4))
    tf_r = r_box.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "DATA INTEGRITY & DESIGN HIGHLIGHTS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(10)

    highlights = [
        ("ACID Transactions", "All quiz updates and candidate submissions execute in atomic SQLite write transactions."),
        ("Normalized Indexing", "Indexed lookups on Join Codes (UPPER) and usernames ensure sub-millisecond retrieval."),
        ("Durable Question Snapshotting", "Questions are serialized as self-contained JSON strings inside `quizzes` to prevent external dependency drift."),
        ("Denormalized Submission Audit", "Attempts store student name, quiz title, and authoring teacher to ensure immutable historical scorecards even if parent records change."),
        ("Automated Snapshot Engine", "Backups are saved to `backups/quiz_system_*.db` protecting institutional records.")
    ]
    for h_t, h_d in highlights:
        ph = tf_r.add_paragraph()
        ph.text = f"• {h_t}: {h_d}"
        ph.font.size = Pt(9.5)
        ph.font.color.rgb = TEXT_MUTED
        ph.space_before = Pt(5)

    # ==========================================
    # SLIDE 8: Initial UI & System Workflow
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_background(s8)
    add_header(s8, "Initial UI & End-to-End System Workflow")

    steps = [
        ("1. AUTHENTICATE", "User logs in as Student, Faculty, or Admin. Navigation immediately configures role-specific view.", ACCENT_BLUE),
        ("2. CREATE QUIZ", "Faculty designs quiz manually or triggers AI Generator. Server assigns unique Join Code (e.g. QZ-4821).", ACCENT_GREEN),
        ("3. ENTER CODE", "Student inputs 6-char Join Code. Assessment metadata and questions load into Candidate Arena in <25ms.", ACCENT_AMBER),
        ("4. TAKE & MONITOR", "Countdown timer runs authoritatively. Client anti-cheat monitors focus and logs tab blurs.", RGBColor(239, 68, 68)),
        ("5. AUTO-GRADE", "Candidate submits test. Server auto-grades in ~25ms and presents detailed scorecard with answer rationale.", ACCENT_PURPLE),
        ("6. AUDIT & EXPORT", "Teacher inspects class gradebook. Admin analyzes platform telemetry and streams roster & attempt CSVs.", RGBColor(14, 165, 233))
    ]

    for i, (s_title, s_desc, col) in enumerate(steps):
        row = i // 3
        col_idx = i % 3
        c_left = Inches(0.8 + col_idx * 3.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s8, c_left, c_top, Inches(3.8), Inches(2.35), stripe_color=col)
        box = s8.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.2), Inches(3.4), Inches(1.95))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = s_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(6)

        pd = tf.add_paragraph()
        pd.text = s_desc
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 9: CRUD Operations Matrix
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_background(s9)
    add_header(s9, "CRUD Operations Aligned with Quality Goals")

    cruds = [
        ("USER MANAGEMENT", ACCENT_BLUE, [
            "CREATE: Register accounts via /api/auth/register or Desktop UI",
            "READ: Authenticate (/api/auth/login), Roster (/api/admin/users)",
            "UPDATE: Department assignment, accommodation time buffers",
            "DELETE: Soft-deactivate user accounts and audit permissions"
        ]),
        ("ASSESSMENT MANAGEMENT", ACCENT_GREEN, [
            "CREATE: Manual authoring (/api/quizzes) or AI Wizard (/api/ai-generate)",
            "READ: Code resolver (/api/quizzes/code/{code}), Quiz listings",
            "UPDATE: Modify time duration, passing mark, or question contents",
            "DELETE: Archive assessment and withdraw public Join Code"
        ]),
        ("SUBMISSIONS & AUDIT", ACCENT_AMBER, [
            "CREATE: Atomic test submission (/api/quizzes/{id}/submit)",
            "READ: Teacher Gradebook (/api/teacher/reports), Candidate Scorecards",
            "UPDATE: Durable progress autosaving during active exam sessions",
            "DELETE: Controlled audit retention purge"
        ]),
        ("BACKUPS & REPORTS", ACCENT_PURPLE, [
            "CREATE: Automated timestamped snapshots in backups/ directory",
            "READ: Stream CSV reports (/api/admin/export/users.csv & submissions.csv)",
            "UPDATE: Validate snapshot integrity against active database",
            "DELETE: Rolling backup policy purging snapshots older than 30 days"
        ])
    ]

    for i, (title, col, ops) in enumerate(cruds):
        row = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * 5.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s9, c_left, c_top, Inches(5.7), Inches(2.35), stripe_color=col)
        box = s9.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(5.3), Inches(2.0))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(4)

        for op in ops:
            po = tf.add_paragraph()
            po.text = f"• {op}"
            po.font.size = Pt(9.5)
            po.font.color.rgb = TEXT_LIGHT
            po.space_before = Pt(2)

    # ==========================================
    # SLIDE 10: Working Demo & Live Execution
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_background(s10)
    add_header(s10, "Working Application & Live Demonstration Plan")

    # Left: Web App
    add_card(s10, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), stripe_color=ACCENT_BLUE)
    box_w = s10.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_w = box_w.text_frame
    tf_w.word_wrap = True

    p = tf_w.paragraphs[0]
    p.text = "WEB APPLICATION DEMONSTRATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(8)

    w_points = [
        ("Command to Start", "python server.py (Runs on http://localhost:8000)"),
        ("Live Student Workflow", "Sign in as 'student' / 'student123' -> Enter Join Code 'QZ-1001' -> Complete assessment -> Demonstrate anti-cheat alert -> Receive instant scorecard."),
        ("Live Faculty Workflow", "Sign in as 'faculty' / 'faculty123' -> Create quiz with AI Question Generator -> Copy Join Code -> View class gradebook with submitted candidate results."),
        ("Live Admin Workflow", "Sign in as 'admin' / 'admin123' -> Inspect platform telemetry KPIs -> Open candidate scorecard modal -> Download Roster & Submissions CSV.")
    ]
    for wt, wd in w_points:
        pw = tf_w.add_paragraph()
        pw.text = f"• {wt}:"
        pw.font.bold = True
        pw.font.size = Pt(10)
        pw.font.color.rgb = TEXT_LIGHT
        pw.space_before = Pt(4)
        pvd = tf_w.add_paragraph()
        pvd.text = f"  {wd}"
        pvd.font.size = Pt(9)
        pvd.font.color.rgb = TEXT_MUTED

    # Right: Desktop App
    add_card(s10, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    box_d = s10.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf_d = box_d.text_frame
    tf_d.word_wrap = True

    p = tf_d.paragraphs[0]
    p.text = "DESKTOP APPLICATION DEMONSTRATION"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)

    d_points = [
        ("Command to Start", "python desktop_app.py (Native Windows Standalone GUI)"),
        ("Desktop Authentication", "Native authentication dialog supporting Student, Faculty, and Admin sign-in with instant role-specific tab adaptation."),
        ("Strict Grid Table Layout", "Pixel-perfect 44px rows with zero vertical detachment; aligned columns for User ID, Name, Role, Quizzes, Avg Score, Pass Rate, Flags."),
        ("Theme & Accessibility", "Toggle between Warm Cream Mode and High-Contrast Dark Mode; dynamic font scaling buttons (A+/A-) and Focus Mode."),
        ("Test Suite Verification", "python -m pytest tests/ (All 22 unit tests passing).")
    ]
    for dt, dd in d_points:
        pd = tf_d.add_paragraph()
        pd.text = f"• {dt}:"
        pd.font.bold = True
        pd.font.size = Pt(10)
        pd.font.color.rgb = TEXT_LIGHT
        pd.space_before = Pt(4)
        pdd = tf_d.add_paragraph()
        pdd.text = f"  {dd}"
        pdd.font.size = Pt(9)
        pdd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 11: Summary & Conclusion
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_background(s11)
    add_header(s11, "Review 1 Deliverables Summary & Next Steps")

    summ_cards = [
        ("REVIEW 1 DELIVERABLES MET", ACCENT_GREEN, [
            "✔ Problem Statement & Quality Objectives formalized",
            "✔ IEEE 830 Software Requirements Specification (SRS)",
            "✔ Role-Based Access Control (Student, Faculty, Admin)",
            "✔ Decoupled Modular Folder Architecture",
            "✔ Complete Database Design with SQLite Persistence",
            "✔ All CRUD Operations implemented and tested",
            "✔ Working Web & Desktop Applications verified"
        ]),
        ("VERIFIED QUALITY METRICS", ACCENT_BLUE, [
            "✔ Sub-250ms submission and grading target exceeded (~25ms)",
            "✔ 100% deterministic grading accuracy",
            "✔ Active Anti-Cheat window blur detection active",
            "✔ Hourly automated database snapshot engine in backups/",
            "✔ 22 of 22 automated Pytest unit tests passing cleanly"
        ]),
        ("ROADMAP FOR REVIEW 2", ACCENT_PURPLE, [
            "➡ Biometric identity verification & live webcam proctoring",
            "➡ Offline synchronization queue for intermittent connections",
            "➡ Enhanced graphical SQC analytics charts (Pareto, p-charts)",
            "➡ Multi-section test scheduling with automated release windows"
        ])
    ]

    for i, (title, col, pts) in enumerate(summ_cards):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s11, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s11.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(10)

        for pt in pts:
            pp = tf.add_paragraph()
            pp.text = pt
            pp.font.size = Pt(9.5)
            pp.font.color.rgb = TEXT_LIGHT
            pp.space_before = Pt(4)

    output_path = os.path.abspath("QuizSphere_Review_1_Presentation.pptx")
    prs.save(output_path)
    print(f"Presentation saved successfully to: {output_path}")

if __name__ == "__main__":
    create_deck()
