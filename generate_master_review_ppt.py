"""
Generate a complete Master PowerPoint Presentation (.pptx)
incorporating all Review 1 and Review 2 topics, following the exact
TQM Quality + Process methodology from the course syllabus:
- Vision, Mission, Quality Objectives
- Three Quality Ideas (Error prevention at source, Process control, Monitoring)
- Process Map with sitting controls
- SIPOC Process Map
- Stakeholders and their needs
- Measurable Requirements (Viva) & Objectives (O1-O5)
- Assigned Quality Goal Q20 (5 features built)
- Feature -> Quality Idea mapping & Crucial Viva mapping
- One-line viva
- Architecture CASE: Folder structure & what each folder means
- The one rule to remember: UI never talks directly to DB
- What each file does (start, config, database, models, services, ui, reports, utils)
- How a click uses these files
- Database design & real table examples (users, quizzes, attempts, audit_logs, error_logs)
- Why migrations matter
- Software feature -> TQM concept mapping
- Quality Dashboard
- Pareto Chart (80/20 rule)
- Fishbone (Ishikawa) Diagram
- FMEA Matrix & How logs feed FMEA
- PDCA Continuous Improvement Cycle
- Review 1 vs Review 2 Roadmap
- Working Application Demo Guide & Step-by-step Walkthroughs
- One sentence for viva
"""

import os
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.dml.color import RGBColor
from pptx.enum.text import PP_ALIGN
from pptx.enum.shapes import MSO_SHAPE

