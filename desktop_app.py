"""
Online Quiz System — Secure Multi-Platform Desktop Application (Pro 2.0)
Designed to mirror the modern web interface (QuizSphere Pro) with rich dark obsidian aesthetics,
top navigation bar, Candidate Arena, Examiner Studio, Live Exam Arena, Scorecard, and Accessibility controls.
"""

import os
import sys
import json
import time
import shutil
import random
import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox, filedialog
import customtkinter as ctk

from ai_quiz_generator import generate_quiz_with_ai
from tqm_sqc_tools import (
    generate_pareto_chart,
    generate_fishbone_diagram,
    run_automated_db_backup,
    export_class_reports_to_csv
)

# CustomTkinter Visual Configuration (Professional Light Theme Default)
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("blue")

DB_PATH = "quiz_system.db"
BACKUPS_DIR = "backups"
REPORTS_DIR = "reports"
os.makedirs(BACKUPS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)


class DatabaseManager:
    """SQLite Database Engine supporting full CRUD, Migrations, and Audit Logs."""
    def __init__(self):
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Quizzes Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id TEXT PRIMARY KEY,
                join_code TEXT UNIQUE NOT NULL,
                teacher_name TEXT NOT NULL DEFAULT 'Prof. Alan Turing',
                title TEXT NOT NULL,
                category TEXT,
                description TEXT,
                duration_minutes INTEGER,
                passing_score INTEGER,
                tags TEXT,
                questions_json TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Attempts Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id TEXT PRIMARY KEY,
                quiz_id TEXT NOT NULL,
                join_code TEXT NOT NULL,
                quiz_title TEXT NOT NULL,
                teacher_name TEXT NOT NULL,
                student_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                cheat_violations INTEGER DEFAULT 0,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
            )
        """)

        # Schema Migrations
        cursor.execute("PRAGMA table_info(quizzes)")
        quiz_cols = [c[1] for c in cursor.fetchall()]
        if "join_code" not in quiz_cols:
            cursor.execute("ALTER TABLE quizzes ADD COLUMN join_code TEXT DEFAULT 'QZ-1001'")
        if "teacher_name" not in quiz_cols:
            cursor.execute("ALTER TABLE quizzes ADD COLUMN teacher_name TEXT DEFAULT 'Prof. Alan Turing'")
        cursor.execute("UPDATE quizzes SET join_code = 'QZ-1001' WHERE join_code IS NULL OR join_code = ''")

        cursor.execute("PRAGMA table_info(attempts)")
        attempt_cols = [c[1] for c in cursor.fetchall()]
        if "join_code" not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN join_code TEXT DEFAULT 'QZ-1001'")
        if "teacher_name" not in attempt_cols:
            cursor.execute("ALTER TABLE attempts ADD COLUMN teacher_name TEXT DEFAULT 'Prof. Alan Turing'")
        if "student_name" not in attempt_cols:
            if "candidate_name" in attempt_cols:
                cursor.execute("ALTER TABLE attempts ADD COLUMN student_name TEXT DEFAULT ''")
                cursor.execute("UPDATE attempts SET student_name = candidate_name WHERE student_name = ''")
            else:
                cursor.execute("ALTER TABLE attempts ADD COLUMN student_name TEXT DEFAULT 'Candidate'")

        conn.commit()

        # Users Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT NOT NULL,
                full_name TEXT NOT NULL,
                department TEXT DEFAULT 'Computer Science & Engineering',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

        # Seed default users if empty
        cursor.execute("SELECT COUNT(*) FROM users")
        if cursor.fetchone()[0] == 0:
            default_users = [
                ("usr-admin", "admin", "admin123", "admin", "System Administrator", "Operations & Quality Assurance"),
                ("usr-fac-1", "faculty", "faculty123", "faculty", "Prof. Alan Turing", "Computer Science & Engineering"),
                ("usr-stu-1", "student", "student123", "student", "Alex Mercer", "B.Tech CSE - 2026")
            ]
            cursor.executemany("""
                INSERT INTO users (id, username, password, role, full_name, department)
                VALUES (?, ?, ?, ?, ?, ?)
            """, default_users)
            conn.commit()

        # Seed initial quiz if empty
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        if cursor.fetchone()[0] == 0:
            seed_q1 = [
                {
                    "id": "q1",
                    "text": "What does HTTP status code 403 Forbidden indicate?",
                    "code": None,
                    "options": [
                        "The server understood the request but refuses authorization",
                        "The requested URL resource does not exist on the server",
                        "The server encountered an unhandled internal exception",
                        "The request method is unsupported by the gateway"
                    ],
                    "correct": 0,
                    "explanation": "403 Forbidden indicates the server authenticated the request but refuses access permissions."
                },
                {
                    "id": "q2",
                    "text": "Which statement best describes the Worst-Case time complexity of searching in an unbalanced BST?",
                    "code": None,
                    "options": ["O(log N)", "O(N)", "O(1)", "O(N log N)"],
                    "correct": 1,
                    "explanation": "An unbalanced BST degenerates into a linear linked list in the worst case, yielding O(N) complexity."
                },
                {
                    "id": "q3",
                    "text": "What is the primary function of Python's '__slots__' class declaration?",
                    "code": "class Particle:\n    __slots__ = ('x', 'y')",
                    "options": [
                        "Restricts dynamic attributes and optimizes object memory footprint",
                        "Compiles the class to native machine bytecode ahead-of-time",
                        "Prevents the class from being inherited or subclassed",
                        "Automatically synchronizes object state across distributed nodes"
                    ],
                    "correct": 0,
                    "explanation": "__slots__ disables the default __dict__ instance dictionary, drastically reducing RAM overhead."
                },
                {
                    "id": "q4",
                    "text": "In Statistical Quality Control, which principle isolates the vital few causes from the trivial many?",
                    "code": None,
                    "options": [
                        "Pareto 80/20 Rule",
                        "Central Limit Theorem",
                        "Ishikawa 4M Rule",
                        "Deming Cycle"
                    ],
                    "correct": 0,
                    "explanation": "Vilfredo Pareto's 80/20 rule demonstrates that roughly 80% of defects stem from 20% of causes."
                }
            ]
            cursor.execute("""
                INSERT INTO quizzes (id, join_code, teacher_name, title, category, description, duration_minutes, passing_score, tags, questions_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "quiz-sample-1",
                "QZ-1001",
                "Prof. Alan Turing",
                "Computer Science & System Architecture",
                "Software Engineering",
                "Baseline assessment covering algorithms, memory optimization, and web networking protocols.",
                10,
                70,
                json.dumps(["Computer Science", "Algorithms", "Core"]),
                json.dumps(seed_q1)
            ))
            conn.commit()

        conn.close()

    def get_all_quizzes(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            keys = r.keys()
            join_code = r["join_code"] if "join_code" in keys else "QZ-1001"
            teacher_name = r["teacher_name"] if "teacher_name" in keys else "Prof. Alan Turing"
            result.append({
                "id": r["id"],
                "joinCode": join_code,
                "teacherName": teacher_name,
                "title": r["title"],
                "category": r["category"] or "General",
                "description": r["description"] or "",
                "durationMinutes": r["duration_minutes"],
                "passingScore": r["passing_score"],
                "tags": json.loads(r["tags"]) if r["tags"] else [],
                "questions": json.loads(r["questions_json"]),
                "createdAt": r["created_at"]
            })
        conn.close()
        return result

    def get_quiz_by_code(self, code):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes WHERE UPPER(join_code) = UPPER(?)", (code.strip(),))
        r = cursor.fetchone()
        conn.close()
        if not r:
            return None
        return {
            "id": r["id"],
            "joinCode": r["join_code"],
            "teacherName": r["teacher_name"],
            "title": r["title"],
            "category": r["category"] or "General",
            "description": r["description"] or "",
            "durationMinutes": r["duration_minutes"],
            "passingScore": r["passing_score"],
            "tags": json.loads(r["tags"]) if r["tags"] else [],
            "questions": json.loads(r["questions_json"]),
            "createdAt": r["created_at"]
        }

    def save_quiz(self, quiz):
        conn = self.get_connection()
        cursor = conn.cursor()
        join_code = quiz.get("joinCode") or f"QZ-{random.randint(1000, 9999)}"
        teacher_name = quiz.get("teacherName") or "Prof. Alan Turing"
        cursor.execute("""
            INSERT OR REPLACE INTO quizzes (id, join_code, teacher_name, title, category, description, duration_minutes, passing_score, tags, questions_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            quiz["id"],
            join_code,
            teacher_name,
            quiz["title"],
            quiz.get("category", "General"),
            quiz.get("description", ""),
            quiz.get("durationMinutes", 10),
            quiz.get("passingScore", 70),
            json.dumps(quiz.get("tags", [])),
            json.dumps(quiz["questions"])
        ))
        conn.commit()
        conn.close()

    def delete_quiz(self, quiz_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        conn.commit()
        conn.close()

    def record_attempt(self, attempt):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("PRAGMA table_info(attempts)")
        cols = [c[1] for c in cursor.fetchall()]
        st_name = attempt.get("studentName") or attempt.get("candidateName") or "Candidate"
        if "candidate_name" in cols:
            cursor.execute("""
                INSERT INTO attempts (id, quiz_id, join_code, quiz_title, teacher_name, student_name, candidate_name, score, total_questions, percentage, passed, cheat_violations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attempt["id"],
                attempt["quizId"],
                attempt["joinCode"],
                attempt["quizTitle"],
                attempt["teacherName"],
                st_name,
                st_name,
                attempt["score"],
                attempt["totalQuestions"],
                attempt["percentage"],
                1 if attempt["passed"] else 0,
                attempt["cheatViolations"]
            ))
        else:
            cursor.execute("""
                INSERT INTO attempts (id, quiz_id, join_code, quiz_title, teacher_name, student_name, score, total_questions, percentage, passed, cheat_violations)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                attempt["id"],
                attempt["quizId"],
                attempt["joinCode"],
                attempt["quizTitle"],
                attempt["teacherName"],
                st_name,
                attempt["score"],
                attempt["totalQuestions"],
                attempt["percentage"],
                1 if attempt["passed"] else 0,
                attempt["cheatViolations"]
            ))
        conn.commit()
        conn.close()

    def get_teacher_reports(self, teacher_name=None):
        conn = self.get_connection()
        cursor = conn.cursor()
        if teacher_name:
            cursor.execute("SELECT * FROM attempts WHERE teacher_name = ? ORDER BY submitted_at DESC", (teacher_name,))
        else:
            cursor.execute("SELECT * FROM attempts ORDER BY submitted_at DESC")
        rows = cursor.fetchall()
        result = []
        for r in rows:
            keys = r.keys()
            student_name = r["student_name"] if "student_name" in keys else "Student"
            result.append({
                "id": r["id"],
                "quizTitle": r["quiz_title"],
                "joinCode": r["join_code"] if "join_code" in keys else "QZ-1001",
                "teacherName": r["teacher_name"] if "teacher_name" in keys else "Prof. Alan Turing",
                "studentName": student_name,
                "score": r["score"],
                "totalQuestions": r["total_questions"],
                "percentage": r["percentage"],
                "passed": bool(r["passed"]),
                "cheatViolations": r["cheat_violations"],
                "submittedAt": r["submitted_at"]
            })
        conn.close()
        return result

    def get_global_stats(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        total_quizzes = cursor.fetchone()[0]

        cursor.execute("SELECT COUNT(*), SUM(passed) FROM attempts")
        row = cursor.fetchone()
        total_attempts = row[0] or 0
        passed_attempts = row[1] or 0
        pass_rate = round((passed_attempts / total_attempts) * 100) if total_attempts > 0 else 0

        cursor.execute("SELECT COUNT(DISTINCT teacher_name) FROM quizzes")
        active_teachers = cursor.fetchone()[0] or 1

        cursor.execute("SELECT COUNT(DISTINCT student_name) FROM attempts")
        active_students = cursor.fetchone()[0] or 0
        conn.close()

        return {
            "totalQuizzes": total_quizzes,
            "totalAttempts": total_attempts,
            "passRate": pass_rate,
            "activeTeachers": active_teachers,
            "activeStudents": active_students
        }


class OnlineQuizDesktopApp(ctk.CTk):
    """
    Native Desktop GUI mirroring the QuizSphere Pro Web Architecture.
    Features:
    - Sleek Top Navbar with Role Switcher & Accessibility Toolbar
    - Candidate Arena Catalog with real-time search & fast Quiz Code joiner
    - Readiness Check Modal with security briefing & custom candidate names
    - Live Exam Arena with timer urgency, code blocks, option cards & palette matrix
    - Minimalist Layout (Focus Mode) that collapses peripheral elements (hotkey: F)
    - Full Result Scorecard with detailed question explanations
    - Examiner Studio with Quiz Creator, AI Synthesizer, Submissions Gradebook, and CSV Export
    """
    def __init__(self):
        super().__init__()

        self.title("Online Quiz System — Secure Multi-Platform Assessment")
        self.geometry("1300x840")
        self.minsize(1060, 720)

        # Accessibility, Theme & Display Settings
        self.current_theme = "light"  # "light" (default) or "dark"
        self.high_contrast = False
        self.font_scale = 1.0  # 0.85 to 1.45
        self.minimalist_focus_mode = False
        self.current_nav_view = "candidate-arena"  # candidate-arena, examiner-studio, exam-arena, result-scorecard

        c = self.get_theme_colors()
        self.configure(fg_color=c["bg_primary"])

        self.db = DatabaseManager()

        # Session & Authentication State
        self.current_role = "student"  # "student" or "examiner"
        self.student_name = "Alex Mercer"
        self.teacher_name = "Prof. Alan Turing"

        # Exam Session Variables
        self.active_quiz = None
        self.current_q_index = 0
        self.user_answers = {}  # q_id -> selected_index
        self.review_flags = set()  # set of marked q_ids
        self.time_left_seconds = 0
        self.timer_running = False
        self.cheat_violations = 0
        self.last_attempt_result = None
        self.last_focus_loss_time = 0

        # Global anti-cheat window focus listener
        self.bind("<FocusOut>", self.on_window_focus_loss)

        # Global keyboard navigation
        self.setup_keyboard_shortcuts()

        # Main Layout Configuration (Row 0: Top Nav, Row 1: Workspace)
        self.grid_rowconfigure(0, weight=0)
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.setup_top_nav()
        self.setup_workspace()

        # Launch directly into Candidate Arena (matching the website!)
        self.switch_nav_view("candidate-arena")

    # =========================================================================
    # ACCESSIBILITY & SCALING HELPERS
    # =========================================================================
    def scaled_font(self, size, weight="normal", family=None):
        scaled_size = max(9, int(round(size * self.font_scale)))
        kwargs = {"size": scaled_size, "weight": weight}
        if family:
            kwargs["family"] = family
        return ctk.CTkFont(**kwargs)

    def get_theme_colors(self):
        if self.high_contrast:
            return {
                "bg_primary": "#000000",
                "bg_card": "#050505",
                "bg_card_secondary": "#111111",
                "bg_card_hover": "#18181b",
                "card_border": "#ffffff",
                "border_width": 2,
                "text_primary": "#ffffff",
                "text_secondary": "#fde047",  # High-vis yellow
                "text_dim": "#fde047",
                "text_cyan": "#38bdf8",
                "accent_primary": "#fbbf24",
                "btn_cyan": "#fde047",
                "btn_cyan_text": "#000000",
                "btn_neutral": "#000000",
                "btn_neutral_text": "#ffffff",
                "btn_neutral_hover": "#222222",
                "palette_current": "#ffffff",
                "palette_answered": "#22c55e",
                "palette_review": "#f59e0b",
                "palette_unanswered": "#18181b",
                "palette_unanswered_text": "#ffffff",
                "code_bg": "#000000",
                "code_text": "#38bdf8",
                "table_header_bg": "#18181b",
                "table_row_alt": "#000000",
                "badge_cyan_bg": "#082f49",
                "badge_cyan_text": "#38bdf8",
                "badge_indigo_bg": "#312e81",
                "badge_indigo_text": "#c7d2fe",
                "option_selected_bg": "#18181b"
            }
        elif self.current_theme == "light":
            # Executive Professional Cream Theme (Default)
            return {
                "bg_primary": "#f6f1e5",         # Rich, soothing warm cream canvas
                "bg_card": "#fdfbf7",            # Warm ivory elevated card surface
                "bg_card_secondary": "#eee7d5",  # Warm beige container / well / header
                "bg_card_hover": "#f3ecda",
                "card_border": "#dfd7c2",        # Warm linen hairline border
                "border_width": 1,
                "text_primary": "#1c1917",       # Stone-900 warm deep espresso charcoal
                "text_secondary": "#44403c",     # Stone-700 warm readable secondary
                "text_dim": "#78716c",           # Stone-500 warm taupe
                "text_cyan": "#0284c7",          # Sapphire / deep sky
                "accent_primary": "#4338ca",     # Deep rich authoritative indigo
                "btn_cyan": "#0284c7",           # Sky / sapphire action button
                "btn_cyan_text": "#ffffff",
                "btn_neutral": "#fdfbf7",        # Warm ivory button
                "btn_neutral_text": "#1c1917",
                "btn_neutral_hover": "#eee7d5",
                "palette_current": "#4338ca",
                "palette_answered": "#059669",
                "palette_review": "#d97706",
                "palette_unanswered": "#eee7d5",
                "palette_unanswered_text": "#44403c",
                "code_bg": "#292524",            # Warm dark stone terminal block
                "code_text": "#38bdf8",          # High-contrast sky blue syntax
                "table_header_bg": "#eee7d5",
                "table_row_alt": "#f3ecda",
                "badge_cyan_bg": "#daf0fa",
                "badge_cyan_text": "#0369a1",
                "badge_indigo_bg": "#ebe9fe",
                "badge_indigo_text": "#4338ca",
                "option_selected_bg": "#ede4ce"  # Warm cream active card tint
            }
        else:
            # Modern Obsidian Dark Theme
            return {
                "bg_primary": "#0a0e17",
                "bg_card": "#0f172a",
                "bg_card_secondary": "#1e293b",
                "bg_card_hover": "#1e293b",
                "card_border": "#1e293b",
                "border_width": 1,
                "text_primary": "#ffffff",
                "text_secondary": "#94a3b8",
                "text_dim": "#64748b",
                "text_cyan": "#06b6d4",
                "accent_primary": "#6366f1",
                "btn_cyan": "#06b6d4",
                "btn_cyan_text": "#030712",
                "btn_neutral": "#1e293b",
                "btn_neutral_text": "#ffffff",
                "btn_neutral_hover": "#334155",
                "palette_current": "#0284c7",
                "palette_answered": "#10b981",
                "palette_review": "#f59e0b",
                "palette_unanswered": "#1e293b",
                "palette_unanswered_text": "#94a3b8",
                "code_bg": "#050811",
                "code_text": "#38bdf8",
                "table_header_bg": "#1e293b",
                "table_row_alt": "#111827",
                "badge_cyan_bg": "#082f49",
                "badge_cyan_text": "#22d3ee",
                "badge_indigo_bg": "#1e1b4b",
                "badge_indigo_text": "#a5b4fc",
                "option_selected_bg": "#1e1b4b"
            }

    def toggle_appearance_mode(self):
        if self.current_theme == "light":
            self.current_theme = "dark"
            ctk.set_appearance_mode("Dark")
            if hasattr(self, "theme_btn"):
                self.theme_btn.configure(text="🌙 Dark")
        else:
            self.current_theme = "light"
            ctk.set_appearance_mode("Light")
            if hasattr(self, "theme_btn"):
                self.theme_btn.configure(text="☀️ Light")

        c = self.get_theme_colors()
        self.configure(fg_color=c["bg_primary"])
        self.nav_header.configure(fg_color=c["bg_primary"], border_color=c["card_border"])
        self.update_nav_controls_colors()
        self.refresh_current_view()

    def update_nav_controls_colors(self):
        c = self.get_theme_colors()
        if hasattr(self, "brand_lbl"):
            self.brand_lbl.configure(text_color=c["text_primary"])
        if hasattr(self, "pro_badge"):
            self.pro_badge.configure(fg_color=c["badge_cyan_bg"], text_color=c["badge_cyan_text"])
        if hasattr(self, "nav_tabs_frame"):
            self.nav_tabs_frame.configure(fg_color=c["bg_card_secondary"], border_color=c["card_border"])
        if hasattr(self, "theme_btn"):
            self.theme_btn.configure(fg_color=c["btn_neutral"], text_color=c["btn_neutral_text"], hover_color=c["btn_neutral_hover"])
        if hasattr(self, "contrast_btn"):
            self.contrast_btn.configure(
                text="👁️ AAA" if self.high_contrast else "👁️ Contrast",
                fg_color="#000000" if self.high_contrast else c["btn_neutral"],
                text_color="#fde047" if self.high_contrast else c["btn_neutral_text"],
                hover_color=c["btn_neutral_hover"]
            )
        if hasattr(self, "font_down_btn"):
            self.font_down_btn.configure(fg_color=c["btn_neutral"], text_color=c["btn_neutral_text"], hover_color=c["btn_neutral_hover"])
        if hasattr(self, "font_up_btn"):
            self.font_up_btn.configure(fg_color=c["btn_neutral"], text_color=c["btn_neutral_text"], hover_color=c["btn_neutral_hover"])
        if hasattr(self, "focus_btn"):
            self.focus_btn.configure(
                fg_color=c["accent_primary"] if self.minimalist_focus_mode else c["btn_neutral"],
                text_color="#ffffff" if self.minimalist_focus_mode else c["btn_neutral_text"],
                hover_color=c["btn_neutral_hover"]
            )
        if hasattr(self, "user_chip_btn"):
            self.user_chip_btn.configure(fg_color=c["badge_cyan_bg"], text_color=c["badge_cyan_text"])

    def adjust_font_scale(self, delta):
        new_scale = round(self.font_scale + delta, 2)
        if 0.85 <= new_scale <= 1.45:
            self.font_scale = new_scale
            self.refresh_current_view()

    def toggle_high_contrast(self):
        self.high_contrast = not self.high_contrast
        c = self.get_theme_colors()
        self.configure(fg_color=c["bg_primary"])
        self.nav_header.configure(fg_color=c["bg_primary"], border_color=c["card_border"])
        self.update_nav_controls_colors()
        self.refresh_current_view()

    def toggle_minimalist_mode(self):
        self.minimalist_focus_mode = not self.minimalist_focus_mode
        self.update_nav_controls_colors()
        if self.current_nav_view == "exam-arena":
            self.render_exam_arena()

    def refresh_current_view(self):
        if self.current_nav_view == "candidate-arena":
            self.render_candidate_arena()
        elif self.current_nav_view == "examiner-studio":
            self.render_examiner_studio()
        elif self.current_nav_view == "exam-arena":
            self.render_exam_arena()
        elif self.current_nav_view == "result-scorecard":
            self.render_result_scorecard()

    # =========================================================================
    # KEYBOARD NAVIGATION & SHORTCUTS
    # =========================================================================
    def setup_keyboard_shortcuts(self):
        def _on_key(event):
            # Do not intercept hotkeys if user is currently typing in an Entry or Textbox
            focused = self.focus_get()
            if isinstance(focused, (tk.Entry, tk.Text, ctk.CTkEntry, ctk.CTkTextbox)):
                return

            key = event.keysym.lower()

            # Global Focus Mode toggle (F key)
            if key == "f":
                self.toggle_minimalist_mode()
                return

            if self.current_nav_view != "exam-arena" or not self.active_quiz:
                return

            # Exam Question Option selection (1-4 or A-D)
            q = self.active_quiz["questions"][self.current_q_index]
            opts_len = len(q["options"])

            if key in ["1", "2", "3", "4"] and (int(key) - 1) < opts_len:
                self.handle_option_selection(int(key) - 1)
            elif key in ["a", "b", "c", "d"]:
                idx_map = {"a": 0, "b": 1, "c": 2, "d": 3}
                if idx_map[key] < opts_len:
                    self.handle_option_selection(idx_map[key])
            elif key in ["left", "p"]: # Previous
                self.navigate_question(-1)
            elif key in ["right", "n"]: # Next
                self.navigate_question(1)
            elif key == "m": # Mark for Review
                self.toggle_review_flag()
            elif key == "s": # Submit Confirm
                self.confirm_exam_submission()

        self.bind("<Key>", _on_key)

    # =========================================================================
    # TOP NAVIGATION BAR (Mirrors Web App Navbar)
    # =========================================================================
    def setup_top_nav(self):
        c = self.get_theme_colors()
        self.nav_header = ctk.CTkFrame(self, height=66, fg_color=c["bg_primary"], corner_radius=0, border_width=1, border_color=c["card_border"])
        self.nav_header.grid(row=0, column=0, sticky="ew")
        self.nav_header.grid_propagate(False)

        # Brand Wrapper
        brand_frame = ctk.CTkFrame(self.nav_header, fg_color="transparent")
        brand_frame.pack(side="left", padx=(25, 15), pady=12)

        logo_lbl = ctk.CTkLabel(brand_frame, text="⚡", font=self.scaled_font(20))
        logo_lbl.pack(side="left", padx=(0, 6))

        self.brand_lbl = ctk.CTkLabel(
            brand_frame,
            text="QuizSphere",
            font=self.scaled_font(18, weight="bold"),
            text_color=c["text_primary"]
        )
        self.brand_lbl.pack(side="left")

        self.pro_badge = ctk.CTkLabel(
            brand_frame,
            text="Pro 2.0",
            font=self.scaled_font(10, weight="bold"),
            text_color=c["badge_cyan_text"],
            fg_color=c["badge_cyan_bg"],
            corner_radius=6,
            padx=7,
            pady=2
        )
        self.pro_badge.pack(side="left", padx=(8, 0))

        # Center Navigation Tabs (Role Switcher)
        self.nav_tabs_frame = ctk.CTkFrame(self.nav_header, fg_color=c["bg_card_secondary"], corner_radius=8, border_width=1, border_color=c["card_border"])
        self.nav_tabs_frame.pack(side="left", padx=20, pady=12)

        self.tab_candidate_btn = ctk.CTkButton(
            self.nav_tabs_frame,
            text="🎓 Candidate Arena",
            font=self.scaled_font(12, weight="bold"),
            fg_color=c["accent_primary"],
            hover_color="#3730a3",
            text_color="#ffffff",
            corner_radius=6,
            height=34,
            command=lambda: self.switch_nav_view("candidate-arena")
        )
        self.tab_candidate_btn.pack(side="left", padx=3, pady=3)

        self.tab_examiner_btn = ctk.CTkButton(
            self.nav_tabs_frame,
            text="🛠️ Examiner Studio",
            font=self.scaled_font(12, weight="bold"),
            fg_color="transparent",
            hover_color=c["bg_card_hover"],
            text_color=c["text_secondary"],
            corner_radius=6,
            height=34,
            command=lambda: self.switch_nav_view("examiner-studio")
        )
        self.tab_examiner_btn.pack(side="left", padx=3, pady=3)

        # Right Controls: Accessibility, Theme & Session
        controls_frame = ctk.CTkFrame(self.nav_header, fg_color="transparent")
        controls_frame.pack(side="right", padx=(10, 25), pady=12)

        self.theme_btn = ctk.CTkButton(
            controls_frame,
            text="☀️ Light" if self.current_theme == "light" else "🌙 Dark",
            width=76,
            height=34,
            font=self.scaled_font(11, weight="bold"),
            fg_color=c["btn_neutral"],
            text_color=c["btn_neutral_text"],
            hover_color=c["btn_neutral_hover"],
            command=self.toggle_appearance_mode
        )
        self.theme_btn.pack(side="left", padx=3)

        self.contrast_btn = ctk.CTkButton(
            controls_frame,
            text="👁️ Contrast",
            width=84,
            height=34,
            font=self.scaled_font(11, weight="bold"),
            fg_color=c["btn_neutral"],
            text_color=c["btn_neutral_text"],
            hover_color=c["btn_neutral_hover"],
            command=self.toggle_high_contrast
        )
        self.contrast_btn.pack(side="left", padx=3)

        self.font_down_btn = ctk.CTkButton(
            controls_frame,
            text="A-",
            width=38,
            height=34,
            font=self.scaled_font(11, weight="bold"),
            fg_color=c["btn_neutral"],
            text_color=c["btn_neutral_text"],
            hover_color=c["btn_neutral_hover"],
            command=lambda: self.adjust_font_scale(-0.1)
        )
        self.font_down_btn.pack(side="left", padx=2)

        self.font_up_btn = ctk.CTkButton(
            controls_frame,
            text="A+",
            width=38,
            height=34,
            font=self.scaled_font(11, weight="bold"),
            fg_color=c["btn_neutral"],
            text_color=c["btn_neutral_text"],
            hover_color=c["btn_neutral_hover"],
            command=lambda: self.adjust_font_scale(0.1)
        )
        self.font_up_btn.pack(side="left", padx=2)

        self.focus_btn = ctk.CTkButton(
            controls_frame,
            text="🎯 Focus",
            width=76,
            height=34,
            font=self.scaled_font(11, weight="bold"),
            fg_color=c["btn_neutral"],
            text_color=c["btn_neutral_text"],
            hover_color=c["btn_neutral_hover"],
            command=self.toggle_minimalist_mode
        )
        self.focus_btn.pack(side="left", padx=3)

        # Candidate Name Pill
        self.user_chip_btn = ctk.CTkButton(
            controls_frame,
            text=f"👤 {self.student_name}",
            height=34,
            font=self.scaled_font(11, weight="bold"),
            fg_color=c["badge_cyan_bg"],
            text_color=c["badge_cyan_text"],
            hover_color=c["badge_cyan_bg"],
            command=self.prompt_change_candidate_name
        )
        self.user_chip_btn.pack(side="left", padx=(6, 0))

    def setup_workspace(self):
        c = self.get_theme_colors()
        self.workspace = ctk.CTkFrame(self, fg_color=c["bg_primary"], corner_radius=0)
        self.workspace.grid(row=1, column=0, sticky="nsew")

    def clear_workspace(self):
        for w in self.workspace.winfo_children():
            w.destroy()

    def switch_nav_view(self, view_name):
        self.current_nav_view = view_name
        c = self.get_theme_colors()
        active_color = c["accent_primary"]

        # Update top tab buttons
        if view_name == "candidate-arena":
            self.tab_candidate_btn.configure(fg_color=active_color, text_color="#ffffff")
            self.tab_examiner_btn.configure(fg_color="transparent", text_color=c["text_secondary"])
            self.render_candidate_arena()
        elif view_name == "examiner-studio":
            self.tab_examiner_btn.configure(fg_color=active_color, text_color="#ffffff")
            self.tab_candidate_btn.configure(fg_color="transparent", text_color=c["text_secondary"])
            self.render_examiner_studio()
        elif view_name == "exam-arena":
            self.tab_candidate_btn.configure(fg_color=active_color, text_color="#ffffff")
            self.tab_examiner_btn.configure(fg_color="transparent", text_color=c["text_secondary"])
            self.render_exam_arena()
        elif view_name == "result-scorecard":
            self.tab_candidate_btn.configure(fg_color=active_color, text_color="#ffffff")
            self.tab_examiner_btn.configure(fg_color="transparent", text_color=c["text_secondary"])
            self.render_result_scorecard()

    def prompt_change_candidate_name(self):
        dialog = ctk.CTkInputDialog(text="Enter Candidate Name for Certificates & Submissions:", title="Candidate Profile")
        name = dialog.get_input()
        if name and name.strip():
            self.student_name = name.strip()
            self.user_chip_btn.configure(text=f"👤 {self.student_name}")

    # =========================================================================
    # VIEW 1: CANDIDATE ARENA (Student Catalog & Quick Join)
    # =========================================================================
    def render_candidate_arena(self):
        self.clear_workspace()
        c = self.get_theme_colors()

        scroll = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=40, pady=(20, 30))

        # Hero Header Row
        header_row = ctk.CTkFrame(scroll, fg_color="transparent")
        header_row.pack(fill="x", pady=(10, 20))

        left_hero = ctk.CTkFrame(header_row, fg_color="transparent")
        left_hero.pack(side="left", fill="y", anchor="w")

        engine_badge = ctk.CTkLabel(
            left_hero,
            text="Cross-Platform Assessment Engine",
            font=self.scaled_font(10, weight="bold"),
            text_color=c["badge_cyan_text"],
            fg_color=c["badge_cyan_bg"],
            corner_radius=6,
            padx=8,
            pady=3
        )
        engine_badge.pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            left_hero,
            text="Explore Available Quizzes",
            font=self.scaled_font(26, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_hero,
            text="Select an assessment to begin your timed, proctored evaluation.",
            font=self.scaled_font(13),
            text_color=c["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # Real-time search box on the right of header
        right_search = ctk.CTkFrame(header_row, fg_color="transparent")
        right_search.pack(side="right", anchor="e", pady=(10, 0))

        self.search_entry = ctk.CTkEntry(
            right_search,
            placeholder_text="🔍 Search assessments or topics...",
            width=320,
            height=40,
            font=self.scaled_font(12),
            fg_color=c["bg_card"],
            text_color=c["text_primary"],
            border_color=c["card_border"]
        )
        self.search_entry.pack(side="right")
        self.search_entry.bind("<KeyRelease>", lambda e: self.filter_quiz_cards())

        # Quick Join by Quiz Code Banner
        join_banner = ctk.CTkFrame(scroll, fg_color=c["bg_card"], corner_radius=12, border_width=1, border_color=c["card_border"])
        join_banner.pack(fill="x", pady=(0, 25))

        banner_inner = ctk.CTkFrame(join_banner, fg_color="transparent")
        banner_inner.pack(fill="x", padx=24, pady=18)

        left_info = ctk.CTkFrame(banner_inner, fg_color="transparent")
        left_info.pack(side="left", fill="both", expand=True)

        ctk.CTkLabel(
            left_info,
            text="🔑 Have a Quiz Code from your Teacher?",
            font=self.scaled_font(15, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_info,
            text="Enter the 6-character code (e.g. QZ-1001) to load your class assessment.",
            font=self.scaled_font(12),
            text_color=c["text_secondary"]
        ).pack(anchor="w", pady=(3, 0))

        right_join = ctk.CTkFrame(banner_inner, fg_color="transparent")
        right_join.pack(side="right")

        self.join_input = ctk.CTkEntry(
            right_join,
            placeholder_text="e.g. QZ-1001",
            width=160,
            height=40,
            font=self.scaled_font(13, weight="bold"),
            justify="center",
            fg_color=c["bg_card_secondary"],
            text_color=c["text_primary"],
            border_color=c["card_border"]
        )
        self.join_input.pack(side="left", padx=(0, 10))

        join_btn = ctk.CTkButton(
            right_join,
            text="Join Quiz 🚀",
            width=130,
            height=40,
            font=self.scaled_font(13, weight="bold"),
            fg_color=c["btn_cyan"],
            hover_color="#0369a1",
            text_color=c["btn_cyan_text"],
            command=self.handle_join_quiz_code
        )
        join_btn.pack(side="left")

        # Quizzes Grid Container
        self.cards_container = ctk.CTkFrame(scroll, fg_color="transparent")
        self.cards_container.pack(fill="both", expand=True)

        self.all_quizzes_cache = self.db.get_all_quizzes()
        self.render_quiz_cards_list(self.all_quizzes_cache)

    def filter_quiz_cards(self):
        query = self.search_entry.get().strip().lower()
        if not query:
            filtered = self.all_quizzes_cache
        else:
            filtered = [
                q for q in self.all_quizzes_cache
                if query in q["title"].lower() or query in q.get("category", "").lower() or query in q.get("description", "").lower()
            ]
        self.render_quiz_cards_list(filtered)

    def render_quiz_cards_list(self, quizzes):
        for w in self.cards_container.winfo_children():
            w.destroy()

        if not quizzes:
            ctk.CTkLabel(
                self.cards_container,
                text="No assessments matched your query.",
                font=self.scaled_font(14),
                text_color="#94a3b8"
            ).pack(pady=40)
            return

        c = self.get_theme_colors()

        # Render 2 columns of rich cards
        for q in quizzes:
            card = ctk.CTkFrame(
                self.cards_container,
                fg_color=c["bg_card"],
                corner_radius=12,
                border_width=c["border_width"],
                border_color=c["card_border"]
            )
            card.pack(fill="x", pady=8, padx=4)

            inner = ctk.CTkFrame(card, fg_color="transparent")
            inner.pack(fill="x", padx=22, pady=18)

            # Tags row
            tags_row = ctk.CTkFrame(inner, fg_color="transparent")
            tags_row.pack(fill="x", pady=(0, 6))

            cat_badge = ctk.CTkLabel(
                tags_row,
                text=q.get("category", "Engineering"),
                font=self.scaled_font(10, weight="bold"),
                text_color=c["badge_cyan_text"],
                fg_color=c["badge_cyan_bg"],
                corner_radius=6,
                padx=8,
                pady=2
            )
            cat_badge.pack(side="left", padx=(0, 6))

            for tag in q.get("tags", [])[:2]:
                ctk.CTkLabel(
                    tags_row,
                    text=tag,
                    font=self.scaled_font(10, weight="bold"),
                    text_color=c["badge_indigo_text"],
                    fg_color=c["badge_indigo_bg"],
                    corner_radius=6,
                    padx=8,
                    pady=2
                ).pack(side="left", padx=4)

            # Code badge on the right
            ctk.CTkLabel(
                tags_row,
                text=f"Code: {q['joinCode']}",
                font=self.scaled_font(11, weight="bold"),
                text_color=c["badge_cyan_text"],
                fg_color=c["badge_cyan_bg"],
                corner_radius=6,
                padx=8,
                pady=2
            ).pack(side="right")

            # Title & Description
            ctk.CTkLabel(
                inner,
                text=q["title"],
                font=self.scaled_font(17, weight="bold"),
                text_color=c["text_primary"],
                anchor="w"
            ).pack(fill="x", pady=(4, 4))

            ctk.CTkLabel(
                inner,
                text=q.get("description", "Test your proficiency with challenging questions."),
                font=self.scaled_font(12),
                text_color=c["text_secondary"],
                anchor="w",
                wraplength=800
            ).pack(fill="x", pady=(0, 10))

            # Info chips & Action button row
            bottom_row = ctk.CTkFrame(inner, fg_color="transparent")
            bottom_row.pack(fill="x", pady=(4, 0))

            chips_box = ctk.CTkFrame(bottom_row, fg_color="transparent")
            chips_box.pack(side="left", fill="y")

            chips_info = [
                f"❓ {len(q['questions'])} Questions",
                f"⏱️ {q['durationMinutes']} Minutes",
                f"🎯 Pass: {q['passingScore']}%"
            ]
            for chip_text in chips_info:
                chip_lbl = ctk.CTkLabel(
                    chips_box,
                    text=chip_text,
                    font=self.scaled_font(11, weight="bold"),
                    text_color=c["text_secondary"],
                    fg_color=c["bg_card_secondary"],
                    corner_radius=6,
                    padx=9,
                    pady=4
                )
                chip_lbl.pack(side="left", padx=(0, 8))

            start_btn = ctk.CTkButton(
                bottom_row,
                text="Start Assessment ⚡",
                font=self.scaled_font(12, weight="bold"),
                fg_color=c["accent_primary"],
                hover_color="#4338ca",
                text_color="#ffffff",
                height=36,
                corner_radius=8,
                command=lambda quiz=q: self.open_readiness_modal(quiz)
            )
            start_btn.pack(side="right")

    def handle_join_quiz_code(self):
        code = self.join_input.get().strip().upper()
        if not code:
            messagebox.showwarning("Quiz Code", "Please enter a valid 6-character Quiz Code.")
            return
        quiz = self.db.get_quiz_by_code(code)
        if not quiz:
            messagebox.showerror("Not Found", f"No assessment found matching Quiz Code: {code}")
            return
        self.open_readiness_modal(quiz)

    # =========================================================================
    # VIEW 2: READINESS CHECK MODAL (Mirrors Web Readiness Modal)
    # =========================================================================
    def open_readiness_modal(self, quiz):
        c = self.get_theme_colors()

        modal = ctk.CTkToplevel(self)
        modal.title("Assessment Readiness Check")
        modal.geometry("560x520")
        modal.transient(self)
        modal.grab_set()
        modal.configure(fg_color=c["bg_primary"])

        content = ctk.CTkFrame(modal, fg_color=c["bg_card"], corner_radius=16, border_width=c["border_width"], border_color=c["card_border"])
        content.pack(fill="both", expand=True, padx=25, pady=25)

        # Header
        ctk.CTkLabel(
            content,
            text="⚡ Assessment Readiness Check",
            font=self.scaled_font(18, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w", padx=25, pady=(20, 4))

        ctk.CTkLabel(
            content,
            text=f"Selected: {quiz['title']}",
            font=self.scaled_font(13),
            text_color=c["text_cyan"]
        ).pack(anchor="w", padx=25, pady=(0, 15))

        # Metadata Chips
        meta_row = ctk.CTkFrame(content, fg_color=c["bg_card_secondary"], corner_radius=8)
        meta_row.pack(fill="x", padx=25, pady=(0, 15))

        ctk.CTkLabel(meta_row, text=f"⏱️ Duration: {quiz['durationMinutes']} Mins", font=self.scaled_font(11, weight="bold"), text_color=c["text_primary"]).pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(meta_row, text=f"🎯 Pass: {quiz['passingScore']}%", font=self.scaled_font(11, weight="bold"), text_color=c["text_primary"]).pack(side="left", padx=12, pady=8)
        ctk.CTkLabel(meta_row, text=f"❓ Items: {len(quiz['questions'])}", font=self.scaled_font(11, weight="bold"), text_color=c["text_primary"]).pack(side="left", padx=12, pady=8)

        # Candidate Name Entry
        ctk.CTkLabel(
            content,
            text="Candidate Legal Name:",
            font=self.scaled_font(12, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w", padx=25, pady=(0, 4))

        name_in = ctk.CTkEntry(content, height=38, font=self.scaled_font(13), fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
        name_in.insert(0, self.student_name)
        name_in.pack(fill="x", padx=25, pady=(0, 15))

        # Proctoring & Anti-Cheat Rules Box
        rules_box = ctk.CTkFrame(content, fg_color=c["bg_card_secondary"], corner_radius=10, border_width=1, border_color=c["card_border"])
        rules_box.pack(fill="x", padx=25, pady=(0, 20))

        ctk.CTkLabel(
            rules_box,
            text="🛡️ Proctoring & Security Rules",
            font=self.scaled_font(12, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w", padx=15, pady=(10, 4))

        rules = [
            "• Do not switch application windows or minimize during the exam.",
            "• Window blur events are logged as proctor violations.",
            "• Answers are autosaved with monotonic revision tracking.",
            "• Time is strictly server-authoritative; exam auto-submits on timeout."
        ]
        for r in rules:
            ctk.CTkLabel(
                rules_box,
                text=r,
                font=self.scaled_font(11),
                text_color=c["text_secondary"],
                anchor="w"
            ).pack(anchor="w", padx=15, pady=1)

        # Buttons Row
        btns_row = ctk.CTkFrame(content, fg_color="transparent")
        btns_row.pack(fill="x", padx=25, pady=(10, 20))

        def on_begin():
            custom_name = name_in.get().strip()
            if custom_name:
                self.student_name = custom_name
                self.user_chip_btn.configure(text=f"👤 {self.student_name}")
            modal.destroy()
            self.start_live_exam(quiz)

        begin_btn = ctk.CTkButton(
            btns_row,
            text="Begin Examination ⚡",
            font=self.scaled_font(13, weight="bold"),
            fg_color=c["btn_cyan"],
            hover_color="#0369a1",
            text_color=c["btn_cyan_text"],
            height=40,
            command=on_begin
        )
        begin_btn.pack(side="right", padx=(10, 0))

        cancel_btn = ctk.CTkButton(
            btns_row,
            text="Cancel",
            font=self.scaled_font(13),
            fg_color=c["btn_neutral"],
            hover_color=c["btn_neutral_hover"],
            text_color=c["btn_neutral_text"],
            height=40,
            command=modal.destroy
        )
        cancel_btn.pack(side="right")

    # =========================================================================
    # VIEW 3: LIVE EXAM ARENA (Timer, Question Card, Palette, Hotkeys)
    # =========================================================================
    def start_live_exam(self, quiz):
        self.active_quiz = quiz
        self.current_q_index = 0
        self.user_answers = {}
        self.review_flags = set()
        self.cheat_violations = 0
        self.time_left_seconds = quiz["durationMinutes"] * 60
        self.timer_running = True

        self.switch_nav_view("exam-arena")
        self.run_timer_tick()

    def run_timer_tick(self):
        if not self.timer_running or self.current_nav_view != "exam-arena":
            return

        if self.time_left_seconds <= 0:
            self.timer_running = False
            messagebox.showinfo("Time Expired", "Exam time has expired! Finalizing assessment submission...")
            self.finalize_exam_submission()
            return

        mins = self.time_left_seconds // 60
        secs = self.time_left_seconds % 60
        timer_text = f"⏱️ {mins:02d}:{secs:02d}"

        if hasattr(self, "exam_timer_lbl") and self.exam_timer_lbl.winfo_exists():
            self.exam_timer_lbl.configure(text=timer_text)
            # Urgency state: turn red when < 60s
            if self.time_left_seconds <= 60:
                self.exam_timer_lbl.configure(text_color="#ef4444")
            else:
                self.exam_timer_lbl.configure(text_color="#38bdf8")

        self.time_left_seconds -= 1
        self.after(1000, self.run_timer_tick)

    def render_exam_arena(self):
        self.clear_workspace()
        c = self.get_theme_colors()

        if not self.active_quiz:
            self.switch_nav_view("candidate-arena")
            return

        q = self.active_quiz["questions"][self.current_q_index]
        total_q = len(self.active_quiz["questions"])

        # Main Exam Container
        exam_container = ctk.CTkFrame(self.workspace, fg_color="transparent")
        exam_container.pack(fill="both", expand=True, padx=30, pady=(15, 15))

        # Top Exam Bar
        top_bar = ctk.CTkFrame(exam_container, fg_color=c["bg_card"], corner_radius=10, border_width=c["border_width"], border_color=c["card_border"], height=58)
        top_bar.pack(fill="x", pady=(0, 15))
        top_bar.pack_propagate(False)

        top_inner = ctk.CTkFrame(top_bar, fg_color="transparent")
        top_inner.pack(fill="both", expand=True, padx=20, pady=10)

        # Left: Quiz Title & Question Index
        left_meta = ctk.CTkFrame(top_inner, fg_color="transparent")
        left_meta.pack(side="left", fill="y")

        ctk.CTkLabel(
            left_meta,
            text=f"Question {self.current_q_index + 1} of {total_q}",
            font=self.scaled_font(13, weight="bold"),
            text_color=c["text_cyan"]
        ).pack(side="left", padx=(0, 12))

        ctk.CTkLabel(
            left_meta,
            text=f"|  {self.active_quiz['title']}",
            font=self.scaled_font(13),
            text_color=c["text_primary"]
        ).pack(side="left")

        # Right: Timer & Submit
        right_tools = ctk.CTkFrame(top_inner, fg_color="transparent")
        right_tools.pack(side="right")

        mins = self.time_left_seconds // 60
        secs = self.time_left_seconds % 60
        self.exam_timer_lbl = ctk.CTkLabel(
            right_tools,
            text=f"⏱️ {mins:02d}:{secs:02d}",
            font=self.scaled_font(14, weight="bold"),
            text_color="#ef4444" if self.time_left_seconds <= 60 else c["badge_cyan_text"],
            fg_color=c["badge_cyan_bg"],
            corner_radius=6,
            padx=12,
            pady=4
        )
        self.exam_timer_lbl.pack(side="left", padx=(0, 10))

        is_marked = q["id"] in self.review_flags
        self.review_btn = ctk.CTkButton(
            right_tools,
            text="★ Marked for Review" if is_marked else "☆ Mark for Review",
            font=self.scaled_font(11, weight="bold"),
            fg_color="#f59e0b" if is_marked else c["btn_neutral"],
            hover_color="#d97706" if is_marked else c["btn_neutral_hover"],
            text_color="#000000" if is_marked else c["btn_neutral_text"],
            height=34,
            command=self.toggle_review_flag
        )
        self.review_btn.pack(side="left", padx=(0, 10))

        submit_btn = ctk.CTkButton(
            right_tools,
            text="Finish & Review →",
            font=self.scaled_font(12, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            height=34,
            command=self.confirm_exam_submission
        )
        submit_btn.pack(side="left")

        # Split Body (Question Card Column vs Palette Matrix Column)
        body_split = ctk.CTkFrame(exam_container, fg_color="transparent")
        body_split.pack(fill="both", expand=True)

        # Question Column
        q_col = ctk.CTkScrollableFrame(
            body_split,
            fg_color=c["bg_card"],
            corner_radius=12,
            border_width=c["border_width"],
            border_color=c["card_border"]
        )
        q_col.pack(side="left", fill="both", expand=True, padx=(0, 0 if self.minimalist_focus_mode else 15))

        q_inner = ctk.CTkFrame(q_col, fg_color="transparent")
        q_inner.pack(fill="both", expand=True, padx=25, pady=22)

        # Question Prompt
        ctk.CTkLabel(
            q_inner,
            text=f"{self.current_q_index + 1}.  {q['text']}",
            font=self.scaled_font(17, weight="bold"),
            text_color=c["text_primary"],
            anchor="w",
            justify="left",
            wraplength=760 if not self.minimalist_focus_mode else 1050
        ).pack(fill="x", pady=(0, 14))

        # Code block (if present)
        if q.get("code"):
            code_card = ctk.CTkFrame(q_inner, fg_color=c["code_bg"], corner_radius=8, border_width=1, border_color=c["card_border"])
            code_card.pack(fill="x", pady=(0, 16))
            ctk.CTkLabel(
                code_card,
                text=q["code"],
                font=ctk.CTkFont(family="Consolas", size=13),
                text_color=c["code_text"],
                justify="left",
                anchor="w",
                padx=16,
                pady=12
            ).pack(fill="x")

        # Options Cards
        letters = ["A", "B", "C", "D", "E", "F"]
        current_selection = self.user_answers.get(q["id"])

        for idx, opt_text in enumerate(q["options"]):
            is_selected = current_selection == idx
            opt_frame = ctk.CTkFrame(
                q_inner,
                fg_color=c["option_selected_bg"] if is_selected else c["bg_card"],
                corner_radius=8,
                border_width=2 if is_selected else 1,
                border_color="#4f46e5" if is_selected else c["card_border"]
            )
            opt_frame.pack(fill="x", pady=6)

            opt_row = ctk.CTkFrame(opt_frame, fg_color="transparent")
            opt_row.pack(fill="x", padx=16, pady=12)

            # Circular marker
            marker = ctk.CTkLabel(
                opt_row,
                text=letters[idx] if idx < len(letters) else str(idx + 1),
                font=self.scaled_font(12, weight="bold"),
                text_color="#ffffff" if is_selected else c["text_secondary"],
                fg_color="#4f46e5" if is_selected else c["bg_card_secondary"],
                corner_radius=12,
                width=28,
                height=28
            )
            marker.pack(side="left", padx=(0, 14))

            # Option text
            opt_lbl = ctk.CTkLabel(
                opt_row,
                text=opt_text,
                font=self.scaled_font(14, weight="bold" if is_selected else "normal"),
                text_color=c["text_primary"],
                anchor="w",
                justify="left"
            )
            opt_lbl.pack(side="left", fill="x", expand=True)

            # Hotkey badge
            hotkey_chip = ctk.CTkLabel(
                opt_row,
                text=f"[{idx + 1} / {letters[idx]}]",
                font=self.scaled_font(10, weight="bold"),
                text_color=c["text_dim"]
            )
            hotkey_chip.pack(side="right")

            # Click binding
            for w in [opt_frame, opt_row, marker, opt_lbl, hotkey_chip]:
                w.bind("<Button-1>", lambda e, opt_idx=idx: self.handle_option_selection(opt_idx))

        # Prev / Next Navigation Row
        nav_row = ctk.CTkFrame(q_inner, fg_color="transparent")
        nav_row.pack(fill="x", pady=(22, 10))

        prev_btn = ctk.CTkButton(
            nav_row,
            text="← Previous Question",
            font=self.scaled_font(12, weight="bold"),
            fg_color=c["btn_neutral"],
            hover_color=c["btn_neutral_hover"],
            text_color=c["btn_neutral_text"],
            state="normal" if self.current_q_index > 0 else "disabled",
            height=38,
            command=lambda: self.navigate_question(-1)
        )
        prev_btn.pack(side="left")

        next_btn = ctk.CTkButton(
            nav_row,
            text="Finish & Review" if self.current_q_index == total_q - 1 else "Next Question →",
            font=self.scaled_font(12, weight="bold"),
            fg_color="#4f46e5",
            hover_color="#4338ca",
            text_color="#ffffff",
            height=38,
            command=lambda: self.navigate_question(1)
        )
        next_btn.pack(side="right")

        # Palette Column (Collapsed in Minimalist Mode)
        if not self.minimalist_focus_mode:
            palette_frame = ctk.CTkFrame(
                body_split,
                fg_color=c["bg_card"],
                corner_radius=12,
                border_width=c["border_width"],
                border_color=c["card_border"],
                width=260
            )
            palette_frame.pack(side="right", fill="y")
            palette_frame.pack_propagate(False)

            p_inner = ctk.CTkFrame(palette_frame, fg_color="transparent")
            p_inner.pack(fill="both", expand=True, padx=16, pady=16)

            ctk.CTkLabel(
                p_inner,
                text="Question Palette",
                font=self.scaled_font(13, weight="bold"),
                text_color=c["text_primary"]
            ).pack(anchor="w", pady=(0, 12))

            grid_box = ctk.CTkFrame(p_inner, fg_color="transparent")
            grid_box.pack(fill="x", pady=(0, 16))

            cols = 4
            for i, question in enumerate(self.active_quiz["questions"]):
                row_idx = i // cols
                col_idx = i % cols

                # Determine badge color
                if i == self.current_q_index:
                    btn_color = c["palette_current"]
                    btn_text_color = "#ffffff"
                elif question["id"] in self.user_answers:
                    btn_color = c["palette_answered"]
                    btn_text_color = "#ffffff"
                elif question["id"] in self.review_flags:
                    btn_color = c["palette_review"]
                    btn_text_color = "#000000"
                else:
                    btn_color = c["palette_unanswered"]
                    btn_text_color = c["palette_unanswered_text"]

                p_btn = ctk.CTkButton(
                    grid_box,
                    text=str(i + 1),
                    width=46,
                    height=38,
                    corner_radius=8,
                    font=self.scaled_font(12, weight="bold"),
                    fg_color=btn_color,
                    text_color=btn_text_color,
                    hover_color="#0369a1",
                    command=lambda target_idx=i: self.jump_to_question(target_idx)
                )
                p_btn.grid(row=row_idx, column=col_idx, padx=3, pady=3)

            # Palette Legend
            legend_box = ctk.CTkFrame(p_inner, fg_color=c["bg_card_secondary"], corner_radius=8)
            legend_box.pack(fill="x", side="bottom", pady=(10, 0))

            legends = [
                ("● Answered", "#10b981"),
                ("● Marked for Review", "#f59e0b"),
                ("● Current Question", "#4f46e5"),
                ("● Unanswered", c["text_dim"])
            ]
            for leg_text, leg_color in legends:
                ctk.CTkLabel(
                    legend_box,
                    text=leg_text,
                    font=self.scaled_font(10, weight="bold"),
                    text_color=leg_color
                ).pack(anchor="w", padx=12, pady=2)

        # Bottom Shortcut Strip
        shortcut_strip = ctk.CTkFrame(exam_container, fg_color=c["bg_card"], corner_radius=8, height=36)
        shortcut_strip.pack(fill="x", pady=(12, 0))
        shortcut_strip.pack_propagate(False)

        legend_text = "[1-4 / A-D] Select Option   |   [← / P] Previous   |   [→ / N] Next   |   [M] Mark Review   |   [S] Submit   |   [F] Minimalist Focus"
        ctk.CTkLabel(
            shortcut_strip,
            text=legend_text,
            font=self.scaled_font(11, weight="bold"),
            text_color="#94a3b8"
        ).pack(side="left", padx=16, pady=8)

    def handle_option_selection(self, opt_idx):
        if not self.active_quiz:
            return
        q_id = self.active_quiz["questions"][self.current_q_index]["id"]
        self.user_answers[q_id] = opt_idx
        self.render_exam_arena()

    def toggle_review_flag(self):
        if not self.active_quiz:
            return
        q_id = self.active_quiz["questions"][self.current_q_index]["id"]
        if q_id in self.review_flags:
            self.review_flags.remove(q_id)
        else:
            self.review_flags.add(q_id)
        self.render_exam_arena()

    def navigate_question(self, direction):
        if not self.active_quiz:
            return
        target = self.current_q_index + direction
        total_q = len(self.active_quiz["questions"])
        if 0 <= target < total_q:
            self.current_q_index = target
            self.render_exam_arena()
        elif target >= total_q:
            self.confirm_exam_submission()

    def jump_to_question(self, index):
        if self.active_quiz and 0 <= index < len(self.active_quiz["questions"]):
            self.current_q_index = index
            self.render_exam_arena()

    def confirm_exam_submission(self):
        total_q = len(self.active_quiz["questions"])
        answered_q = len(self.user_answers)
        unanswered = total_q - answered_q

        msg = f"Are you sure you want to finalize your exam?\n\n• Total Questions: {total_q}\n• Answered: {answered_q}\n• Unanswered: {unanswered}\n• Proctor Violations: {self.cheat_violations}"
        if messagebox.askyesno("Confirm Final Submission", msg):
            self.finalize_exam_submission()

    def finalize_exam_submission(self):
        self.timer_running = False
        quiz = self.active_quiz
        questions = quiz["questions"]

        # Deterministic grading
        score = 0
        review_details = []
        for idx, q in enumerate(questions):
            q_id = q["id"]
            user_sel = self.user_answers.get(q_id)
            correct_idx = q["correct"]
            is_correct = (user_sel == correct_idx)
            if is_correct:
                score += 1

            review_details.append({
                "index": idx + 1,
                "text": q["text"],
                "options": q["options"],
                "userSelection": user_sel,
                "correctSelection": correct_idx,
                "isCorrect": is_correct,
                "explanation": q.get("explanation", "")
            })

        total = len(questions)
        percentage = round((score / total) * 100) if total > 0 else 0
        passed = percentage >= quiz["passingScore"]

        attempt_record = {
            "id": f"att-{int(time.time() * 1000)}",
            "quizId": quiz["id"],
            "joinCode": quiz["joinCode"],
            "quizTitle": quiz["title"],
            "teacherName": quiz["teacherName"],
            "studentName": self.student_name,
            "score": score,
            "totalQuestions": total,
            "percentage": percentage,
            "passed": passed,
            "cheatViolations": self.cheat_violations
        }
        self.db.record_attempt(attempt_record)

        self.last_attempt_result = {
            "attempt": attempt_record,
            "review": review_details
        }
        self.active_quiz = None
        self.switch_nav_view("result-scorecard")

    # =========================================================================
    # VIEW 4: RESULT SCORECARD & DETAILED EXPLANATIONS (Mirrors Web Result)
    # =========================================================================
    def render_result_scorecard(self):
        self.clear_workspace()
        c = self.get_theme_colors()

        if not self.last_attempt_result:
            self.switch_nav_view("candidate-arena")
            return

        attempt = self.last_attempt_result["attempt"]
        reviews = self.last_attempt_result["review"]

        scroll = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=40, pady=(20, 30))

        # Result Summary Card
        card = ctk.CTkFrame(
            scroll,
            fg_color=c["bg_card"],
            corner_radius=16,
            border_width=c["border_width"],
            border_color=c["card_border"]
        )
        card.pack(fill="x", pady=(10, 20))

        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=30, pady=25)

        # Status badge
        is_passed = attempt["passed"]
        status_badge = ctk.CTkLabel(
            inner,
            text="PASSED 🏆" if is_passed else "NEEDS IMPROVEMENT",
            font=self.scaled_font(12, weight="bold"),
            text_color="#ffffff",
            fg_color="#10b981" if is_passed else "#ef4444",
            corner_radius=8,
            padx=14,
            pady=4
        )
        status_badge.pack(anchor="w", pady=(0, 6))

        ctk.CTkLabel(
            inner,
            text=attempt["quizTitle"],
            font=self.scaled_font(22, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            inner,
            text=f"Candidate: {attempt['studentName']}   |   Evaluator: {attempt['teacherName']}",
            font=self.scaled_font(13),
            text_color=c["text_secondary"]
        ).pack(anchor="w", pady=(2, 16))

        # Score Gauge Box
        gauge_box = ctk.CTkFrame(inner, fg_color=c["bg_card_secondary"], corner_radius=12)
        gauge_box.pack(fill="x", pady=(0, 18))

        g_inner = ctk.CTkFrame(gauge_box, fg_color="transparent")
        g_inner.pack(fill="x", padx=25, pady=16)

        ctk.CTkLabel(
            g_inner,
            text=f"{attempt['percentage']}%",
            font=self.scaled_font(36, weight="bold"),
            text_color="#10b981" if is_passed else "#ef4444"
        ).pack(side="left", padx=(0, 20))

        stats_meta = f"Score: {attempt['score']} / {attempt['totalQuestions']} Correct Points\nPassing Standard: 70%\nProctor Violations: {attempt['cheatViolations']}"
        ctk.CTkLabel(
            g_inner,
            text=stats_meta,
            font=self.scaled_font(13),
            text_color=c["text_primary"],
            justify="left"
        ).pack(side="left")

        # Action Buttons
        act_row = ctk.CTkFrame(inner, fg_color="transparent")
        act_row.pack(fill="x")

        back_btn = ctk.CTkButton(
            act_row,
            text="Return to Candidate Arena 🎓",
            font=self.scaled_font(13, weight="bold"),
            fg_color="#4f46e5",
            hover_color="#4338ca",
            text_color="#ffffff",
            height=40,
            command=lambda: self.switch_nav_view("candidate-arena")
        )
        back_btn.pack(side="left", padx=(0, 10))

        export_btn = ctk.CTkButton(
            act_row,
            text="Export Gradebook CSV 📥",
            font=self.scaled_font(13),
            fg_color=c["btn_neutral"],
            hover_color=c["btn_neutral_hover"],
            text_color=c["btn_neutral_text"],
            height=40,
            command=self.handle_export_csv
        )
        export_btn.pack(side="left")

        # Question-by-Question Review Header
        ctk.CTkLabel(
            scroll,
            text="Detailed Question Review & Explanations:",
            font=self.scaled_font(18, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w", pady=(15, 12))

        # Review Cards
        for item in reviews:
            rev_card = ctk.CTkFrame(
                scroll,
                fg_color=c["bg_card"],
                corner_radius=10,
                border_width=1,
                border_color="#10b981" if item["isCorrect"] else "#ef4444"
            )
            rev_card.pack(fill="x", pady=8)

            r_inner = ctk.CTkFrame(rev_card, fg_color="transparent")
            r_inner.pack(fill="x", padx=20, pady=16)

            # Header row
            r_top = ctk.CTkFrame(r_inner, fg_color="transparent")
            r_top.pack(fill="x", pady=(0, 6))

            ctk.CTkLabel(
                r_top,
                text=f"Question {item['index']}",
                font=self.scaled_font(14, weight="bold"),
                text_color=c["text_primary"]
            ).pack(side="left")

            badge_text = "Correct ✅" if item["isCorrect"] else ("Skipped ⚠️" if item["userSelection"] is None else "Incorrect ❌")
            badge_color = "#10b981" if item["isCorrect"] else ("#f59e0b" if item["userSelection"] is None else "#ef4444")
            ctk.CTkLabel(
                r_top,
                text=badge_text,
                font=self.scaled_font(11, weight="bold"),
                text_color=badge_color,
                fg_color=c["bg_card_secondary"],
                corner_radius=6,
                padx=8,
                pady=2
            ).pack(side="right")

            ctk.CTkLabel(
                r_inner,
                text=item["text"],
                font=self.scaled_font(14, weight="bold"),
                text_color=c["text_primary"],
                anchor="w",
                justify="left"
            ).pack(fill="x", pady=(0, 10))

            user_ans_str = item["options"][item["userSelection"]] if item["userSelection"] is not None else "Not Answered"
            correct_ans_str = item["options"][item["correctSelection"]]

            ctk.CTkLabel(
                r_inner,
                text=f"Your Answer: {user_ans_str}",
                font=self.scaled_font(12),
                text_color="#10b981" if item["isCorrect"] else "#ef4444",
                anchor="w"
            ).pack(fill="x")

            ctk.CTkLabel(
                r_inner,
                text=f"Correct Answer: {correct_ans_str}",
                font=self.scaled_font(12, weight="bold"),
                text_color="#10b981",
                anchor="w"
            ).pack(fill="x", pady=(2, 8))

            if item.get("explanation"):
                exp_box = ctk.CTkFrame(r_inner, fg_color=c["badge_cyan_bg"], corner_radius=6)
                exp_box.pack(fill="x", pady=(4, 0))
                ctk.CTkLabel(
                    exp_box,
                    text=f"💡 Explanation: {item['explanation']}",
                    font=self.scaled_font(12),
                    text_color=c["badge_cyan_text"],
                    anchor="w",
                    justify="left",
                    padx=12,
                    pady=8
                ).pack(fill="x")

    # =========================================================================
    # VIEW 5: EXAMINER STUDIO (Dashboard, Creator, AI Synthesizer & Reports)
    # =========================================================================
    def render_examiner_studio(self):
        self.clear_workspace()
        c = self.get_theme_colors()

        scroll = ctk.CTkScrollableFrame(self.workspace, fg_color="transparent", corner_radius=0)
        scroll.pack(fill="both", expand=True, padx=40, pady=(20, 30))

        # Header Row
        header_row = ctk.CTkFrame(scroll, fg_color="transparent")
        header_row.pack(fill="x", pady=(10, 20))

        left_hero = ctk.CTkFrame(header_row, fg_color="transparent")
        left_hero.pack(side="left", fill="y", anchor="w")

        ctk.CTkLabel(
            left_hero,
            text="Examiner Studio & Assessment Builder",
            font=self.scaled_font(24, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w")

        ctk.CTkLabel(
            left_hero,
            text="Synthesize AI tests, manage join codes, and inspect live gradebook analytics.",
            font=self.scaled_font(13),
            text_color=c["text_secondary"]
        ).pack(anchor="w", pady=(2, 0))

        # Metrics Overview Row
        stats = self.db.get_global_stats()
        metrics_row = ctk.CTkFrame(scroll, fg_color="transparent")
        metrics_row.pack(fill="x", pady=(0, 25))

        metrics_data = [
            ("Total Assessments", f"{stats['totalQuizzes']} Quizzes", c["text_cyan"]),
            ("Total Submissions", f"{stats['totalAttempts']} Attempts", c["accent_primary"]),
            ("Average Pass Rate", f"{stats['passRate']}% Passed", "#10b981"),
            ("Active Students", f"{stats['activeStudents']} Candidates", "#f59e0b")
        ]

        for title, val, col in metrics_data:
            m_card = ctk.CTkFrame(metrics_row, fg_color=c["bg_card"], corner_radius=12, border_width=c["border_width"], border_color=c["card_border"])
            m_card.pack(side="left", fill="both", expand=True, padx=6)

            m_inner = ctk.CTkFrame(m_card, fg_color="transparent")
            m_inner.pack(fill="both", expand=True, padx=18, pady=16)

            ctk.CTkLabel(m_inner, text=title, font=self.scaled_font(11, weight="bold"), text_color=c["text_secondary"]).pack(anchor="w")
            ctk.CTkLabel(m_inner, text=val, font=self.scaled_font(20, weight="bold"), text_color=col).pack(anchor="w", pady=(4, 0))

        # Action Toolbar (New Assessment, AI Generator, CSV Export, DB Backup)
        tool_bar = ctk.CTkFrame(scroll, fg_color=c["bg_card"], corner_radius=10, border_width=c["border_width"], border_color=c["card_border"])
        tool_bar.pack(fill="x", pady=(0, 20))

        t_inner = ctk.CTkFrame(tool_bar, fg_color="transparent")
        t_inner.pack(fill="x", padx=16, pady=12)

        ctk.CTkButton(
            t_inner,
            text="+ Create Assessment",
            font=self.scaled_font(12, weight="bold"),
            fg_color="#4f46e5",
            hover_color="#4338ca",
            text_color="#ffffff",
            command=self.open_create_quiz_dialog
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            t_inner,
            text="🤖 AI Quiz Synthesizer",
            font=self.scaled_font(12, weight="bold"),
            fg_color=c["btn_cyan"],
            hover_color="#0369a1",
            text_color=c["btn_cyan_text"],
            command=self.open_ai_synthesizer_dialog
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            t_inner,
            text="📥 Export Gradebook CSV",
            font=self.scaled_font(12),
            fg_color=c["btn_neutral"],
            hover_color=c["btn_neutral_hover"],
            text_color=c["btn_neutral_text"],
            command=self.handle_export_csv
        ).pack(side="left", padx=(0, 10))

        ctk.CTkButton(
            t_inner,
            text="💾 Database Snapshot",
            font=self.scaled_font(12),
            fg_color=c["btn_neutral"],
            hover_color=c["btn_neutral_hover"],
            text_color=c["btn_neutral_text"],
            command=self.handle_db_backup
        ).pack(side="left")

        # Active Assessments & Student Join Codes Showcase
        ctk.CTkLabel(
            scroll,
            text="Active Tests & Student Join Codes:",
            font=self.scaled_font(16, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w", pady=(10, 8))

        all_quizzes = self.db.get_all_quizzes()
        quiz_grid = ctk.CTkFrame(scroll, fg_color="transparent")
        quiz_grid.pack(fill="x", pady=(0, 20))

        for q in all_quizzes:
            q_card = ctk.CTkFrame(quiz_grid, fg_color=c["bg_card"], corner_radius=10, border_width=c["border_width"], border_color=c["card_border"])
            q_card.pack(fill="x", pady=4)

            q_row = ctk.CTkFrame(q_card, fg_color="transparent")
            q_row.pack(fill="x", padx=16, pady=10)

            # Left: Title and metadata
            q_left = ctk.CTkFrame(q_row, fg_color="transparent")
            q_left.pack(side="left", fill="both", expand=True)

            ctk.CTkLabel(q_left, text=q["title"], font=self.scaled_font(13, weight="bold"), text_color=c["text_primary"]).pack(anchor="w")
            ctk.CTkLabel(
                q_left,
                text=f"📂 {q.get('category', 'General')}  •  ⏱️ {q.get('durationMinutes', 10)} Mins  •  📝 {len(q.get('questions', []))} Questions  •  🎯 Pass: {q.get('passingScore', 70)}%",
                font=self.scaled_font(11),
                text_color=c["text_secondary"]
            ).pack(anchor="w", pady=(2, 0))

            # Right: Code badge and copy button
            code_str = q.get("joinCode") or "QZ-1001"
            q_right = ctk.CTkFrame(q_row, fg_color="transparent")
            q_right.pack(side="right")

            code_badge = ctk.CTkFrame(q_right, fg_color=c["bg_card_secondary"], corner_radius=8, border_width=1, border_color=c["card_border"])
            code_badge.pack(side="left", padx=(0, 10))

            ctk.CTkLabel(
                code_badge,
                text=f"🔑 CODE: {code_str}",
                font=self.scaled_font(12, weight="bold"),
                text_color=c["accent_primary"],
                padx=10,
                pady=4
            ).pack()

            def make_copy_handler(cd=code_str, ttl=q["title"]):
                def _cp():
                    self.clipboard_clear()
                    self.clipboard_append(cd)
                    messagebox.showinfo("Join Code Copied", f"Join Code '{cd}' for '{ttl}' copied to clipboard!\n\nStudents can enter this code in the Candidate Arena to join.")
                return _cp

            ctk.CTkButton(
                q_right,
                text="📋 Copy Code",
                width=90,
                height=30,
                font=self.scaled_font(11, weight="bold"),
                fg_color=c["btn_neutral"],
                hover_color=c["btn_neutral_hover"],
                text_color=c["btn_neutral_text"],
                command=make_copy_handler(code_str, q["title"])
            ).pack(side="left")

        # Class Gradebook & Submissions Table
        ctk.CTkLabel(
            scroll,
            text="Student Submissions & Class Gradebook Roster:",
            font=self.scaled_font(16, weight="bold"),
            text_color=c["text_primary"]
        ).pack(anchor="w", pady=(15, 6))

        # Filter and Search Bar for Submissions
        filter_bar = ctk.CTkFrame(scroll, fg_color=c["bg_card"], corner_radius=10, border_width=c["border_width"], border_color=c["card_border"])
        filter_bar.pack(fill="x", pady=(0, 10))

        fb_inner = ctk.CTkFrame(filter_bar, fg_color="transparent")
        fb_inner.pack(fill="x", padx=16, pady=10)

        ctk.CTkLabel(fb_inner, text="Filter by Test:", font=self.scaled_font(11, weight="bold"), text_color=c["text_secondary"]).pack(side="left", padx=(0, 6))

        quiz_filter_opts = ["All Assessments"] + [f"{q.get('joinCode', 'QZ')}: {q['title']}" for q in all_quizzes]
        quiz_filter_menu = ctk.CTkOptionMenu(
            fb_inner,
            values=quiz_filter_opts,
            height=32,
            width=240,
            font=self.scaled_font(11),
            fg_color=c["bg_card_secondary"],
            text_color=c["text_primary"],
            button_color=c["card_border"]
        )
        quiz_filter_menu.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(fb_inner, text="Search Student:", font=self.scaled_font(11, weight="bold"), text_color=c["text_secondary"]).pack(side="left", padx=(0, 6))
        search_student_entry = ctk.CTkEntry(
            fb_inner,
            placeholder_text="Enter student name...",
            height=32,
            width=200,
            font=self.scaled_font(11),
            fg_color=c["bg_card_secondary"],
            text_color=c["text_primary"],
            border_color=c["card_border"]
        )
        search_student_entry.pack(side="left", padx=(0, 12))

        table_card = ctk.CTkFrame(scroll, fg_color=c["bg_card"], corner_radius=12, border_width=c["border_width"], border_color=c["card_border"])
        table_card.pack(fill="x", pady=(0, 20))

        all_reports = self.db.get_teacher_reports()

        def render_roster_rows():
            for widget in table_card.winfo_children():
                widget.destroy()

            selected_filter = quiz_filter_menu.get()
            search_query = search_student_entry.get().strip().lower()

            filtered = all_reports
            if selected_filter != "All Assessments":
                code_part = selected_filter.split(":")[0].strip().upper()
                filtered = [r for r in filtered if r.get("joinCode", "").upper() == code_part or code_part in r.get("quizTitle", "").upper()]

            if search_query:
                filtered = [r for r in filtered if search_query in r.get("studentName", "").lower()]

            if not filtered:
                ctk.CTkLabel(table_card, text="No candidate submissions matching current filters.", font=self.scaled_font(13), text_color=c["text_secondary"]).pack(pady=30)
                return

            # Table Header
            th_frame = ctk.CTkFrame(table_card, fg_color=c["table_header_bg"], corner_radius=0)
            th_frame.pack(fill="x")

            headers = [("Candidate", 160), ("Assessment", 200), ("Code", 90), ("Score", 80), ("Percent", 80), ("Status", 95), ("Violations", 85), ("Date", 140)]
            for h_title, h_width in headers:
                lbl = ctk.CTkLabel(th_frame, text=h_title, font=self.scaled_font(11, weight="bold"), text_color=c["text_secondary"], width=h_width, anchor="w")
                lbl.pack(side="left", padx=8, pady=8)

            for idx, r in enumerate(filtered[:25]):
                row_frame = ctk.CTkFrame(table_card, fg_color=c["bg_card"] if idx % 2 == 0 else c["table_row_alt"], corner_radius=0)
                row_frame.pack(fill="x")

                passed = r["passed"]
                vals = [
                    (r["studentName"], 160, c["text_primary"]),
                    (r["quizTitle"], 200, c["text_cyan"]),
                    (r.get("joinCode", "QZ-1001"), 90, c["accent_primary"]),
                    (f"{r['score']} / {r['totalQuestions']}", 80, c["text_primary"]),
                    (f"{r['percentage']}%", 80, "#10b981" if passed else "#ef4444"),
                    ("PASSED 🏆" if passed else "FAILED", 95, "#10b981" if passed else "#ef4444"),
                    (str(r["cheatViolations"]), 85, "#f59e0b" if r["cheatViolations"] > 0 else "#64748b"),
                    (r["submittedAt"][:16] if r["submittedAt"] else "", 140, c["text_secondary"])
                ]
                for v_text, v_width, v_color in vals:
                    ctk.CTkLabel(row_frame, text=v_text, font=self.scaled_font(11), text_color=v_color, width=v_width, anchor="w").pack(side="left", padx=8, pady=7)

        quiz_filter_menu.configure(command=lambda _: render_roster_rows())
        search_student_entry.bind("<KeyRelease>", lambda _: render_roster_rows())

        ctk.CTkButton(
            fb_inner,
            text="🔄 Refresh",
            width=80,
            height=32,
            font=self.scaled_font(11),
            fg_color=c["btn_neutral"],
            hover_color=c["btn_neutral_hover"],
            text_color=c["btn_neutral_text"],
            command=render_roster_rows
        ).pack(side="left")

        render_roster_rows()

    def handle_export_csv(self):
        filepath = export_class_reports_to_csv()
        messagebox.showinfo("Export Successful", f"Class Gradebook CSV generated successfully:\n\n{filepath}")

    def handle_db_backup(self):
        backup_path = run_automated_db_backup()
        messagebox.showinfo("Backup Successful", f"Authoritative SQLite snapshot generated:\n\n{backup_path}")

    # =========================================================================
    # DIALOGS: CREATE QUIZ & AI SYNTHESIZER
    # =========================================================================
    def open_create_quiz_dialog(self):
        c = self.get_theme_colors()
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create New Assessment")
        dialog.geometry("640x680")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=c["bg_primary"])

        scroll = ctk.CTkScrollableFrame(dialog, fg_color=c["bg_card"], corner_radius=12, border_width=c["border_width"], border_color=c["card_border"])
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(scroll, text="⚡ New Assessment Setup", font=self.scaled_font(18, weight="bold"), text_color=c["text_primary"]).pack(anchor="w", pady=(0, 15))

        # Title
        ctk.CTkLabel(scroll, text="Assessment Title:", font=self.scaled_font(12, weight="bold"), text_color=c["text_primary"]).pack(anchor="w", pady=(2, 2))
        title_in = ctk.CTkEntry(scroll, placeholder_text="e.g. Distributed Database Architecture", height=36, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
        title_in.pack(fill="x", pady=(0, 8))

        # Join Code row
        code_row = ctk.CTkFrame(scroll, fg_color="transparent")
        code_row.pack(fill="x", pady=(0, 8))

        ctk.CTkLabel(code_row, text="Student Join Code:", font=self.scaled_font(12, weight="bold"), text_color=c["text_primary"]).pack(side="left", padx=(0, 10))
        code_in = ctk.CTkEntry(code_row, width=140, height=36, fg_color=c["bg_card_secondary"], text_color=c["accent_primary"], border_color=c["card_border"], font=self.scaled_font(12, weight="bold"))
        code_in.insert(0, f"QZ-{random.randint(1000, 9999)}")
        code_in.pack(side="left", padx=(0, 10))

        def roll_code():
            code_in.delete(0, "end")
            code_in.insert(0, f"QZ-{random.randint(1000, 9999)}")

        ctk.CTkButton(code_row, text="🎲 Roll New", width=90, height=32, font=self.scaled_font(11), fg_color=c["btn_neutral"], hover_color=c["btn_neutral_hover"], text_color=c["btn_neutral_text"], command=roll_code).pack(side="left")

        # Category
        ctk.CTkLabel(scroll, text="Category:", font=self.scaled_font(12, weight="bold"), text_color=c["text_primary"]).pack(anchor="w", pady=(2, 2))
        cat_in = ctk.CTkEntry(scroll, placeholder_text="e.g. Cloud Engineering", height=36, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
        cat_in.insert(0, "Cloud Engineering")
        cat_in.pack(fill="x", pady=(0, 8))

        # Duration & Passing Score
        meta_row = ctk.CTkFrame(scroll, fg_color="transparent")
        meta_row.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(meta_row, text="Duration (Minutes):", font=self.scaled_font(12, weight="bold"), text_color=c["text_primary"]).pack(side="left", padx=(0, 6))
        dur_in = ctk.CTkEntry(meta_row, width=80, height=36, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
        dur_in.insert(0, "15")
        dur_in.pack(side="left", padx=(0, 20))

        ctk.CTkLabel(meta_row, text="Passing Score (%):", font=self.scaled_font(12, weight="bold"), text_color=c["text_primary"]).pack(side="left", padx=(0, 6))
        pass_in = ctk.CTkEntry(meta_row, width=80, height=36, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
        pass_in.insert(0, "70")
        pass_in.pack(side="left")

        # Question 1
        ctk.CTkLabel(scroll, text="Question 1 Prompt:", font=self.scaled_font(12, weight="bold"), text_color=c["text_cyan"]).pack(anchor="w", pady=(10, 2))
        q1_in = ctk.CTkEntry(scroll, placeholder_text="e.g. What guarantees read isolation in ACID transactions?", height=36, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
        q1_in.pack(fill="x", pady=(0, 8))

        # Options
        opt_inputs = []
        for i in range(4):
            ctk.CTkLabel(scroll, text=f"Option {chr(65 + i)}:", font=self.scaled_font(11), text_color=c["text_secondary"]).pack(anchor="w")
            oi = ctk.CTkEntry(scroll, height=32, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
            oi.pack(fill="x", pady=(0, 4))
            opt_inputs.append(oi)

        opt_inputs[0].insert(0, "Multi-Version Concurrency Control (MVCC)")
        opt_inputs[1].insert(0, "Disabling transaction rollback logs")
        opt_inputs[2].insert(0, "Using single-threaded file locks exclusively")
        opt_inputs[3].insert(0, "Bypassing write-ahead logging")

        def on_save():
            title = title_in.get().strip()
            if not title:
                messagebox.showerror("Error", "Title is required")
                return
            join_code = code_in.get().strip().upper() or f"QZ-{random.randint(1000, 9999)}"
            new_quiz = {
                "id": f"quiz-{int(time.time())}",
                "joinCode": join_code,
                "title": title,
                "category": cat_in.get().strip() or "General",
                "description": "Standardized academic assessment.",
                "durationMinutes": int(dur_in.get().strip() or 10),
                "passingScore": int(pass_in.get().strip() or 70),
                "teacherName": self.teacher_name,
                "tags": [cat_in.get().strip() or "General", "Core"],
                "questions": [
                    {
                        "id": f"q-{int(time.time())}",
                        "text": q1_in.get().strip() or "Sample Question",
                        "code": None,
                        "options": [oi.get().strip() or f"Option {i}" for i, oi in enumerate(opt_inputs)],
                        "correct": 0,
                        "explanation": "Verified correct option."
                    }
                ]
            }
            self.db.save_quiz(new_quiz)
            dialog.destroy()
            messagebox.showinfo("Quiz Created", f"Assessment '{title}' created with Join Code: {new_quiz['joinCode']}")
            self.render_examiner_studio()

        ctk.CTkButton(
            scroll,
            text="Save & Publish Assessment 🚀",
            font=self.scaled_font(13, weight="bold"),
            fg_color="#10b981",
            hover_color="#059669",
            text_color="#ffffff",
            height=40,
            command=on_save
        ).pack(fill="x", pady=(15, 10))

    def open_ai_synthesizer_dialog(self):
        c = self.get_theme_colors()
        dialog = ctk.CTkToplevel(self)
        dialog.title("AI Assessment Synthesizer")
        dialog.geometry("560x420")
        dialog.transient(self)
        dialog.grab_set()
        dialog.configure(fg_color=c["bg_primary"])

        content = ctk.CTkFrame(dialog, fg_color=c["bg_card"], corner_radius=12, border_width=c["border_width"], border_color=c["card_border"])
        content.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(content, text="🤖 AI Assessment Synthesizer", font=self.scaled_font(18, weight="bold"), text_color=c["text_primary"]).pack(anchor="w", padx=20, pady=(20, 4))
        ctk.CTkLabel(content, text="Generate multi-item quiz banks dynamically with verified keys.", font=self.scaled_font(12), text_color=c["text_secondary"]).pack(anchor="w", padx=20, pady=(0, 16))

        ctk.CTkLabel(content, text="Subject / Topic:", font=self.scaled_font(12, weight="bold"), text_color=c["text_primary"]).pack(anchor="w", padx=20, pady=(0, 2))
        topic_in = ctk.CTkEntry(content, placeholder_text="e.g. Distributed Consensus Algorithms", height=38, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], border_color=c["card_border"])
        topic_in.insert(0, "Distributed Systems (Raft & Paxos)")
        topic_in.pack(fill="x", padx=20, pady=(0, 12))

        diff_row = ctk.CTkFrame(content, fg_color="transparent")
        diff_row.pack(fill="x", padx=20, pady=(0, 20))

        ctk.CTkLabel(diff_row, text="Difficulty:", font=self.scaled_font(12, weight="bold"), text_color=c["text_primary"]).pack(side="left", padx=(0, 10))
        diff_menu = ctk.CTkOptionMenu(diff_row, values=["Beginner", "Medium", "Advanced"], height=36, fg_color=c["bg_card_secondary"], text_color=c["text_primary"], button_color=c["card_border"])
        diff_menu.pack(side="left")

        def on_generate():
            topic = topic_in.get().strip() or "General Technology"
            diff = diff_menu.get()
            dialog.destroy()
            self.generate_ai_quiz(topic, diff)

        ctk.CTkButton(
            content,
            text="Synthesize Quiz ⚡",
            font=self.scaled_font(13, weight="bold"),
            fg_color=c["btn_cyan"],
            hover_color="#0369a1",
            text_color=c["btn_cyan_text"],
            height=42,
            command=on_generate
        ).pack(fill="x", padx=20, pady=(10, 20))

    def generate_ai_quiz(self, topic, difficulty):
        raw_res = generate_quiz_with_ai(topic=topic, num_questions=3, difficulty=difficulty)
        questions = raw_res.get("questions", [])
        if not questions:
            messagebox.showerror("Error", "Failed to synthesize questions.")
            return

        new_quiz = {
            "id": f"quiz-ai-{int(time.time())}",
            "joinCode": f"QZ-{random.randint(1000, 9999)}",
            "title": f"{topic} ({difficulty})",
            "category": "AI Synthesized",
            "description": f"Automated assessment focusing on core principles of {topic}.",
            "durationMinutes": 10,
            "passingScore": 70,
            "teacherName": self.teacher_name,
            "tags": [topic.split()[0], difficulty, "AI"],
            "questions": questions
        }
        self.db.save_quiz(new_quiz)
        messagebox.showinfo("AI Generated", f"Assessment '{new_quiz['title']}' generated successfully with Code: {new_quiz['joinCode']}")
        self.render_examiner_studio()

    # =========================================================================
    # ANTI-CHEAT LISTENER (WINDOW BLUR DETECTION)
    # =========================================================================
    def on_window_focus_loss(self, event):
        if self.current_nav_view == "exam-arena" and self.active_quiz:
            now = time.time()
            if now - self.last_focus_loss_time > 2.0:
                self.cheat_violations += 1
                self.last_focus_loss_time = now


if __name__ == "__main__":
    app = OnlineQuizDesktopApp()
    app.mainloop()
