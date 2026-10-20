"""
Generate a professional, high-impact PowerPoint presentation (.pptx)
for Review 1: Setup & SRS (Online Quiz System - QuizSphere Pro).
Includes comprehensive Software Requirements Specification (SRS) and
Working Application Demo Guide slides.
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def create_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions (13.333" x 7.5")
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Harmonious Design Palette
    BG_COLOR = RGBColor(15, 23, 42)         # #0f172a Dark Slate Navy
    CARD_BG = RGBColor(30, 41, 59)          # #1e293b Container Slate
    CARD_BORDER = RGBColor(51, 65, 85)      # #334155
    ACCENT_BLUE = RGBColor(59, 130, 246)    # #3b82f6 Primary Electric Blue
    ACCENT_GREEN = RGBColor(16, 185, 129)   # #10b981 Emerald
    ACCENT_AMBER = RGBColor(245, 158, 11)   # #f59e0b Warm Amber
    ACCENT_PURPLE = RGBColor(139, 92, 246)  # #8b5cf6 Royal Violet
    ACCENT_CYAN = RGBColor(14, 165, 233)    # #0ea5e9 Cyan
    ACCENT_RED = RGBColor(239, 68, 68)      # #ef4444 Crimson
    TEXT_LIGHT = RGBColor(255, 255, 255)    # Pure White
    TEXT_MUTED = RGBColor(203, 213, 225)    # #cbd5e1 Light Slate
    TEXT_DIM = RGBColor(148, 163, 184)      # #94a3b8 Slate Dim

    def apply_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
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

    banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(2.2), Inches(0.35))
    banner.fill.solid()
    banner.fill.fore_color.rgb = ACCENT_BLUE
    banner.line.fill.background()
    p_b = banner.text_frame.paragraphs[0]
    p_b.text = "ACADEMIC REVIEW 1"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = TEXT_LIGHT
    p_b.alignment = PP_ALIGN.CENTER

    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.5), Inches(1.5))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Online Quiz System (QuizSphere Pro)"
    p1.font.size = Pt(36)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_LIGHT

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Setup & Software Requirements Specification (SRS) with Working Demo"
    p1_sub.font.size = Pt(20)
    p1_sub.font.color.rgb = ACCENT_BLUE
    p1_sub.space_before = Pt(8)

    cards_data = [
        ("Course & Baseline", "BBAT104: Fundamentals of TQM\nBaseline System 9: Online Quiz System", ACCENT_BLUE),
        ("Assigned Quality Goal", "Q20: Overall Software Quality\nDashboards, Validation, Export & Backups", ACCENT_GREEN),
        ("Engineering Target", "Zero-Latency Submissions (<250ms)\n100% Deterministic Auto-Grading", ACCENT_AMBER),
        ("Dual Platform Deployment", "FastAPI Unified Web Backend + SPA\nNative CustomTkinter Desktop Client", ACCENT_PURPLE)
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

    add_card(s2, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), stripe_color=ACCENT_RED)
    b2_left = s2.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf2_l = b2_left.text_frame
    tf2_l.word_wrap = True
    
    p = tf2_l.paragraphs[0]
    p.text = "CRITICAL LIMITATIONS IN EXISTING SYSTEMS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
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
    # SLIDE 5: SRS Overview & IEEE 830 Architecture
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_header(s5, "Software Requirements Specification (SRS) — Architecture & Scope")

    srs_cards = [
        ("IEEE 830 STANDARD STRUCTURE", ACCENT_BLUE, [
            "Formal specification covering Functional & Non-Functional criteria",
            "Document: docs/SRS_Document.md (Version 1.0.0)",
            "Multi-tenant data isolation and audit trails",
            "Integration with TQM Q20 (Overall Software Quality mandate)"
        ]),
        ("SYSTEM BOUNDARIES & ACTORS", ACCENT_GREEN, [
            "Primary Actors: Students (Examinees), Faculty (Examiners), Admins",
            "Client Channels: Web Browser (HTML5/CSS3) & Windows Desktop GUI",
            "Communication: High-throughput JSON REST APIs + WebSockets",
            "Storage Engine: Transactional ACID-compliant SQLite instance"
        ]),
        ("POKA-YOKE MISTAKE PROOFING", ACCENT_AMBER, [
            "Validation Layer: Eliminates malformed question inputs and bad boundaries",
            "Schema Guards: Pydantic v2 strict models for all request bodies",
            "Join Code Integrity: Unique constraint locks preventing collisions",
            "Deterministic State: In-memory evaluation removing race conditions"
        ])
    ]

    for i, (title, col, items) in enumerate(srs_cards):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s5, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s5.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(10)

        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"• {it}"
            pi.font.size = Pt(10)
            pi.font.color.rgb = TEXT_LIGHT
            pi.space_before = Pt(6)

    # ==========================================
    # SLIDE 6: SRS Functional Requirements Matrix
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_background(s6)
    add_header(s6, "SRS: Functional Requirements Matrix (FR-1 to FR-5)")

    frs = [
        ("FR-1: Multi-Role Dashboards", "Segregated workspaces for Student, Faculty, and Admin with dynamic navigation visibility based on authenticated role.", ACCENT_BLUE),
        ("FR-2: Poka-Yoke Input Validation", "Strict bounds checking on quiz limits (1-180m, 1-100%), non-empty options, and unique constraint enforcement on Join Codes.", ACCENT_GREEN),
        ("FR-3: AI Question Synthesis", "Automated MCQ synthesis based on syllabus topic and difficulty (Beginner, Medium, Advanced) with deterministic answer keys.", ACCENT_AMBER),
        ("FR-4: Automated Gradebook & Export", "Instant candidate scorecard delivery with per-question review and one-click streaming CSV exports for rosters and attempts.", ACCENT_PURPLE),
        ("FR-5: Automated Database Backups", "Dedicated backup utility creating timestamped SQLite snapshots in backups/ directory with on-demand snapshot triggers.", ACCENT_CYAN)
    ]

    for i, (f_title, f_desc, col) in enumerate(frs):
        row = i // 3
        col_idx = i % 3
        c_left = Inches(0.8 + col_idx * 3.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s6, c_left, c_top, Inches(3.8), Inches(2.35), stripe_color=col)
        box = s6.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(3.4), Inches(2.0))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = f_title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(6)

        pd = tf.add_paragraph()
        pd.text = f_desc
        pd.font.size = Pt(9.5)
        pd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 7: SRS Non-Functional Requirements & Security
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_background(s7)
    add_header(s7, "SRS: Non-Functional Requirements & Security Safeguards")

    nfrs = [
        ("SUB-250MS DETERMINISTIC SPEED", ACCENT_BLUE, [
            "In-memory evaluation pipeline yields immediate grading without blocking I/O",
            "Benchmark: 15 to 35 milliseconds turnaround per 50-question test",
            "Zero client-side grading drift or race condition vulnerabilities"
        ]),
        ("ACID TRANSACTION GUARANTEE", ACCENT_GREEN, [
            "Atomic SQLite write transactions protect test records from corrupt state",
            "Automatic database migrations on boot via FastAPI lifespan handlers",
            "Zero startup deprecation warnings across all endpoints"
        ]),
        ("ACTIVE PROCTORING & INTEGRITY", ACCENT_RED, [
            "Window blur & tab switch listeners capture unauthorized browser browsing",
            "Infraction tally permanently attached to candidate attempt record",
            "Authoritative server-side countdown timer preventing client manipulation"
        ]),
        ("THEMING & ACCESSIBILITY", ACCENT_PURPLE, [
            "Warm Cream Modern Theme + High-Contrast Dark Mode",
            "Dynamic font scaling controls (A+/A-) for laboratory accessibility",
            "Focus Mode minimizing visual clutter during high-stakes assessments"
        ])
    ]

    for i, (title, col, items) in enumerate(nfrs):
        row = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * 5.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s7, c_left, c_top, Inches(5.7), Inches(2.35), stripe_color=col)
        box = s7.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(5.3), Inches(2.0))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(4)

        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"▪ {it}"
            pi.font.size = Pt(9.5)
            pi.font.color.rgb = TEXT_LIGHT
            pi.space_before = Pt(2)

    # ==========================================
    # SLIDE 8: Modular Folder Architecture
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_background(s8)
    add_header(s8, "Modular Folder Architecture & Technology Stack")

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
        add_card(s8, c_left, c_top, Inches(5.7), Inches(2.35), stripe_color=col)
        box = s8.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(5.3), Inches(2.0))
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
    # SLIDE 9: Core Modules Breakdown
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_background(s9)
    add_header(s9, "Core Modules & Feature Breakdown")

    modules = [
        ("M1: Identity & Authentication", "Role-based sign-in and registration for Student, Faculty, and Admin. Dynamically alters client navigation tabs according to authenticated persona.", ACCENT_BLUE),
        ("M2: Examiner Studio & AI Wizard", "Faculty test creator supporting manual MCQ authoring or AI syllabus synthesis. Configures duration, passing score, category, and deterministic 6-character Join Code.", ACCENT_GREEN),
        ("M3: Candidate Assessment Arena", "Quick test join via code. Delivers questions with interactive palette, authoritative server countdown timer, and automatic submission upon deadline expiry.", ACCENT_AMBER),
        ("M4: Anti-Cheat Proctoring Hub", "Active focus tracking monitors window blur and tab switching during exams. Violations increment in real time and are permanently audited into submission records.", ACCENT_RED),
        ("M5: Zero-Latency Auto-Grading", "In-memory evaluation engine compares answers against key in ~25ms. Displays immediate percentage, pass/fail status, and per-question rationale explanations.", ACCENT_PURPLE),
        ("M6: Admin Governance & Telemetry", "Platform telemetry KPIs, filterable user roster, candidate performance scorecard drill-down modal, and instant one-click CSV export streams.", ACCENT_CYAN)
    ]

    for i, (m_title, m_desc, col) in enumerate(modules):
        row = i // 3
        col_idx = i % 3
        c_left = Inches(0.8 + col_idx * 3.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s9, c_left, c_top, Inches(3.8), Inches(2.35), stripe_color=col)
        box = s9.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.2), Inches(3.4), Inches(1.95))
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
    # SLIDE 10: Database & System Design
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_background(s10)
    add_header(s10, "Database & System Design (ACID SQLite Persistence)")

    tables = [
        ("TABLE: users", "id (PK), username (UNIQUE), password, role, full_name, department, created_at", ACCENT_BLUE),
        ("TABLE: quizzes", "id (PK), join_code (UNIQUE), teacher_name, title, category, duration_minutes, passing_score, tags, questions_json, created_at", ACCENT_GREEN),
        ("TABLE: attempts", "id (PK), quiz_id (FK), join_code, quiz_title, teacher_name, student_name, score, total_questions, percentage, passed, cheat_violations, submitted_at", ACCENT_PURPLE)
    ]

    for i, (t_name, t_schema, col) in enumerate(tables):
        top_pos = Inches(1.8 + i * 1.65)
        add_card(s10, Inches(0.8), top_pos, Inches(6.8), Inches(1.5), stripe_color=col)
        box = s10.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.15), Inches(6.4), Inches(1.2))
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

    add_card(s10, Inches(7.8), Inches(1.8), Inches(4.7), Inches(4.8), stripe_color=ACCENT_AMBER)
    r_box = s10.shapes.add_textbox(Inches(8.0), Inches(2.0), Inches(4.3), Inches(4.4))
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
    # SLIDE 11: CRUD Operations Matrix
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_background(s11)
    add_header(s11, "CRUD Operations Aligned with Quality Goals")

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
        add_card(s11, c_left, c_top, Inches(5.7), Inches(2.35), stripe_color=col)
        box = s11.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(5.3), Inches(2.0))
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
    # SLIDE 12: Working App Demo Guide — Setup & Credentials
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    apply_background(s12)
    add_header(s12, "Working Application Demo Guide — Setup & Test Credentials")

    # Left: Startup Commands
    add_card(s12, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), stripe_color=ACCENT_BLUE)
    box_s12l = s12.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_s12l = box_s12l.text_frame
    tf_s12l.word_wrap = True

    p = tf_s12l.paragraphs[0]
    p.text = "EXECUTION & VERIFICATION COMMANDS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    exec_cmds = [
        ("1. Launch Web Server", "python server.py\nBinds to http://localhost:8000 with real-time reload & lifespan initialization."),
        ("2. Launch Desktop GUI", "python desktop_app.py\nNative Windows CustomTkinter application with strict grid alignment."),
        ("3. Run Test Suite", "python -m pytest tests/ -v\nRuns all 22 automated tests verifying auth, join codes, and admin analytics.")
    ]
    for c_title, c_desc in exec_cmds:
        pc = tf_s12l.add_paragraph()
        pc.text = f"▶ {c_title}:"
        pc.font.bold = True
        pc.font.size = Pt(10.5)
        pc.font.color.rgb = TEXT_LIGHT
        pc.space_before = Pt(6)

        pcd = tf_s12l.add_paragraph()
        pcd.text = f"   {c_desc}"
        pcd.font.size = Pt(9.5)
        pcd.font.color.rgb = TEXT_MUTED

    # Right: Test Accounts Table
    add_card(s12, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    box_s12r = s12.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf_s12r = box_s12r.text_frame
    tf_s12r.word_wrap = True

    p = tf_s12r.paragraphs[0]
    p.text = "READY-TO-USE TEST ACCOUNTS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)

    accounts = [
        ("STUDENT ROLE", "student", "student123", "Alex Mercer", "Candidate Arena: Join assessment via code 'QZ-1001', test anti-cheat, instant scorecard.", ACCENT_BLUE),
        ("FACULTY ROLE", "faculty", "faculty123", "Prof. Alan Turing", "Examiner Studio: Manual quiz builder, AI quiz generator, class submission gradebook.", ACCENT_GREEN),
        ("ADMIN ROLE", "admin", "admin123", "System Administrator", "Platform Admin: Global telemetry KPIs, candidate history modal, and CSV exports.", ACCENT_PURPLE)
    ]
    for role_h, uname, pwd, name, desc, col in accounts:
        pa = tf_s12r.add_paragraph()
        pa.text = f"👤 {role_h} — {name} ({col.rgb if hasattr(col, 'rgb') else ''})"
        pa.font.bold = True
        pa.font.size = Pt(10)
        pa.font.color.rgb = col
        pa.space_before = Pt(6)

        pad = tf_s12r.add_paragraph()
        pad.text = f"   Login: {uname}  |  Password: {pwd}"
        pad.font.size = Pt(9.5)
        pad.font.bold = True
        pad.font.color.rgb = TEXT_LIGHT

        pad2 = tf_s12r.add_paragraph()
        pad2.text = f"   Purpose: {desc}"
        pad2.font.size = Pt(9)
        pad2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 13: Live Demonstration Workflows
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    apply_background(s13)
    add_header(s13, "Live Demonstration Walkthroughs (Student, Faculty, Admin)")

    flows = [
        ("SCENARIO 1: STUDENT EXAMINATION", ACCENT_BLUE, [
            "1. Sign in as student / student123; navigation tabs restrict to Candidate Arena",
            "2. Enter active Join Code 'QZ-1001' and launch assessment",
            "3. Answer questions while authoritative countdown timer runs",
            "4. Switch browser tabs to trigger live Anti-Cheat violation alert",
            "5. Submit test; zero-latency auto-grading delivers scorecard in ~25ms"
        ]),
        ("SCENARIO 2: FACULTY STUDIO & AI", ACCENT_GREEN, [
            "1. Sign in as faculty / faculty123; Examiner Studio is front and center",
            "2. Open AI Question Generator, enter topic 'Data Structures', click Generate",
            "3. Set passing score to 70%, 15m duration, click Publish Quiz",
            "4. System creates new 6-char Join Code (e.g. QZ-3942)",
            "5. Open Class Gradebook to inspect student attempts and proctor violation counts"
        ]),
        ("SCENARIO 3: ADMIN GOVERNANCE", ACCENT_PURPLE, [
            "1. Sign in as admin / admin123; open Platform Administration Console",
            "2. Inspect high-level KPIs (Total accounts, candidates, faculty, violations)",
            "3. Filter user roster table by role or search string 'Alex Mercer'",
            "4. Click 'View Report' on candidate to open historical performance modal",
            "5. Click 'Export Roster CSV' & 'Export Submissions CSV' for audit reports"
        ])
    ]

    for i, (title, col, steps) in enumerate(flows):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s13, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s13.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True

        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(10)

        for step in steps:
            ps = tf.add_paragraph()
            ps.text = step
            ps.font.size = Pt(9.5)
            ps.font.color.rgb = TEXT_LIGHT
            ps.space_before = Pt(5)

    # ==========================================
    # SLIDE 14: Review 1 Deliverables Summary
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    apply_background(s14)
    add_header(s14, "Review 1 Deliverables Summary & Next Steps")

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
        add_card(s14, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s14.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
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