def build_master_deck():
    prs = Presentation()
    # 16:9 Widescreen dimensions (13.333" x 7.5")
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    blank_layout = prs.slide_layouts[6]

    # Professional TQM Theme Colors
    BG_COLOR = RGBColor(15, 23, 42)         # #0f172a Dark Slate Navy
    CARD_BG = RGBColor(30, 41, 59)          # #1e293b Slate Container
    CARD_BORDER = RGBColor(51, 65, 85)      # #334155 Border
    ACCENT_BLUE = RGBColor(59, 130, 246)    # #3b82f6 Primary Blue
    ACCENT_GREEN = RGBColor(16, 185, 129)   # #10b981 Emerald Green
    ACCENT_AMBER = RGBColor(245, 158, 11)   # #f59e0b Amber Accent
    ACCENT_PURPLE = RGBColor(139, 92, 246)  # #8b5cf6 Purple Accent
    ACCENT_CYAN = RGBColor(14, 165, 233)    # #0ea5e9 Sky Cyan
    ACCENT_RED = RGBColor(239, 68, 68)      # #ef4444 Crimson
    TEXT_LIGHT = RGBColor(255, 255, 255)    # White
    TEXT_MUTED = RGBColor(203, 213, 225)    # #cbd5e1 Light Slate
    TEXT_DIM = RGBColor(148, 163, 184)      # #94a3b8 Dim Slate

    def apply_background(slide):
        bg = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, 0, 0, prs.slide_width, prs.slide_height)
        bg.fill.solid()
        bg.fill.fore_color.rgb = BG_COLOR
        bg.line.fill.background()
        return bg

    def add_header(slide, title_text, category_text="SRS REVIEW 1 & 2 · PROCESS + QUALITY", slide_num=None):
        sub_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(11.7), Inches(0.4))
        tf_sub = sub_box.text_frame
        tf_sub.word_wrap = True
        p_sub = tf_sub.paragraphs[0]
        p_sub.text = category_text.upper()
        p_sub.font.size = Pt(11)
        p_sub.font.bold = True
        p_sub.font.color.rgb = ACCENT_BLUE

        title_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.7), Inches(11.7), Inches(0.8))
        tf = title_box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title_text
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT

        if slide_num:
            num_box = slide.shapes.add_textbox(Inches(12.0), Inches(0.4), Inches(0.8), Inches(0.4))
            p_n = num_box.text_frame.paragraphs[0]
            p_n.text = str(slide_num)
            p_n.font.size = Pt(11)
            p_n.font.color.rgb = TEXT_DIM
            p_n.alignment = PP_ALIGN.RIGHT

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
    # SLIDE 1: Title Slide (Matches PDF Slide 1)
    # ==========================================
    s1 = prs.slides.add_slide(blank_layout)
    apply_background(s1)

    banner = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), Inches(1.2), Inches(3.2), Inches(0.35))
    banner.fill.solid()
    banner.fill.fore_color.rgb = ACCENT_BLUE
    banner.line.fill.background()
    p_b = banner.text_frame.paragraphs[0]
    p_b.text = "SRS REVIEW 1 & 2 · PROCESS + QUALITY"
    p_b.font.size = Pt(10)
    p_b.font.bold = True
    p_b.font.color.rgb = TEXT_LIGHT
    p_b.alignment = PP_ALIGN.CENTER

    t_box = s1.shapes.add_textbox(Inches(0.8), Inches(1.7), Inches(11.5), Inches(1.8))
    tf1 = t_box.text_frame
    tf1.word_wrap = True
    p1 = tf1.paragraphs[0]
    p1.text = "Process map, stakeholders,\nmeasurable requirements, quality goals"
    p1.font.size = Pt(32)
    p1.font.bold = True
    p1.font.color.rgb = TEXT_LIGHT

    p1_sub = tf1.add_paragraph()
    p1_sub.text = "Online Quiz System (QuizSphere Pro) — Baseline System 9\nQ20: Overall Software Quality & Zero-Latency Submissions"
    p1_sub.font.size = Pt(18)
    p1_sub.font.color.rgb = ACCENT_BLUE
    p1_sub.space_before = Pt(8)

    cards_data_s1 = [
        ("Course & Baseline", "BBAT104: Fundamentals of TQM\nBaseline System 9: Online Quiz System", ACCENT_BLUE),
        ("Assigned Quality Goal", "Q20: Overall Software Quality\nDashboards, Validation, Export & Backups", ACCENT_GREEN),
        ("Core Objective", "Zero-Latency Evaluation (<250ms)\n100% Deterministic Auto-Grading", ACCENT_AMBER),
        ("Architecture", "FastAPI REST/WebSocket Backend\nNative CustomTkinter Desktop Client", ACCENT_PURPLE)
    ]
    for i, (head, val, col) in enumerate(cards_data_s1):
        c_left = Inches(0.8 + i * 2.95)
        add_card(s1, c_left, Inches(4.0), Inches(2.8), Inches(2.2), stripe_color=col)
        box = s1.shapes.add_textbox(c_left + Inches(0.15), Inches(4.2), Inches(2.5), Inches(1.8))
        tf = box.text_frame
        tf.word_wrap = True
        ph = tf.paragraphs[0]
        ph.text = head.upper()
        ph.font.size = Pt(10)
        ph.font.bold = True
        ph.font.color.rgb = col
        ph.space_after = Pt(6)
        pv = tf.add_paragraph()
        pv.text = val
        pv.font.size = Pt(11)
        pv.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 2: Vision, mission, quality objective (Matches PDF Slide 2)
    # ==========================================
    s2 = prs.slides.add_slide(blank_layout)
    apply_background(s2)
    add_header(s2, "Vision, mission, quality objective", slide_num=2)

    s2_sections = [
        ("VISION", "An examination environment where zero unrecorded answers, zero grading latency, and zero undetected academic infractions occur.", ACCENT_BLUE),
        ("MISSION", "Build a high-performance assessment system (Web & Desktop) that records student attempts, blocks cheating via active proctoring, auto-grades in <250ms, and shows who did what.", ACCENT_GREEN),
        ("QUALITY OBJECTIVE OF THIS SOFTWARE", "Prevent the error at the source (Poka-yoke).\nControl the examination process.\nMonitor every attempt and infraction with logs.", ACCENT_AMBER)
    ]
    for i, (title, content, col) in enumerate(s2_sections):
        top_pos = Inches(1.8 + i * 1.65)
        add_card(s2, Inches(0.8), top_pos, Inches(11.7), Inches(1.45), stripe_color=col)
        box = s2.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.15), Inches(11.1), Inches(1.15))
        tf = box.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = title
        pt.font.size = Pt(11)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(4)
        pc = tf.add_paragraph()
        pc.text = content
        pc.font.size = Pt(14 if i == 2 else 13)
        pc.font.bold = (i == 2)
        pc.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 3: Three quality ideas behind the software (Matches PDF Slide 3)
    # ==========================================
    s3 = prs.slides.add_slide(blank_layout)
    apply_background(s3)
    add_header(s3, "Three quality ideas behind the software", slide_num=3)

    q_ideas = [
        ("Error prevention at source", "Poka-yoke", [
            "Blank question prompt blocked.",
            "Missing correct choice blocked.",
            "Duration <= 0 or >180m blocked.",
            "Duplicate Join Code blocked."
        ], ACCENT_BLUE),
        ("Process control", "One path for work", [
            "Quiz Authoring → Join Code",
            "→ Timed Exam → Scorecard.",
            "UI cannot skip rules.",
            "Student cannot bypass countdown."
        ], ACCENT_GREEN),
        ("Monitoring", "See and trace", [
            "Dashboard KPI alerts.",
            "Proctor infraction audit log.",
            "Student attempt telemetry.",
            "Error log → FMEA integration."
        ], ACCENT_PURPLE)
    ]
    for i, (title, sub, items, col) in enumerate(q_ideas):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s3, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s3.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        ps = tf.add_paragraph()
        ps.text = sub
        ps.font.size = Pt(11)
        ps.font.color.rgb = TEXT_MUTED
        ps.space_after = Pt(12)
        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"• {it}"
            pi.font.size = Pt(11)
            pi.font.color.rgb = TEXT_LIGHT
            pi.space_before = Pt(8)

    # ==========================================
    # SLIDE 4: Process map & Controls sitting on this process (Matches PDF Slide 4)
    # ==========================================
    s4 = prs.slides.add_slide(blank_layout)
    apply_background(s4)
    add_header(s4, "Process map & controls sitting on this process", slide_num=4)

    # Top: Process Map Pipeline Boxes
    p_steps = ["Teacher", "Quiz Creation", "Join Code", "Student", "Exam Execution", "Report"]
    for i, step in enumerate(p_steps):
        s_left = Inches(0.8 + i * 1.95)
        box = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, s_left, Inches(1.8), Inches(1.8), Inches(0.75))
        box.fill.solid()
        box.fill.fore_color.rgb = CARD_BG
        box.line.color.rgb = ACCENT_BLUE
        p = box.text_frame.paragraphs[0]
        p.text = step
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT
        p.alignment = PP_ALIGN.CENTER

    # Subtitle
    sub_t = s4.shapes.add_textbox(Inches(0.8), Inches(2.75), Inches(11.7), Inches(0.4))
    p = sub_t.text_frame.paragraphs[0]
    p.text = "Controls sitting on this process"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER

    # 4 Control Cards (2x2 grid)
    ctrls = [
        ("On Quiz Creation", "Title, passing score (1-100%), duration, and question choices must be valid.", ACCENT_BLUE),
        ("On Join Code", "Normalization to uppercase, SQL uniqueness check, sub-25ms resolution.", ACCENT_GREEN),
        ("On Exam Execution", "Authoritative server timer countdown + window blur focus loss tracking.", ACCENT_RED),
        ("On Report / Submission", "Measure latency (<250ms), grade deterministically, and record cheat flags.", ACCENT_PURPLE)
    ]
    for i, (c_name, c_desc, col) in enumerate(ctrls):
        row = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * 5.95)
        c_top = Inches(3.3 + row * 1.8)
        add_card(s4, c_left, c_top, Inches(5.7), Inches(1.6), stripe_color=col)
        box = s4.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(5.3), Inches(1.3))
        tf = box.text_frame
        tf.word_wrap = True
        pt = tf.paragraphs[0]
        pt.text = c_name
        pt.font.size = Pt(12)
        pt.font.bold = True
        pt.font.color.rgb = col
        pt.space_after = Pt(4)
        pd = tf.add_paragraph()
        pd.text = c_desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 5: SIPOC of the examination process (Matches PDF Slide 5)
    # ==========================================
    s5 = prs.slides.add_slide(blank_layout)
    apply_background(s5)
    add_header(s5, "SIPOC of the examination process", slide_num=5)

    sipoc_cols = [
        ("S (Suppliers)", ["Teacher / Faculty", "Curriculum SME", "AI Engine", "Database"], ACCENT_BLUE),
        ("I (Inputs)", ["Question Prompts", "Answer Key", "Duration Bounds", "Candidate Code"], ACCENT_GREEN),
        ("P (Process)", ["Validate Entry", "Generate Code", "Host Timed Exam", "Track Window Blur", "Auto-grade & Save"], ACCENT_AMBER),
        ("O (Outputs)", ["Instant Scorecard", "Question Breakdown", "Class Gradebook", "Violation Audit Log"], ACCENT_PURPLE),
        ("C (Customers)", ["Student / Examinee", "Teacher / Examiner", "System Admin", "Academic Auditor"], ACCENT_CYAN)
    ]
    for i, (col_head, items, col) in enumerate(sipoc_cols):
        c_left = Inches(0.8 + i * 2.36)
        add_card(s5, c_left, Inches(1.8), Inches(2.25), Inches(4.9), stripe_color=col)
        box = s5.shapes.add_textbox(c_left + Inches(0.15), Inches(2.0), Inches(1.95), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = col_head
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(12)
        for it in items:
            pi = tf.add_paragraph()
            pi.text = f"• {it}"
            pi.font.size = Pt(10)
            pi.font.color.rgb = TEXT_LIGHT
            pi.space_before = Pt(6)

    # ==========================================
    # SLIDE 6: Stakeholders and their need (Matches PDF Slide 6)
    # ==========================================
    s6 = prs.slides.add_slide(blank_layout)
    apply_background(s6)
    add_header(s6, "Stakeholders and their need", slide_num=6)

    stakeholders = [
        ("Student / Candidate", "Zero latency during submission. Transparent scorecard. Fair timer.", ACCENT_BLUE),
        ("Teacher / Examiner", "Fast quiz creation (manual & AI). Quick join code. Live class gradebook.", ACCENT_GREEN),
        ("Administrator / Owner", "User governance, platform telemetry numbers, CSV audit exports.", ACCENT_PURPLE),
        ("Academic Auditor", "Who submitted what, exact timestamps, and proctoring violation logs.", ACCENT_AMBER),
        ("Institution", "Zero exam downtime. High academic integrity. Automated database backups.", ACCENT_CYAN)
    ]
    for i, (s_name, s_need, col) in enumerate(stakeholders):
        top_pos = Inches(1.8 + i * 0.98)
        # Left label card
        add_card(s6, Inches(0.8), top_pos, Inches(3.2), Inches(0.85), stripe_color=col)
        b_left = s6.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.15), Inches(2.9), Inches(0.6))
        p = b_left.text_frame.paragraphs[0]
        p.text = s_name
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        # Right need card
        add_card(s6, Inches(4.2), top_pos, Inches(8.3), Inches(0.85))
        b_right = s6.shapes.add_textbox(Inches(4.4), top_pos + Inches(0.15), Inches(7.9), Inches(0.6))
        p = b_right.text_frame.paragraphs[0]
        p.text = s_need
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 7: Measurable requirements (viva) (Matches PDF Slide 7)
    # ==========================================
    s7 = prs.slides.add_slide(blank_layout)
    apply_background(s7)
    add_header(s7, "Measurable requirements (viva)", slide_num=7)

    sub_t = s7.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.35))
    p = sub_t.text_frame.paragraphs[0]
    p.text = "Need → number we can count"
    p.font.size = Pt(12)
    p.font.color.rgb = ACCENT_AMBER

    req_rows = [
        ("Zero lost submissions", "Submission loss count = 0 (100% recorded)"),
        ("Zero grading latency", "Submission turnaround time < 250 ms (achieved ~25 ms)"),
        ("100% grading accuracy", "Score calculation consistency = 100.0% (Zero Defect)"),
        ("Trace academic dishonesty", "100% of window/tab switches logged with timestamp"),
        ("Find assessment fast", "Join Code resolution time < 25 milliseconds"),
        ("Protect institutional data", "Hourly automated database snapshot in backups/ = 100%")
    ]
    for i, (need, num) in enumerate(req_rows):
        top_pos = Inches(1.85 + i * 0.85)
        add_card(s7, Inches(0.8), top_pos, Inches(5.6), Inches(0.72))
        bl = s7.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.12), Inches(5.2), Inches(0.5))
        p = bl.text_frame.paragraphs[0]
        p.text = need
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT

        add_card(s7, Inches(6.6), top_pos, Inches(5.9), Inches(0.72), stripe_color=ACCENT_GREEN)
        br = s7.shapes.add_textbox(Inches(6.8), top_pos + Inches(0.12), Inches(5.5), Inches(0.5))
        p = br.text_frame.paragraphs[0]
        p.text = num
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN

    # ==========================================
    # SLIDE 8: Measurable quality objectives (O1 to O5) (Matches PDF Slide 8)
    # ==========================================
    s8 = prs.slides.add_slide(blank_layout)
    apply_background(s8)
    add_header(s8, "Measurable quality objectives", slide_num=8)

    objs = [
        ("O1", "Zero lost submissions on any student attempt under peak concurrency.", ACCENT_BLUE),
        ("O2", "Every test submission either saves fully (ACID) or not at all.", ACCENT_GREEN),
        ("O3", "Every user action and proctoring violation is captured in audit logs.", ACCENT_AMBER),
        ("O4", "Automated database backup file created at least once a day.", ACCENT_PURPLE),
        ("O5", "Login and code validation fail safely. App does not crash.", ACCENT_CYAN)
    ]
    for i, (code, text, col) in enumerate(objs):
        top_pos = Inches(1.8 + i * 0.98)
        add_card(s8, Inches(0.8), top_pos, Inches(1.2), Inches(0.85), stripe_color=col)
        bl = s8.shapes.add_textbox(Inches(0.8), top_pos + Inches(0.15), Inches(1.2), Inches(0.6))
        p = bl.text_frame.paragraphs[0]
        p.text = code
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER

        add_card(s8, Inches(2.2), top_pos, Inches(10.3), Inches(0.85))
        br = s8.shapes.add_textbox(Inches(2.5), top_pos + Inches(0.15), Inches(9.8), Inches(0.6))
        p = br.text_frame.paragraphs[0]
        p.text = text
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 9: Assigned quality goal Q20 (Matches PDF Slide 9)
    # ==========================================
    s9 = prs.slides.add_slide(blank_layout)
    apply_background(s9)
    add_header(s9, "Assigned quality goal Q20: Overall Software Quality", slide_num=9)

    sub_t = s9.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.35))
    p = sub_t.text_frame.paragraphs[0]
    p.text = "Overall Software Quality — five features we built"
    p.font.size = Pt(12)
    p.font.color.rgb = ACCENT_AMBER

    q20_features = [
        ("Auto Backup", "Automated timestamped copy of quiz_system.db saved in backups/.", ACCENT_BLUE),
        ("Audit Log", "User ID, action, join code, score, cheat violation tally, submission time.", ACCENT_GREEN),
        ("Input Validation", "Poka-yoke prevents blank questions, negative limits, duplicate codes.", ACCENT_AMBER),
        ("Error Recovery", "ACID transactions: if save fails, show error. No half-graded attempt.", ACCENT_RED),
        ("User Roles", "Student / Faculty / Admin only see their dedicated workflows.", ACCENT_PURPLE)
    ]
    for i, (feat, desc, col) in enumerate(q20_features):
        top_pos = Inches(1.85 + i * 0.98)
        add_card(s9, Inches(0.8), top_pos, Inches(3.2), Inches(0.85), stripe_color=col)
        bl = s9.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.15), Inches(2.9), Inches(0.6))
        p = bl.text_frame.paragraphs[0]
        p.text = feat
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        add_card(s9, Inches(4.2), top_pos, Inches(8.3), Inches(0.85))
        br = s9.shapes.add_textbox(Inches(4.4), top_pos + Inches(0.15), Inches(7.9), Inches(0.6))
        p = br.text_frame.paragraphs[0]
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 10: Feature → quality idea (Matches PDF Slide 10)
    # ==========================================
    s10 = prs.slides.add_slide(blank_layout)
    apply_background(s10)
    add_header(s10, "Feature → quality idea", slide_num=10)

    mappings = [
        ("Input Validation", "Error prevention at source (Poka-yoke)", ACCENT_BLUE),
        ("User Roles", "Process control + accountability", ACCENT_GREEN),
        ("Audit Log & Violation Tracker", "Monitoring + traceability", ACCENT_AMBER),
        ("Error Recovery (ACID)", "Reliability. No broken test submission.", ACCENT_RED),
        ("Auto Backup", "Reliability. Data is never lost.", ACCENT_PURPLE)
    ]
    for i, (feat, q_idea, col) in enumerate(mappings):
        top_pos = Inches(1.8 + i * 0.98)
        add_card(s10, Inches(0.8), top_pos, Inches(4.5), Inches(0.85), stripe_color=col)
        bl = s10.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.15), Inches(4.1), Inches(0.6))
        p = bl.text_frame.paragraphs[0]
        p.text = feat
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        add_card(s10, Inches(5.5), top_pos, Inches(7.0), Inches(0.85))
        br = s10.shapes.add_textbox(Inches(5.7), top_pos + Inches(0.15), Inches(6.6), Inches(0.6))
        p = br.text_frame.paragraphs[0]
        p.text = q_idea
        p.font.size = Pt(12)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 11: Crucial mapping (say this) (Matches PDF Slide 11)
    # ==========================================
    s11 = prs.slides.add_slide(blank_layout)
    apply_background(s11)
    add_header(s11, "Crucial mapping (say this)", slide_num=11)

    crucial_points = [
        ("Customer need:", "Honest, fast, zero-latency assessment.", ACCENT_BLUE),
        ("Measurable requirement:", "Turnaround latency < 250ms, zero lost answers.", ACCENT_GREEN),
        ("Process control:", "Assessment cannot skip proctor check or code validation.", ACCENT_AMBER),
        ("Monitoring:", "Audit log + violation tracker + admin dashboard.", ACCENT_PURPLE),
        ("Quality goal:", "Q20 Overall Software Quality features above.", ACCENT_CYAN)
    ]
    for i, (label, val, col) in enumerate(crucial_points):
        top_pos = Inches(1.8 + i * 0.98)
        add_card(s11, Inches(0.8), top_pos, Inches(11.7), Inches(0.85), stripe_color=col)
        box = s11.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.15), Inches(11.1), Inches(0.6))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.text = f"{label}  "
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col

        p_val = tf.add_paragraph()
        p_val.text = val
        p_val.font.size = Pt(14)
        p_val.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 12: One-line viva (Matches PDF Slide 12)
    # ==========================================
    s12 = prs.slides.add_slide(blank_layout)
    apply_background(s12)
    add_header(s12, "One-line viva", slide_num=12)

    add_card(s12, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    box12 = s12.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(10.9), Inches(4.0))
    tf12 = box12.text_frame
    tf12.word_wrap = True

    p = tf12.paragraphs[0]
    p.text = "Requirement: zero latency, zero cheating undetected."
    p.font.size = Pt(22)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT
    p.space_after = Pt(24)

    p2 = tf12.add_paragraph()
    p2.text = "Objective: submissions graded < 250ms, 100% tab switches logged."
    p2.font.size = Pt(20)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_BLUE
    p2.space_after = Pt(28)

    p3 = tf12.add_paragraph()
    p3.text = "How: validate at entry, control the exam path,\nmonitor with audit and violation logs."
    p3.font.size = Pt(20)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_AMBER

    # ==========================================
    # SLIDE 13: CASE: Online Quiz System (Matches PDF Slide 13)
    # ==========================================
    s13 = prs.slides.add_slide(blank_layout)
    apply_background(s13)
    add_header(s13, "CASE: Online Quiz System Architecture", slide_num=13)

    add_card(s13, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_BLUE)
    box13 = s13.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(4.0))
    tf13 = box13.text_frame
    tf13.word_wrap = True

    p = tf13.paragraphs[0]
    p.text = "Online Quiz System (QuizSphere Pro)"
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(14)

    p2 = tf13.add_paragraph()
    p2.text = "Every folder, every screen, every table.\nSimple enough to explain from the last row."
    p2.font.size = Pt(20)
    p2.font.color.rgb = TEXT_LIGHT
    p2.space_after = Pt(28)

    p3 = tf13.add_paragraph()
    p3.text = "Quality-oriented system  |  Modular design  |  TQM controls"
    p3.font.size = Pt(16)
    p3.font.bold = True
    p3.font.color.rgb = ACCENT_GREEN

    # ==========================================
    # SLIDE 14: What each folder means (Matches PDF Slide 16)
    # ==========================================
    s14 = prs.slides.add_slide(blank_layout)
    apply_background(s14)
    add_header(s14, "What each folder means", slide_num=14)

    folder_meanings = [
        ("ui/", "what the user sees (Web SPA & CustomTkinter Desktop)", ACCENT_BLUE),
        ("services/", "business rules (auth, quiz, grading, proctoring)", ACCENT_GREEN),
        ("models/", "what a User / Quiz / Attempt / Question is", ACCENT_AMBER),
        ("database/", "how data is stored (SQLite connection, schema, migrations)", ACCENT_PURPLE),
        ("reports/", "numbers for decisions (gradebook, telemetry, CSV)", ACCENT_CYAN),
        ("server.py", "starts the program only (FastAPI lifespan, zero raw SQL in UI)", ACCENT_RED)
    ]
    for i, (f_name, f_meaning, col) in enumerate(folder_meanings):
        top_pos = Inches(1.8 + i * 0.82)
        add_card(s14, Inches(0.8), top_pos, Inches(3.0), Inches(0.72), stripe_color=col)
        bl = s14.shapes.add_textbox(Inches(1.0), top_pos + Inches(0.12), Inches(2.6), Inches(0.5))
        p = bl.text_frame.paragraphs[0]
        p.text = f_name
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        add_card(s14, Inches(4.0), top_pos, Inches(8.5), Inches(0.72))
        br = s14.shapes.add_textbox(Inches(4.2), top_pos + Inches(0.12), Inches(8.1), Inches(0.5))
        p = br.text_frame.paragraphs[0]
        p.text = f_meaning
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 15: Why this folder structure? (Matches PDF Slide 17)
    # ==========================================
    s15 = prs.slides.add_slide(blank_layout)
    apply_background(s15)
    add_header(s15, "Why this folder structure?", slide_num=15)

    add_card(s15, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_AMBER)
    box15 = s15.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.9), Inches(4.2))
    tf15 = box15.text_frame
    tf15.word_wrap = True

    why_points = [
        "• One job per folder. Easy to explain.",
        "• A bug in grading does not hide inside server.py or main.py.",
        "• Validation and anti-cheat audit have a dedicated home.",
        "• You can build and test one layer at a time (Pytest unit tests pass independently)."
    ]
    for i, pt in enumerate(why_points):
        p = tf15.paragraphs[0] if i == 0 else tf15.add_paragraph()
        p.text = pt
        p.font.size = Pt(16)
        p.font.color.rgb = TEXT_LIGHT
        p.space_before = Pt(14)

    # ==========================================
    # SLIDE 16: The one rule to remember (Matches PDF Slide 18)
    # ==========================================
    s16 = prs.slides.add_slide(blank_layout)
    apply_background(s16)
    add_header(s16, "The one rule to remember", slide_num=16)

    add_card(s16, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_RED)
    box16 = s16.shapes.add_textbox(Inches(1.2), Inches(2.2), Inches(10.9), Inches(4.0))
    tf16 = box16.text_frame
    tf16.word_wrap = True

    p = tf16.paragraphs[0]
    p.text = "The screen must not talk to the database."
    p.font.size = Pt(28)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p.space_after = Pt(28)

    p2 = tf16.add_paragraph()
    p2.text = "UI  →  Service  →  Model / Database"
    p2.font.size = Pt(24)
    p2.font.bold = True
    p2.font.color.rgb = ACCENT_BLUE
    p2.space_after = Pt(28)

    p3 = tf16.add_paragraph()
    p3.text = "No  SELECT * FROM quizzes  or  INSERT INTO attempts  inside UI buttons."
    p3.font.size = Pt(16)
    p3.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 17: What you must be able to explain (Matches PDF Slide 19)
    # ==========================================
    s17 = prs.slides.add_slide(blank_layout)
    apply_background(s17)
    add_header(s17, "What you must be able to explain", slide_num=17)

    add_card(s17, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    box17 = s17.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.9), Inches(4.2))
    tf17 = box17.text_frame
    tf17.word_wrap = True

    explain_points = [
        "1. What each folder is for",
        "2. How a click travels: UI → Service → Database",
        "3. What data sits in each table (users, quizzes, attempts, audit_logs)",
        "4. How this is TQM, not only CRUD (Poka-yoke, CTQ, FMEA, Pareto, PDCA)"
    ]
    for i, pt in enumerate(explain_points):
        p = tf17.paragraphs[0] if i == 0 else tf17.add_paragraph()
        p.text = pt
        p.font.size = Pt(18)
        p.font.bold = True
        p.font.color.rgb = TEXT_LIGHT if i < 3 else ACCENT_AMBER
        p.space_before = Pt(18)

    # ==========================================
    # SLIDE 18: Full folder structure (Matches PDF Slide 20)
    # ==========================================
    s18 = prs.slides.add_slide(blank_layout)
    apply_background(s18)
    add_header(s18, "Full modular folder structure", slide_num=18)

    # 3 Column Trees
    col_trees = [
        ("CORE ROOT & DATABASE", ACCENT_BLUE, [
            "Online_Quiz_System/",
            "├── server.py",
            "├── desktop_app.py",
            "├── ai_quiz_generator.py",
            "├── quiz_system.db",
            "├── database/",
            "│   ├── db.py",
            "│   ├── schema.py",
            "│   └── migrations.py",
            "└── backups/"
        ]),
        ("SERVICES & MODELS", ACCENT_GREEN, [
            "├── services/",
            "│   ├── auth_service.py",
            "│   ├── quiz_service.py",
            "│   ├── grading_service.py",
            "│   ├── proctor_service.py",
            "│   └── report_service.py",
            "├── models/",
            "│   ├── user.py",
            "│   ├── quiz.py",
            "│   └── attempt.py"
        ]),
        ("UI, UTILS & REPORTS", ACCENT_AMBER, [
            "├── ui/ (Web SPA + Desktop)",
            "│   ├── login.py / auth.js",
            "│   ├── candidate_arena",
            "│   ├── examiner_studio",
            "│   └── admin_panel",
            "├── reports/ (gradebook, CSV)",
            "├── utils/ (validators, logs)",
            "└── tests/ (22 passing unit tests)"
        ])
    ]
    for i, (title, col, lines) in enumerate(col_trees):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s18, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s18.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(8)
        for line in lines:
            pl = tf.add_paragraph()
            pl.text = line
            pl.font.size = Pt(9.5)
            pl.font.color.rgb = TEXT_LIGHT
            pl.space_before = Pt(2)

    # ==========================================
    # SLIDE 19: What each file does — start + config + database (Matches PDF Slide 21)
    # ==========================================
    s19 = prs.slides.add_slide(blank_layout)
    apply_background(s19)
    add_header(s19, "What each file does — start + config + database", slide_num=19)

    f_desc_s19 = [
        ("server.py / desktop_app.py", "Starts the app. Configures FastAPI lifespan, DB connection, routes, then login."),
        ("config / settings.py", "App name, DB path, test time limits, passing score defaults, join code prefix."),
        ("database / db.py", "Opens SQLite, runs parameterized queries, commits transactions, closes connections."),
        ("database / schema.py", "Creates tables (users, quizzes, attempts, audit_logs) the first time the app runs."),
        ("database / migrations.py", "Adds new columns later (e.g. join_code, cheat_violations) without wiping test data.")
    ]
    for i, (fname, fdesc) in enumerate(f_desc_s19):
        top_pos = Inches(1.8 + i * 0.98)
        add_card(s19, Inches(0.8), top_pos, Inches(3.8), Inches(0.85), stripe_color=ACCENT_BLUE)
        bl = s19.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.15), Inches(3.5), Inches(0.6))
        p = bl.text_frame.paragraphs[0]
        p.text = fname
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE

        add_card(s19, Inches(4.8), top_pos, Inches(7.7), Inches(0.85))
        br = s19.shapes.add_textbox(Inches(5.0), top_pos + Inches(0.15), Inches(7.3), Inches(0.6))
        p = br.text_frame.paragraphs[0]
        p.text = fdesc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 20: What each file does — models (Matches PDF Slide 22)
    # ==========================================
    s20 = prs.slides.add_slide(blank_layout)
    apply_background(s20)
    add_header(s20, "What each file does — models", slide_num=20)

    sub_t = s20.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.35))
    p = sub_t.text_frame.paragraphs[0]
    p.text = "A model is the object. Not the SQL. Not the screen."
    p.font.size = Pt(12)
    p.font.color.rgb = ACCENT_AMBER

    models_desc = [
        ("models/user.py", "User object: id, username, password_hash, role (student/faculty/admin), department."),
        ("models/quiz.py", "Quiz object: id, join_code, teacher_name, title, category, duration, passing_score."),
        ("models/question.py", "Question object: id, prompt, options (list), correct_index, explanation."),
        ("models/attempt.py", "Attempt object: id, quiz_id, student_name, score, percentage, passed, cheat_violations."),
        ("models/violation.py", "Violation object: attempt_id, timestamp, event_type (window_blur, tab_switch).")
    ]
    for i, (mname, mdesc) in enumerate(models_desc):
        top_pos = Inches(1.85 + i * 0.98)
        add_card(s20, Inches(0.8), top_pos, Inches(3.2), Inches(0.85), stripe_color=ACCENT_GREEN)
        bl = s20.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.15), Inches(2.9), Inches(0.6))
        p = bl.text_frame.paragraphs[0]
        p.text = mname
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_GREEN

        add_card(s20, Inches(4.2), top_pos, Inches(8.3), Inches(0.85))
        br = s20.shapes.add_textbox(Inches(4.4), top_pos + Inches(0.15), Inches(7.9), Inches(0.6))
        p = br.text_frame.paragraphs[0]
        p.text = mdesc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 21: What each file does — services (Matches PDF Slide 23)
    # ==========================================
    s21 = prs.slides.add_slide(blank_layout)
    apply_background(s21)
    add_header(s21, "What each file does — services (The work happens here)", slide_num=21)

    services_desc = [
        ("auth_service.py", "Login, registration, password hashing, role permissions, token generation.", ACCENT_BLUE),
        ("quiz_service.py", "Create / edit quiz, generate unique 6-char Join Code, validate bounds.", ACCENT_GREEN),
        ("ai_service.py", "Synthesize questions automatically from syllabus topic keywords & difficulty.", ACCENT_AMBER),
        ("grading_service.py", "Sub-250ms deterministic scoring pipeline, calculate percentage & pass/fail.", ACCENT_PURPLE),
        ("proctor_service.py", "Log window blur & tab switch events, increment cheat violation tallies.", ACCENT_RED),
        ("report_service.py", "Pull live class gradebook records, platform KPIs, stream CSV exports.", ACCENT_CYAN)
    ]
    for i, (sname, sdesc, col) in enumerate(services_desc):
        top_pos = Inches(1.8 + i * 0.82)
        add_card(s21, Inches(0.8), top_pos, Inches(3.2), Inches(0.72), stripe_color=col)
        bl = s21.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.12), Inches(2.9), Inches(0.5))
        p = bl.text_frame.paragraphs[0]
        p.text = sname
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        add_card(s21, Inches(4.2), top_pos, Inches(8.3), Inches(0.72))
        br = s21.shapes.add_textbox(Inches(4.4), top_pos + Inches(0.12), Inches(7.9), Inches(0.5))
        p = br.text_frame.paragraphs[0]
        p.text = sdesc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 22: What each file does — UI screens (Matches PDF Slide 24)
    # ==========================================
    s22 = prs.slides.add_slide(blank_layout)
    apply_background(s22)
    add_header(s22, "What each file does — UI screens (What the person sees)", slide_num=22)

    ui_screens = [
        ("ui/login.py / auth.js", "Username + password authentication dialog with role navigation dispatch.", ACCENT_BLUE),
        ("ui/candidate_arena", "Join Code entry box, question navigation palette, authoritative countdown timer.", ACCENT_GREEN),
        ("ui/examiner_studio", "Manual question bank builder + AI synthesis wizard with 6-char code publisher.", ACCENT_AMBER),
        ("ui/gradebook", "Class submission table with candidate scores, timestamps, and proctor flags.", ACCENT_PURPLE),
        ("ui/admin_panel", "System KPI metrics, user roster table, and drill-down scorecard modal.", ACCENT_CYAN)
    ]
    for i, (uname, udesc, col) in enumerate(ui_screens):
        top_pos = Inches(1.8 + i * 0.98)
        add_card(s22, Inches(0.8), top_pos, Inches(3.2), Inches(0.85), stripe_color=col)
        bl = s22.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.15), Inches(2.9), Inches(0.6))
        p = bl.text_frame.paragraphs[0]
        p.text = uname
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        add_card(s22, Inches(4.2), top_pos, Inches(8.3), Inches(0.85))
        br = s22.shapes.add_textbox(Inches(4.4), top_pos + Inches(0.15), Inches(7.9), Inches(0.6))
        p = br.text_frame.paragraphs[0]
        p.text = udesc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 23: What each file does — reports + utils + assets (Matches PDF Slide 25)
    # ==========================================
    s23 = prs.slides.add_slide(blank_layout)
    apply_background(s23)
    add_header(s23, "What each file does — reports + utils + assets", slide_num=23)

    rua = [
        ("reports/gradebook.py", "Class submission logs. Pass rate, highest/lowest scores, student rankings.", ACCENT_BLUE),
        ("reports/tqm_report.py", "Submission latency statistics, proctor violation rates, Pareto charts.", ACCENT_GREEN),
        ("utils/validators.py", "Poka-yoke: rejects empty questions, invalid time limits, duplicate codes.", ACCENT_AMBER),
        ("utils/logger.py", "Writes structured telemetry and errors into error_logs table.", ACCENT_RED),
        ("utils/security.py", "Password hashing, role permissions verification, session persistence.", ACCENT_PURPLE),
        ("assets/ (CSS + Themes)", "Consistent fonts, cream theme, dark contrast mode across every screen.", ACCENT_CYAN)
    ]
    for i, (name, desc, col) in enumerate(rua):
        top_pos = Inches(1.8 + i * 0.82)
        add_card(s23, Inches(0.8), top_pos, Inches(3.2), Inches(0.72), stripe_color=col)
        bl = s23.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.12), Inches(2.9), Inches(0.5))
        p = bl.text_frame.paragraphs[0]
        p.text = name
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col

        add_card(s23, Inches(4.2), top_pos, Inches(8.3), Inches(0.72))
        br = s23.shapes.add_textbox(Inches(4.4), top_pos + Inches(0.12), Inches(7.9), Inches(0.5))
        p = br.text_frame.paragraphs[0]
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 24: How a click uses these files (Matches PDF Slide 26)
    # ==========================================
    s24 = prs.slides.add_slide(blank_layout)
    apply_background(s24)
    add_header(s24, "How a click uses these files (Candidate Submit Walkthrough)", slide_num=24)

    click_steps = [
        ("1 Screen", "candidate_arena takes answers and clicks Submit."),
        ("2 Service", "grading_service checks answers against the key."),
        ("3 Extra service", "proctor_service packages violation counts and timestamps."),
        ("4 Utils", "validators.py rejects malformed or corrupted payloads."),
        ("5 Database", "db.py saves attempt, score, and violations in one ACID transaction."),
        ("6 Proof", "audit_logs and attempts get a permanent row (<25ms)."),
        ("7 Later", "tqm_report, Pareto chart, and FMEA matrix read those logs.")
    ]
    for i, (lbl, desc) in enumerate(click_steps):
        top_pos = Inches(1.8 + i * 0.7)
        add_card(s24, Inches(0.8), top_pos, Inches(2.4), Inches(0.62), stripe_color=ACCENT_BLUE if i < 4 else ACCENT_GREEN)
        bl = s24.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.1), Inches(2.1), Inches(0.45))
        p = bl.text_frame.paragraphs[0]
        p.text = lbl
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE if i < 4 else ACCENT_GREEN

        add_card(s24, Inches(3.4), top_pos, Inches(9.1), Inches(0.62))
        br = s24.shapes.add_textbox(Inches(3.6), top_pos + Inches(0.1), Inches(8.7), Inches(0.45))
        p = br.text_frame.paragraphs[0]
        p.text = desc
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 25: Architecture 1 — request goes down (Matches PDF Slide 28)
    # ==========================================
    s25 = prs.slides.add_slide(blank_layout)
    apply_background(s25)
    add_header(s25, "Architecture 1 — request goes down (Multi-Tier Layers)", slide_num=25)

    arch_layers = [
        ("USER / EXAMINEE / ADMIN", "Student, Teacher, or Administrator interacting with the platform", ACCENT_BLUE),
        ("UI LAYER", "Login  /  Candidate Arena  /  Examiner Studio  /  Admin Console", ACCENT_GREEN),
        ("SERVICE LAYER", "Business rules: Auth, Quiz Engine, AI Generator, Auto-Grading, Proctoring", ACCENT_AMBER),
        ("MODEL & UTILITY LAYER", "User / Quiz / Attempt / Question  |  Poka-yoke Validation / Logger / Security", ACCENT_PURPLE),
        ("DATABASE LAYER", "ACID-compliant SQLite Engine (quiz_system.db)", ACCENT_CYAN),
        ("REPORTS / ANALYTICS", "Class Gradebook  /  Platform Telemetry  /  CSV Exports  /  TQM Charts", ACCENT_RED)
    ]
    for i, (lname, ldesc, col) in enumerate(arch_layers):
        top_pos = Inches(1.8 + i * 0.82)
        add_card(s25, Inches(0.8), top_pos, Inches(11.7), Inches(0.72), stripe_color=col)
        box = s25.shapes.add_textbox(Inches(1.1), top_pos + Inches(0.12), Inches(11.1), Inches(0.5))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.text = f"{lname}  —  "
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p_desc = tf.add_paragraph()
        p_desc.text = ldesc
        p_desc.font.size = Pt(11)
        p_desc.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 26: Architecture 2 — quality loop (Matches PDF Slide 29)
    # ==========================================
    s26 = prs.slides.add_slide(blank_layout)
    apply_background(s26)
    add_header(s26, "Architecture 2 — quality loop (Data into TQM Tools)", slide_num=26)

    # Top: Transaction Flow
    t_boxes = [("UI LAYER", ACCENT_BLUE), ("SERVICE LAYER", ACCENT_GREEN), ("REPORTS", ACCENT_AMBER)]
    for i, (name, col) in enumerate(t_boxes):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s26, c_left, Inches(1.8), Inches(3.8), Inches(1.0), stripe_color=col)
        b = s26.shapes.add_textbox(c_left, Inches(2.0), Inches(3.8), Inches(0.6))
        p = b.text_frame.paragraphs[0]
        p.text = name
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col
        p.alignment = PP_ALIGN.CENTER

    add_card(s26, Inches(0.8), Inches(3.0), Inches(11.7), Inches(0.9), stripe_color=ACCENT_PURPLE)
    b_mid = s26.shapes.add_textbox(Inches(0.8), Inches(3.15), Inches(11.7), Inches(0.6))
    p = b_mid.text_frame.paragraphs[0]
    p.text = "MODEL LAYER  |  DATABASE (SQLite)  |  UTILITY LOGGERS"
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.alignment = PP_ALIGN.CENTER

    # Bottom: Quality Loop
    add_card(s26, Inches(0.8), Inches(4.1), Inches(5.7), Inches(1.2), stripe_color=ACCENT_CYAN)
    b_bl = s26.shapes.add_textbox(Inches(1.0), Inches(4.25), Inches(5.3), Inches(0.9))
    p = b_bl.text_frame.paragraphs[0]
    p.text = "TRANSACTION DATA\nEvery attempt, score, latency, and violation logged."
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = TEXT_LIGHT

    add_card(s26, Inches(6.8), Inches(4.1), Inches(5.7), Inches(1.2), stripe_color=ACCENT_GREEN)
    b_br = s26.shapes.add_textbox(Inches(7.0), Inches(4.25), Inches(5.3), Inches(0.9))
    p = b_br.text_frame.paragraphs[0]
    p.text = "TQM ANALYSIS → CONTINUOUS IMPROVEMENT\nData from work becomes Pareto, Fishbone, FMEA, PDCA."
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN

    # Bottom Callout
    bot_box = s26.shapes.add_textbox(Inches(0.8), Inches(5.8), Inches(11.7), Inches(0.8))
    p = bot_box.text_frame.paragraphs[0]
    p.text = "Quality is not an afterthought: Every exam submission directly feeds the TQM statistical feedback loop."
    p.font.size = Pt(13)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.alignment = PP_ALIGN.CENTER

    # ==========================================
    # SLIDE 27: database / schema.py — tables we create (Matches PDF Slide 33)
    # ==========================================
    s27 = prs.slides.add_slide(blank_layout)
    apply_background(s27)
    add_header(s27, "database / schema.py — tables we create", slide_num=27)

    schema_tables = [
        ("users", "User accounts: student, faculty, admin with credentials & roles", ACCENT_BLUE),
        ("quizzes", "Assessments: join code, title, duration, pass score, questions JSON", ACCENT_GREEN),
        ("attempts", "Submissions: student name, score, percentage, pass/fail, violations", ACCENT_PURPLE),
        ("audit_logs", "Immutable audit trail of all administrative and testing actions", ACCENT_AMBER),
        ("error_logs", "Technical errors and focus loss events feeding FMEA and Pareto", ACCENT_RED),
        ("backups/", "Automated timestamped snapshots of database states", ACCENT_CYAN)
    ]
    for i, (tname, tdesc, col) in enumerate(schema_tables):
        row = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * 5.95)
        c_top = Inches(1.8 + row * 1.65)
        add_card(s27, c_left, c_top, Inches(5.7), Inches(1.45), stripe_color=col)
        box = s27.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.15), Inches(5.3), Inches(1.15))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = tname
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(4)
        pd = tf.add_paragraph()
        pd.text = tdesc
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 28: users table — example rows & other columns (Matches PDF Slides 37 & 38)
    # ==========================================
    s28 = prs.slides.add_slide(blank_layout)
    apply_background(s28)
    add_header(s28, "users table — example rows & schema", slide_num=28)

    # Table example
    add_card(s28, Inches(0.8), Inches(1.8), Inches(7.5), Inches(4.9), stripe_color=ACCENT_BLUE)
    b_tbl = s28.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(7.1), Inches(4.5))
    tf_tbl = b_tbl.text_frame
    tf_tbl.word_wrap = True

    p = tf_tbl.paragraphs[0]
    p.text = "LIVE USERS TABLE DATA (ACID PERSISTED)"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(8)

    user_rows = [
        ("usr-admin", "admin", "System Administrator", "admin", "Operations"),
        ("usr-fac-1", "faculty", "Prof. Alan Turing", "faculty", "Computer Science"),
        ("usr-fac-2", "sharma", "Prof. R.K. Sharma", "faculty", "Information Tech"),
        ("usr-stu-1", "student", "Alex Mercer", "student", "B.Tech CSE - 2026"),
        ("usr-stu-2", "priya", "Priya Verma", "student", "B.Tech IT - 2026")
    ]
    p_h = tf_tbl.add_paragraph()
    p_h.text = f"{'USER_ID':<12} {'USERNAME':<10} {'ROLE':<9} {'NAME':<18} {'DEPARTMENT'}"
    p_h.font.size = Pt(9.5)
    p_h.font.bold = True
    p_h.font.color.rgb = ACCENT_AMBER
    p_h.space_after = Pt(4)

    for uid, un, name, role, dept in user_rows:
        pu = tf_tbl.add_paragraph()
        pu.text = f"{uid:<12} {un:<10} {role.upper():<9} {name:<18} {dept}"
        pu.font.size = Pt(9)
        pu.font.color.rgb = TEXT_LIGHT
        pu.space_before = Pt(2)

    # Right: Other columns
    add_card(s28, Inches(8.5), Inches(1.8), Inches(4.0), Inches(4.9), stripe_color=ACCENT_GREEN)
    b_col = s28.shapes.add_textbox(Inches(8.7), Inches(2.0), Inches(3.6), Inches(4.5))
    tf_col = b_col.text_frame
    tf_col.word_wrap = True

    p = tf_col.paragraphs[0]
    p.text = "SECURITY & AUDIT COLUMNS"
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)

    u_details = [
        ("password_hash", "Never store plaintext in production. Store cryptographic hashes."),
        ("role", "Restricts portal access: Student, Faculty, or Admin."),
        ("department", "Groups cohorts for class gradebook filtering."),
        ("created_at", "Audit timestamp when account was registered.")
    ]
    for ut, ud in u_details:
        put = tf_col.add_paragraph()
        put.text = f"• {ut}:"
        put.font.size = Pt(10)
        put.font.bold = True
        put.font.color.rgb = TEXT_LIGHT
        put.space_before = Pt(6)
        pud = tf_col.add_paragraph()
        pud.text = f"  {ud}"
        pud.font.size = Pt(9)
        pud.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 29: quizzes and attempts tables — examples (Matches PDF Slides 39 & 44)
    # ==========================================
    s29 = prs.slides.add_slide(blank_layout)
    apply_background(s29)
    add_header(s29, "quizzes and attempts tables — live examples", slide_num=29)

    # Left: Quizzes table
    add_card(s29, Inches(0.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    bq = s29.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tfq = bq.text_frame
    tfq.word_wrap = True
    p = tfq.paragraphs[0]
    p.text = "TABLE: quizzes"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(8)

    q_samples = [
        ("QZ-1001", "Python Core & OOP", "Prof. Alan Turing", "10m", "70%"),
        ("QZ-2045", "Data Structures", "Prof. Alan Turing", "15m", "75%"),
        ("QZ-3942", "TQM Fundamentals", "Prof. R.K. Sharma", "12m", "65%")
    ]
    for code, title, teacher, dur, pscore in q_samples:
        p_item = tfq.add_paragraph()
        p_item.text = f"Code: {code}  |  {title}"
        p_item.font.bold = True
        p_item.font.size = Pt(10)
        p_item.font.color.rgb = TEXT_LIGHT
        p_item.space_before = Pt(4)
        p_det = tfq.add_paragraph()
        p_det.text = f"Teacher: {teacher} • Duration: {dur} • Pass: {pscore}"
        p_det.font.size = Pt(9)
        p_det.font.color.rgb = TEXT_MUTED

    # Right: Attempts table
    add_card(s29, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_PURPLE)
    ba = s29.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tfa = ba.text_frame
    tfa.word_wrap = True
    p = tfa.paragraphs[0]
    p.text = "TABLE: attempts"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(8)

    att_samples = [
        ("Alex Mercer", "QZ-1001", "5/5 (100%)", "PASSED", "0 violations"),
        ("Priya Verma", "QZ-1001", "4/5 (80%)", "PASSED", "1 tab switch"),
        ("Rahul Singh", "QZ-2045", "2/5 (40%)", "FAILED", "3 violations")
    ]
    for sname, code, score, res, viol in att_samples:
        p_item = tfa.add_paragraph()
        p_item.text = f"Student: {sname}  [{code}]"
        p_item.font.bold = True
        p_item.font.size = Pt(10)
        p_item.font.color.rgb = TEXT_LIGHT
        p_item.space_before = Pt(4)
        p_det = tfa.add_paragraph()
        p_det.text = f"Score: {score} • Result: {res} • Proctor: {viol}"
        p_det.font.size = Pt(9)
        p_det.font.color.rgb = ACCENT_GREEN if res == "PASSED" else ACCENT_RED

    # ==========================================
    # SLIDE 30: audit_logs and error_logs (Matches PDF Slides 45 & 46)
    # ==========================================
    s30 = prs.slides.add_slide(blank_layout)
    apply_background(s30)
    add_header(s30, "audit_logs & error_logs — feeding FMEA", slide_num=30)

    # Left: audit_logs
    add_card(s30, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), stripe_color=ACCENT_AMBER)
    bl30 = s30.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_l = bl30.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "AUDIT_LOGS — TRACEABILITY"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_AMBER
    p.space_after = Pt(8)

    audits = [
        ("Turing", "CREATE_QUIZ", "QZ-1001 published", "09:00"),
        ("Mercer", "SUBMIT_EXAM", "Score 100% (25ms latency)", "09:15"),
        ("Verma", "TAB_BLUR", "Focus loss violation logged", "09:22"),
        ("Admin", "EXPORT_CSV", "Class roster exported", "10:00")
    ]
    for who, act, det, tm in audits:
        p_a = tf_l.add_paragraph()
        p_a.text = f"{who}  →  {act} [{tm}]"
        p_a.font.bold = True
        p_a.font.size = Pt(10)
        p_a.font.color.rgb = TEXT_LIGHT
        p_a.space_before = Pt(4)
        p_d = tf_l.add_paragraph()
        p_d.text = f"  Detail: {det}"
        p_d.font.size = Pt(9)
        p_d.font.color.rgb = TEXT_MUTED

    # Right: error_logs
    add_card(s30, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_RED)
    br30 = s30.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf_r = br30.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "ERROR_LOGS — FOR FMEA LATER"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_RED
    p.space_after = Pt(8)

    errs = [
        ("E01", "window_blur (Tab switch)", "18 occurrences", "11:12"),
        ("E02", "blank_question_attempted", "7 occurrences", "10:03"),
        ("E03", "invalid_join_code_entered", "11 occurrences", "11:40"),
        ("E04", "login_credential_mismatch", "9 occurrences", "08:21")
    ]
    for code, prob, cnt, ls in errs:
        p_e = tf_r.add_paragraph()
        p_e.text = f"[{code}] {prob}"
        p_e.font.bold = True
        p_e.font.size = Pt(10)
        p_e.font.color.rgb = TEXT_LIGHT
        p_e.space_before = Pt(4)
        p_c = tf_r.add_paragraph()
        p_c.text = f"  Frequency: {cnt} • Last Seen: {ls}"
        p_c.font.size = Pt(9)
        p_c.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 31: Why migrations.py matters (Matches PDF Slide 35)
    # ==========================================
    s31 = prs.slides.add_slide(blank_layout)
    apply_background(s31)
    add_header(s31, "Why migrations.py matters", slide_num=31)

    add_card(s31, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    box31 = s31.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.9), Inches(4.2))
    tf31 = box31.text_frame
    tf31.word_wrap = True

    mig_points = [
        "1. If you only edit schema.py and recreate the DB, student test data is wiped.",
        "2. Migration dynamically inspects PRAGMA table_info and adds new columns to the live file.",
        "3. Real project example: Added 'join_code' and 'cheat_violations' seamlessly to live database.",
        "4. Review line: The database layer can grow without destroying historical examination records.",
        "5. TQM link: Maintainability, data durability, and process control."
    ]
    for i, pt in enumerate(mig_points):
        p = tf31.paragraphs[0] if i == 0 else tf31.add_paragraph()
        p.text = pt
        p.font.size = Pt(16)
        p.font.color.rgb = TEXT_LIGHT if i < 4 else ACCENT_AMBER
        p.space_before = Pt(14)

    # ==========================================
    # SLIDE 32: Software feature → TQM concept (Matches PDF Slide 68)
    # ==========================================
    s32 = prs.slides.add_slide(blank_layout)
    apply_background(s32)
    add_header(s32, "Software feature → TQM concept", slide_num=32)

    tqm_concepts = [
        ("Modular architecture", "Process / system approach"),
        ("Validation (Poka-yoke)", "Error prevention at source"),
        ("Audit log & Telemetry", "Traceability"),
        ("User roles (RBAC)", "Accountability"),
        ("Anti-Cheat Proctoring", "Process control"),
        ("Quality dashboard", "Data-driven decisions"),
        ("Pareto chart", "Root-cause prioritization (80/20)"),
        ("Fishbone diagram", "Causal analysis"),
        ("FMEA matrix", "Risk mitigation & RPN reduction"),
        ("PDCA cycle", "Continuous improvement")
    ]
    for i, (feat, concept) in enumerate(tqm_concepts):
        row = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * 5.95)
        c_top = Inches(1.8 + row * 0.95)
        add_card(s32, c_left, c_top, Inches(5.7), Inches(0.85))
        box = s32.shapes.add_textbox(c_left + Inches(0.15), c_top + Inches(0.12), Inches(5.4), Inches(0.6))
        tf = box.text_frame
        p = tf.paragraphs[0]
        p.text = feat
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = ACCENT_BLUE if col_idx == 0 else ACCENT_GREEN
        p_c = tf.add_paragraph()
        p_c.text = f"→ {concept}"
        p_c.font.size = Pt(10)
        p_c.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 33: Quality dashboard (Matches PDF Slide 69)
    # ==========================================
    s33 = prs.slides.add_slide(blank_layout)
    apply_background(s33)
    add_header(s33, "Quality dashboard (Real-time telemetry)", slide_num=33)

    q_cards = [
        ("Grading Accuracy", "100.0%", ACCENT_GREEN),
        ("Average Submission Latency", "24.8 ms", ACCENT_BLUE),
        ("Proctor Violation Rate", "0.4%", ACCENT_AMBER),
        ("Active Faculty & Creators", "2", ACCENT_PURPLE),
        ("Candidate Submissions", "50+", ACCENT_CYAN),
        ("System Defect Rate", "0.0%", ACCENT_GREEN)
    ]
    for i, (metric, val, col) in enumerate(q_cards):
        row = i // 3
        col_idx = i % 3
        c_left = Inches(0.8 + col_idx * 3.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s33, c_left, c_top, Inches(3.8), Inches(2.35), stripe_color=col)
        box = s33.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.2), Inches(3.4), Inches(1.95))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = metric
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = TEXT_MUTED
        p.space_after = Pt(12)
        pv = tf.add_paragraph()
        pv.text = val
        pv.font.size = Pt(32)
        pv.font.bold = True
        pv.font.color.rgb = col

    # ==========================================
    # SLIDE 34: Pareto — from error_logs and returns (Matches PDF Slide 70)
    # ==========================================
    s34 = prs.slides.add_slide(blank_layout)
    apply_background(s34)
    add_header(s34, "Pareto — from error_logs and violation telemetry", slide_num=34)

    sub_t = s34.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.35))
    p = sub_t.text_frame.paragraphs[0]
    p.text = "Fix the top bars first. That is 80/20 root cause prioritization."
    p.font.size = Pt(12)
    p.font.color.rgb = ACCENT_AMBER

    add_card(s34, Inches(0.8), Inches(1.85), Inches(11.7), Inches(4.85), stripe_color=ACCENT_BLUE)
    box34 = s34.shapes.add_textbox(Inches(1.2), Inches(2.0), Inches(10.9), Inches(4.5))
    tf34 = box34.text_frame
    tf34.word_wrap = True

    pareto_items = [
        ("Window Blur / Tab Switch Infractions", 18, 68),
        ("Invalid / Mis-typed Join Code", 7, 85),
        ("Unselected Radio Choice on Submit", 3, 94),
        ("Browser Network Glitch", 2, 98),
        ("Other", 1, 100)
    ]
    p_h = tf34.paragraphs[0]
    p_h.text = f"{'DEFECT / INFRACTION CATEGORY':<42} {'COUNT':<10} {'CUMULATIVE %'}"
    p_h.font.size = Pt(11)
    p_h.font.bold = True
    p_h.font.color.rgb = ACCENT_AMBER
    p_h.space_after = Pt(8)

    for cat, cnt, cum in pareto_items:
        p_row = tf34.add_paragraph()
        bar = "█" * (cnt * 2)
        p_row.text = f"{cat:<40} {cnt:<6} {cum}%  {bar}"
        p_row.font.size = Pt(11)
        p_row.font.color.rgb = TEXT_LIGHT
        p_row.space_before = Pt(6)

    # ==========================================
    # SLIDE 35: Fishbone — why exam submission errors happen (Matches PDF Slide 71)
    # ==========================================
    s35 = prs.slides.add_slide(blank_layout)
    apply_background(s35)
    add_header(s35, "Fishbone — why exam submission errors happen", slide_num=35)

    sub_t = s35.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.35))
    p = sub_t.text_frame.paragraphs[0]
    p.text = "Effect on the right: Examination Error / Submission Delay"
    p.font.size = Pt(12)
    p.font.color.rgb = ACCENT_RED

    fish_branches = [
        ("People", "Rushed student, exam anxiety, non-technical faculty compiler.", ACCENT_BLUE),
        ("Process", "No pre-flight code validation, manual spreadsheet scoring.", ACCENT_GREEN),
        ("Software", "Synchronous thread locks, missing Poka-yoke dialogs.", ACCENT_AMBER),
        ("Data", "Malformed question JSON, duplicate join codes, null values.", ACCENT_PURPLE),
        ("Machine", "Slow client browser, OS sleep timer, intermittent Wi-Fi.", ACCENT_CYAN)
    ]
    for i, (bone, causes, col) in enumerate(fish_branches):
        top_pos = Inches(1.85 + i * 0.98)
        add_card(s35, Inches(0.8), top_pos, Inches(3.2), Inches(0.85), stripe_color=col)
        bl = s35.shapes.add_textbox(Inches(0.95), top_pos + Inches(0.15), Inches(2.9), Inches(0.6))
        p = bl.text_frame.paragraphs[0]
        p.text = bone
        p.font.size = Pt(12)
        p.font.bold = True
        p.font.color.rgb = col

        add_card(s35, Inches(4.2), top_pos, Inches(8.3), Inches(0.85))
        br = s35.shapes.add_textbox(Inches(4.4), top_pos + Inches(0.15), Inches(7.9), Inches(0.6))
        p = br.text_frame.paragraphs[0]
        p.text = causes
        p.font.size = Pt(11)
        p.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 36: FMEA — from automated error logs (Matches PDF Slide 72)
    # ==========================================
    s36 = prs.slides.add_slide(blank_layout)
    apply_background(s36)
    add_header(s36, "FMEA — from automated error logs", slide_num=36)

    sub_t = s36.shapes.add_textbox(Inches(0.8), Inches(1.4), Inches(11.7), Inches(0.35))
    p = sub_t.text_frame.paragraphs[0]
    p.text = "RPN = Severity x Occurrence x Detection"
    p.font.size = Pt(12)
    p.font.color.rgb = ACCENT_AMBER

    add_card(s36, Inches(0.8), Inches(1.85), Inches(11.7), Inches(4.85), stripe_color=ACCENT_RED)
    box36 = s36.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(11.3), Inches(4.5))
    tf36 = box36.text_frame
    tf36.word_wrap = True

    fmea_rows = [
        ("Tab switch cheating", 8, 6, 7, 336, "FocusOut listener + Audio-visual warning", 6, 2, 4, 48),
        ("Lost answer on crash", 9, 5, 6, 270, "Local SQLite session caching & auto-save", 6, 2, 3, 36),
        ("Malformed question entry", 7, 5, 5, 175, "Poka-yoke validation disabled save until ready", 7, 1, 3, 21),
        ("Database corruption", 10, 3, 5, 150, "Automated timestamped snapshots in backups/", 10, 1, 3, 30),
        ("Invalid join code", 6, 6, 4, 144, "Auto-uppercase normalization & instant pre-flight", 4, 2, 2, 16)
    ]
    p_h = tf36.paragraphs[0]
    p_h.text = f"{'FAILURE MODE':<26} {'INIT S':<7} {'O':<3} {'D':<3} {'RPN':<6} {'ACTION (POKA-YOKE)':<34} {'REV RPN'}"
    p_h.font.size = Pt(9.5)
    p_h.font.bold = True
    p_h.font.color.rgb = ACCENT_AMBER
    p_h.space_after = Pt(6)

    for f_mode, s, o, d, rpn, act, rs, ro, rd, rev_rpn in fmea_rows:
        p_r = tf36.add_paragraph()
        p_r.text = f"{f_mode:<26} {s:<7} {o:<3} {d:<3} {rpn:<6} {act:<34} {rev_rpn} (-86%)"
        p_r.font.size = Pt(9)
        p_r.font.color.rgb = TEXT_LIGHT
        p_r.space_before = Pt(3)

    # ==========================================
    # SLIDE 37: How logs feed FMEA (Matches PDF Slide 73)
    # ==========================================
    s37 = prs.slides.add_slide(blank_layout)
    apply_background(s37)
    add_header(s37, "How logs feed FMEA", slide_num=37)

    add_card(s37, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_AMBER)
    box37 = s37.shapes.add_textbox(Inches(1.2), Inches(2.1), Inches(10.9), Inches(4.2))
    tf37 = box37.text_frame
    tf37.word_wrap = True

    feed_steps = [
        "1. Candidate triggers bad action (e.g. tab blur) or system catches invalid code.",
        "2. error_logs / audit_logs get a new structured row with timestamp.",
        "3. tqm_report / telemetry module counts each error code.",
        "4. High frequency count = High Occurrence rating (O).",
        "5. That row feeds directly into the FMEA matrix for risk mitigation."
    ]
    for i, pt in enumerate(feed_steps):
        p = tf37.paragraphs[0] if i == 0 else tf37.add_paragraph()
        p.text = pt
        p.font.size = Pt(17)
        p.font.color.rgb = TEXT_LIGHT if i < 4 else ACCENT_GREEN
        p.space_before = Pt(16)

    # ==========================================
    # SLIDE 38: PDCA on the same problem (Matches PDF Slide 74)
    # ==========================================
    s38 = prs.slides.add_slide(blank_layout)
    apply_background(s38)
    add_header(s38, "PDCA on the same problem (Continuous Improvement)", slide_num=38)

    pdca_quads = [
        ("PLAN", "Problem: Too many candidate window-blur cheating infractions.\nTarget: Reduce unmonitored infractions to zero with active proctoring.", ACCENT_BLUE),
        ("DO", "Action: Bind <FocusOut> event listeners and client tab-switch detector. Display live alert and log violation count.", ACCENT_GREEN),
        ("CHECK", "Audit: Monitor infraction frequency in class gradebook. Recalculate FMEA RPN from 336 down to 48.", ACCENT_AMBER),
        ("ACT", "Standardize: Make anti-cheat proctoring the mandatory standard across both Web SPA and Desktop GUI.", ACCENT_PURPLE)
    ]
    for i, (q_title, q_desc, col) in enumerate(pdca_quads):
        row = i // 2
        col_idx = i % 2
        c_left = Inches(0.8 + col_idx * 5.95)
        c_top = Inches(1.8 + row * 2.55)
        add_card(s38, c_left, c_top, Inches(5.7), Inches(2.35), stripe_color=col)
        box = s38.shapes.add_textbox(c_left + Inches(0.2), c_top + Inches(0.2), Inches(5.3), Inches(1.95))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = q_title
        p.font.size = Pt(14)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(8)
        pd = tf.add_paragraph()
        pd.text = q_desc
        pd.font.size = Pt(11)
        pd.font.color.rgb = TEXT_LIGHT

    # ==========================================
    # SLIDE 39: Build this much first & Review 1 vs later (Matches PDF Slides 77 & 78)
    # ==========================================
    s39 = prs.slides.add_slide(blank_layout)
    apply_background(s39)
    add_header(s39, "Build this much first — Review 1 vs Later Reviews", slide_num=39)

    add_card(s39, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), stripe_color=ACCENT_BLUE)
    bl39 = s39.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_l39 = bl39.text_frame
    tf_l39.word_wrap = True
    p = tf_l39.paragraphs[0]
    p.text = "REVIEW 1 DELIVERED (FOUNDATION)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    r1_items = [
        ("1. Login + User Roles", "Student, Faculty, Admin RBAC segregation"),
        ("2. Quizzes + Join Code", "Fast code distribution with QZ-XXXX"),
        ("3. Exam with 3 Checks", "Countdown timer + focus tracking + Poka-yoke"),
        ("4. Instant Auto-Grading", "Sub-250ms deterministic scoring pipeline"),
        ("5. Audit + Error Log", "Persistent SQLite telemetry tracking"),
        ("6. Working Web & Desktop", "Full functional parity verified with 22 tests")
    ]
    for it, idesc in r1_items:
        pi = tf_l39.add_paragraph()
        pi.text = f"✔ {it}:"
        pi.font.bold = True
        pi.font.size = Pt(10)
        pi.font.color.rgb = TEXT_LIGHT
        pi.space_before = Pt(3)
        pd = tf_l39.add_paragraph()
        pd.text = f"   {idesc}"
        pd.font.size = Pt(9)
        pd.font.color.rgb = TEXT_MUTED

    add_card(s39, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_PURPLE)
    br39 = s39.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf_r39 = br39.text_frame
    tf_r39.word_wrap = True
    p = tf_r39.paragraphs[0]
    p.text = "LATER REVIEWS (FULL TQM INTEGRATION)"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_PURPLE
    p.space_after = Pt(10)

    r2_items = [
        ("Full FMEA Scoring Marks", "Live recalculation of RPN after proctor mitigations"),
        ("Statistical Pareto Analysis", "Automated chart generation from live error logs"),
        ("Complete Ishikawa Fishbone", "Systematic root-cause remediation"),
        ("PDCA Continuous Loop", "Quarterly syllabus quality improvements"),
        ("Biometric Proctoring", "Periodic webcam identity verification")
    ]
    for it, idesc in r2_items:
        pi = tf_r39.add_paragraph()
        pi.text = f"➡ {it}:"
        pi.font.bold = True
        pi.font.size = Pt(10)
        pi.font.color.rgb = ACCENT_PURPLE
        pi.space_before = Pt(4)
        pd = tf_r39.add_paragraph()
        pd.text = f"   {idesc}"
        pd.font.size = Pt(9)
        pd.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 40: Working App Demo Guide — Setup & Commands
    # ==========================================
    s40 = prs.slides.add_slide(blank_layout)
    apply_background(s40)
    add_header(s40, "Working Application Demo Guide — Setup & Commands", slide_num=40)

    add_card(s40, Inches(0.8), Inches(1.8), Inches(5.6), Inches(4.9), stripe_color=ACCENT_BLUE)
    bl40 = s40.shapes.add_textbox(Inches(1.0), Inches(2.0), Inches(5.2), Inches(4.5))
    tf_l40 = bl40.text_frame
    tf_l40.word_wrap = True
    p = tf_l40.paragraphs[0]
    p.text = "EXECUTION & TEST COMMANDS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_BLUE
    p.space_after = Pt(10)

    demo_cmds = [
        ("1. Launch Web Server", "python server.py\nStarts FastAPI at http://localhost:8000 with lifespan initialization."),
        ("2. Launch Desktop GUI", "python desktop_app.py\nNative Windows CustomTkinter app with strict 44px grid table alignment."),
        ("3. Run Verification Tests", "python -m pytest tests/ -v\nRuns all 22 automated tests with zero deprecation warnings.")
    ]
    for ct, cd in demo_cmds:
        pc = tf_l40.add_paragraph()
        pc.text = f"▶ {ct}:"
        pc.font.bold = True
        pc.font.size = Pt(10.5)
        pc.font.color.rgb = TEXT_LIGHT
        pc.space_before = Pt(6)
        pcd = tf_l40.add_paragraph()
        pcd.text = f"   {cd}"
        pcd.font.size = Pt(9.5)
        pcd.font.color.rgb = TEXT_MUTED

    add_card(s40, Inches(6.8), Inches(1.8), Inches(5.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    br40 = s40.shapes.add_textbox(Inches(7.0), Inches(2.0), Inches(5.3), Inches(4.5))
    tf_r40 = br40.text_frame
    tf_r40.word_wrap = True
    p = tf_r40.paragraphs[0]
    p.text = "READY-TO-USE TEST ACCOUNTS"
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = ACCENT_GREEN
    p.space_after = Pt(10)

    demo_accs = [
        ("STUDENT", "student", "student123", "Candidate Arena: Join 'QZ-1001', test anti-cheat, instant scorecard."),
        ("FACULTY", "faculty", "faculty123", "Examiner Studio: Manual & AI quiz generator, class gradebook."),
        ("ADMIN", "admin", "admin123", "Platform Admin: Global telemetry KPIs, candidate history modal, CSV exports.")
    ]
    for rh, un, pwd, purp in demo_accs:
        pa = tf_r40.add_paragraph()
        pa.text = f"👤 {rh} ROLE:"
        pa.font.bold = True
        pa.font.size = Pt(10.5)
        pa.font.color.rgb = ACCENT_AMBER
        pa.space_before = Pt(6)
        pad = tf_r40.add_paragraph()
        pad.text = f"   Username: {un}  |  Password: {pwd}"
        pad.font.size = Pt(10)
        pad.font.bold = True
        pad.font.color.rgb = TEXT_LIGHT
        pad2 = tf_r40.add_paragraph()
        pad2.text = f"   Purpose: {purp}"
        pad2.font.size = Pt(9)
        pad2.font.color.rgb = TEXT_MUTED

    # ==========================================
    # SLIDE 41: Live Demonstration Workflows (Student, Faculty, Admin)
    # ==========================================
    s41 = prs.slides.add_slide(blank_layout)
    apply_background(s41)
    add_header(s41, "Live demonstration walkthroughs (Student, Faculty, Admin)", slide_num=41)

    flows41 = [
        ("STUDENT EXAM FLOW", ACCENT_BLUE, [
            "1. Sign in as student / student123",
            "2. Navigation restricts to Candidate Arena",
            "3. Enter active Join Code 'QZ-1001'",
            "4. Take test while countdown runs",
            "5. Switch tabs to trigger Anti-Cheat alert",
            "6. Submit: Scorecard delivered in ~25ms"
        ]),
        ("FACULTY STUDIO FLOW", ACCENT_GREEN, [
            "1. Sign in as faculty / faculty123",
            "2. Navigation displays Examiner Studio",
            "3. Use AI Wizard: Topic 'Data Structures'",
            "4. Publish test with Join Code (e.g. QZ-3942)",
            "5. Open Class Gradebook to inspect submissions and cheat violation flags"
        ]),
        ("ADMIN TELEMETRY FLOW", ACCENT_PURPLE, [
            "1. Sign in as admin / admin123",
            "2. Open Platform Admin Console",
            "3. Review telemetry KPIs & pass rate",
            "4. Filter roster table by role or name",
            "5. Open candidate historical modal",
            "6. One-click CSV export streams"
        ])
    ]
    for i, (title, col, steps) in enumerate(flows41):
        c_left = Inches(0.8 + i * 3.95)
        add_card(s41, c_left, Inches(1.8), Inches(3.8), Inches(4.9), stripe_color=col)
        box = s41.shapes.add_textbox(c_left + Inches(0.2), Inches(2.0), Inches(3.4), Inches(4.5))
        tf = box.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = title
        p.font.size = Pt(11)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_after = Pt(8)
        for st in steps:
            ps = tf.add_paragraph()
            ps.text = st
            ps.font.size = Pt(9.5)
            ps.font.color.rgb = TEXT_LIGHT
            ps.space_before = Pt(5)

    # ==========================================
    # SLIDE 42: One sentence for viva (The Perfect Closing) (Matches PDF Slide 79)
    # ==========================================
    s42 = prs.slides.add_slide(blank_layout)
    apply_background(s42)
    add_header(s42, "One sentence for viva", slide_num=42)

    add_card(s42, Inches(0.8), Inches(1.8), Inches(11.7), Inches(4.9), stripe_color=ACCENT_GREEN)
    box42 = s42.shapes.add_textbox(Inches(1.2), Inches(2.3), Inches(10.9), Inches(4.0))
    tf42 = box42.text_frame
    tf42.word_wrap = True

    viva_lines = [
        ("The UI never writes SQL.", ACCENT_RED),
        ("Validation stops bad data at the source.", ACCENT_BLUE),
        ("Audit records who submitted what and when.", ACCENT_AMBER),
        ("Cheating is tracked and timeouts cannot corrupt grades.", ACCENT_CYAN),
        ("Logs become Pareto, Fishbone, FMEA, and PDCA.", ACCENT_GREEN)
    ]
    for i, (line, col) in enumerate(viva_lines):
        p = tf42.paragraphs[0] if i == 0 else tf42.add_paragraph()
        p.text = line
        p.font.size = Pt(22)
        p.font.bold = True
        p.font.color.rgb = col
        p.space_before = Pt(12)

    # Save to master PPT and primary PPT
    p_master = os.path.abspath("QuizSphere_Master_Review_1_and_2.pptx")
    prs.save(p_master)
    print(f"Master presentation successfully saved to:\n - {p_master}")

    p_rev1 = os.path.abspath("QuizSphere_Review_1_Presentation.pptx")
    try:
        prs.save(p_rev1)
        print(f" - {p_rev1}")
    except PermissionError:
        p_alt = os.path.abspath("QuizSphere_Review_1_and_2_Deck.pptx")
        prs.save(p_alt)
        print(f"Note: '{p_rev1}' was open in PowerPoint. Saved copy to:\n - {p_alt}")

if __name__ == "__main__":
    build_master_deck()
