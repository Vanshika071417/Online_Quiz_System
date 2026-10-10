"""
Online Quiz System - Native Python Desktop Application
Featuring 3 Dedicated Dashboards:
1. 🛡️ Admin Dashboard (Global analytics, system health, all quizzes & attempt records)
2. 👩‍🏫 Teacher / Faculty Dashboard (Manual builder, 🤖 AI Quiz Generator, Quiz Code generator, Student Class Reports)
3. 🎓 Student Dashboard (Join via Quiz Code, timed proctored exam, personal scorecard & answers review)
"""

import sys
import json
import time
import sqlite3
import random
import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

from ai_quiz_generator import generate_quiz_with_ai

# CustomTkinter Setup
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DB_PATH = "quiz_system.db"


class DatabaseManager:
    """SQLite Database layer supporting Users, Quizzes, Quiz Join Codes, and Student Reports."""
    def __init__(self):
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Quizzes table with join_code and teacher_id
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id TEXT PRIMARY KEY,
                join_code TEXT UNIQUE NOT NULL,
                teacher_name TEXT NOT NULL DEFAULT 'Prof. Smith',
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

        # Student attempts table linked to quiz and teacher
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
        # Check and migrate columns in existing database
        cursor.execute("PRAGMA table_info(quizzes)")
        quiz_cols = [c[1] for c in cursor.fetchall()]
        if "join_code" not in quiz_cols:
            cursor.execute("ALTER TABLE quizzes ADD COLUMN join_code TEXT DEFAULT 'QZ-1001'")
        if "teacher_name" not in quiz_cols:
            cursor.execute("ALTER TABLE quizzes ADD COLUMN teacher_name TEXT DEFAULT 'Prof. Alan Turing'")

        # Ensure all existing quizzes have valid join_code
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

        # Seed initial quiz with join code if empty
        cursor.execute("SELECT COUNT(*) FROM quizzes")
        if cursor.fetchone()[0] == 0:
            seed_q = [
                {
                    "id": "q1",
                    "text": "What does HTTP status code 403 Forbidden indicate?",
                    "code": None,
                    "options": [
                        "The server understood the request but refuses to authorize it",
                        "The requested URL resource does not exist on the server",
                        "The server crashed while executing a database query",
                        "The request method is not supported"
                    ],
                    "correct": 0,
                    "explanation": "403 Forbidden indicates the server authenticated or parsed the request but refuses permission."
                },
                {
                    "id": "q2",
                    "text": "Which Python data structure maintains insertion order starting from Python 3.7+?",
                    "code": None,
                    "options": ["dict (Dictionary)", "set (Set)", "frozenset", "Default tree bucket"],
                    "correct": 0,
                    "explanation": "In Python 3.7+, standard dictionaries guarantee key insertion order preservation."
                }
            ]
            cursor.execute("""
                INSERT INTO quizzes (id, join_code, teacher_name, title, category, description, duration_minutes, passing_score, tags, questions_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "quiz-sample-1",
                "QZ-1001",
                "Prof. Alan Turing",
                "Computer Science Foundations",
                "Software Engineering",
                "Test core concepts of network protocols and language fundamentals.",
                10,
                70,
                json.dumps(["CS", "HTTP", "Python"]),
                json.dumps(seed_q)
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
            result.append({
                "id": r["id"],
                "joinCode": r["join_code"] if "join_code" in keys else "QZ-1001",
                "teacherName": r["teacher_name"] if "teacher_name" in keys else "Prof. Alan Turing",
                "title": r["title"],
                "category": r["category"],
                "description": r["description"],
                "durationMinutes": r["duration_minutes"],
                "passingScore": r["passing_score"],
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
        keys = r.keys()
        return {
            "id": r["id"],
            "joinCode": r["join_code"] if "join_code" in keys else "QZ-1001",
            "teacherName": r["teacher_name"] if "teacher_name" in keys else "Prof. Alan Turing",
            "title": r["title"],
            "category": r["category"],
            "description": r["description"],
            "durationMinutes": r["duration_minutes"],
            "passingScore": r["passing_score"],
            "questions": json.loads(r["questions_json"]),
            "createdAt": r["created_at"]
        }

    def save_quiz(self, quiz):
        conn = self.get_connection()
        cursor = conn.cursor()
        join_code = quiz.get("joinCode") or f"QZ-{random.randint(1000, 9999)}"
        cursor.execute("""
            INSERT INTO quizzes (id, join_code, teacher_name, title, category, description, duration_minutes, passing_score, tags, questions_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                category = excluded.category,
                description = excluded.description,
                duration_minutes = excluded.duration_minutes,
                passing_score = excluded.passing_score,
                questions_json = excluded.questions_json
        """, (
            quiz["id"],
            join_code,
            quiz.get("teacherName", "Prof. Alan"),
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
        return join_code

    def delete_quiz(self, quiz_id):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
        cursor.execute("DELETE FROM attempts WHERE quiz_id = ?", (quiz_id,))
        conn.commit()
        conn.close()

    def record_attempt(self, attempt):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attempts (id, quiz_id, join_code, quiz_title, teacher_name, student_name, score, total_questions, percentage, passed, cheat_violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            attempt["id"],
            attempt["quizId"],
            attempt["joinCode"],
            attempt["quizTitle"],
            attempt["teacherName"],
            attempt["studentName"],
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
            student_name = r["student_name"] if "student_name" in keys else (r["candidate_name"] if "candidate_name" in keys else "Student")
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
    def __init__(self):
        super().__init__()

        self.title("Online Quiz System — Pro Desktop (Admin, Teacher & Student)")
        self.geometry("1180x760")
        self.minsize(1020, 680)

        self.db = DatabaseManager()

        # Session State
        self.current_role = "student" # 'admin', 'teacher', 'student'
        self.teacher_name = "Prof. Alan Turing"
        self.student_name = "Candidate Student"
        
        # Exam State
        self.active_quiz = None
        self.current_q_index = 0
        self.user_answers = {}
        self.time_left_seconds = 0
        self.timer_running = False
        self.cheat_violations = 0

        # Anti-cheat tracking: Window focus out
        self.bind("<FocusOut>", self.on_window_focus_loss)

        # Configure Grid
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_views()

        # Default to Student Dashboard
        self.switch_role("student")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=250, corner_radius=0, fg_color="#0a0f1d")
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(7, weight=1)

        # Brand Banner
        logo_box = ctk.CTkFrame(self.sidebar_frame, fg_color="transparent")
        logo_box.grid(row=0, column=0, padx=20, pady=(25, 15), sticky="w")

        ctk.CTkLabel(
            logo_box,
            text="⚡ QuizSphere",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            logo_box,
            text="Enterprise Desktop 3-Role Suite",
            font=ctk.CTkFont(size=11),
            text_color="#06b6d4"
        ).pack(anchor="w")

        # Role Selector Dropdown
        ctk.CTkLabel(
            self.sidebar_frame,
            text="ACTIVE DASHBOARD ROLE:",
            font=ctk.CTkFont(size=10, weight="bold"),
            text_color="#94a3b8"
        ).grid(row=1, column=0, padx=20, pady=(10, 4), sticky="w")

        self.role_selector = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["🎓 Student", "👩‍🏫 Teacher / Faculty", "🛡️ Administrator"],
            command=self.on_role_menu_select,
            fg_color="#1e293b",
            button_color="#334155",
            font=ctk.CTkFont(size=12, weight="bold")
        )
        self.role_selector.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="ew")

        # Sidebar Dynamic Navigation Buttons
        self.nav_btn_1 = ctk.CTkButton(
            self.sidebar_frame,
            text="📝 My Quizzes",
            anchor="w",
            font=ctk.CTkFont(size=13),
            command=lambda: self.on_nav_click(1)
        )
        self.nav_btn_1.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.nav_btn_2 = ctk.CTkButton(
            self.sidebar_frame,
            text="🤖 AI Quiz Generator",
            anchor="w",
            fg_color="transparent",
            hover_color="#1e293b",
            font=ctk.CTkFont(size=13),
            command=lambda: self.on_nav_click(2)
        )
        self.nav_btn_2.grid(row=4, column=0, padx=15, pady=6, sticky="ew")

        self.nav_btn_3 = ctk.CTkButton(
            self.sidebar_frame,
            text="📊 Student Reports",
            anchor="w",
            fg_color="transparent",
            hover_color="#1e293b",
            font=ctk.CTkFont(size=13),
            command=lambda: self.on_nav_click(3)
        )
        self.nav_btn_3.grid(row=5, column=0, padx=15, pady=6, sticky="ew")

        # Bottom System Indicator
        status_box = ctk.CTkFrame(self.sidebar_frame, fg_color="#111827", corner_radius=8)
        status_box.grid(row=8, column=0, padx=15, pady=20, sticky="ew")

        ctk.CTkLabel(
            status_box,
            text="● SQLite Engine Active",
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#10b981"
        ).pack(padx=10, pady=(8, 2))

        ctk.CTkLabel(
            status_box,
            text="Desktop + Mobile Ready",
            font=ctk.CTkFont(size=10),
            text_color="gray"
        ).pack(padx=10, pady=(0, 8))

    def setup_views(self):
        # Container for main views
        self.container = ctk.CTkFrame(self, corner_radius=14, fg_color="#0f172a")
        self.container.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")
        self.container.grid_columnconfigure(0, weight=1)
        self.container.grid_rowconfigure(0, weight=1)

    def on_role_menu_select(self, choice):
        if "Student" in choice:
            self.switch_role("student")
        elif "Teacher" in choice:
            self.switch_role("teacher")
        elif "Admin" in choice:
            self.switch_role("admin")

    def switch_role(self, role):
        self.current_role = role
        
        # Reset nav buttons depending on role
        if role == "student":
            self.role_selector.set("🎓 Student")
            self.nav_btn_1.configure(text="🎯 Join & Take Quiz", fg_color=["#3B8ED0", "#1F6AA5"])
            self.nav_btn_2.configure(text="📜 My Attempt History", fg_color="transparent")
            self.nav_btn_3.grid_remove()
            self.render_student_lobby()

        elif role == "teacher":
            self.role_selector.set("👩‍🏫 Teacher / Faculty")
            self.nav_btn_1.configure(text="📚 Question Banks", fg_color=["#3B8ED0", "#1F6AA5"])
            self.nav_btn_2.configure(text="🤖 AI Quiz Generator", fg_color="transparent")
            self.nav_btn_3.grid()
            self.nav_btn_3.configure(text="📊 Class Reports", fg_color="transparent")
            self.render_teacher_quizzes()

        elif role == "admin":
            self.role_selector.set("🛡️ Administrator")
            self.nav_btn_1.configure(text="📈 System Overview", fg_color=["#3B8ED0", "#1F6AA5"])
            self.nav_btn_2.configure(text="📂 All Quizzes Management", fg_color="transparent")
            self.nav_btn_3.grid()
            self.nav_btn_3.configure(text="📋 Global Attempt Records", fg_color="transparent")
            self.render_admin_overview()

    def on_nav_click(self, btn_index):
        for btn in [self.nav_btn_1, self.nav_btn_2, self.nav_btn_3]:
            btn.configure(fg_color="transparent")

        if btn_index == 1:
            self.nav_btn_1.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            if self.current_role == "student":
                self.render_student_lobby()
            elif self.current_role == "teacher":
                self.render_teacher_quizzes()
            elif self.current_role == "admin":
                self.render_admin_overview()

        elif btn_index == 2:
            self.nav_btn_2.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            if self.current_role == "student":
                self.render_student_history()
            elif self.current_role == "teacher":
                self.render_teacher_ai_generator()
            elif self.current_role == "admin":
                self.render_admin_quizzes()

        elif btn_index == 3:
            self.nav_btn_3.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            if self.current_role == "teacher":
                self.render_teacher_reports()
            elif self.current_role == "admin":
                self.render_admin_attempts()

    def clear_container(self):
        for widget in self.container.winfo_children():
            widget.destroy()

    # =============================================================
    # 1. STUDENT DASHBOARD & ASSESSMENT ARENA
    # =============================================================
    def render_student_lobby(self):
        self.clear_container()

        header_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        header_frame.pack(fill="x", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            header_frame,
            text="Student Examination Dashboard",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w")

        ctk.CTkLabel(
            header_frame,
            text="Join an exam using your teacher's Quiz Code or browse available tests.",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        ).pack(anchor="w")

        # Join with Quiz Code Box
        code_box = ctk.CTkFrame(self.container, fg_color="#1e293b", corner_radius=12)
        code_box.pack(fill="x", padx=30, pady=15)

        ctk.CTkLabel(
            code_box,
            text="🔑 Enter Quiz Code to Join:",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#38bdf8"
        ).pack(side="left", padx=20, pady=15)

        self.quiz_code_entry = ctk.CTkEntry(
            code_box,
            placeholder_text="e.g. QZ-1001",
            width=180,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        self.quiz_code_entry.pack(side="left", padx=10, pady=15)

        ctk.CTkLabel(code_box, text="Your Name:", font=ctk.CTkFont(size=13)).pack(side="left", padx=(15, 5))
        self.student_name_entry = ctk.CTkEntry(code_box, width=180)
        self.student_name_entry.insert(0, self.student_name)
        self.student_name_entry.pack(side="left", padx=5)

        join_btn = ctk.CTkButton(
            code_box,
            text="Join Assessment ⚡",
            fg_color="#06b6d4",
            hover_color="#0891b2",
            text_color="#030712",
            font=ctk.CTkFont(weight="bold"),
            command=self.join_quiz_via_code
        )
        join_btn.pack(side="left", padx=15, pady=15)

        # Available Quizzes List
        ctk.CTkLabel(
            self.container,
            text="Available Faculty Quizzes:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#f8fafc"
        ).pack(anchor="w", padx=30, pady=(15, 8))

        scroll = ctk.CTkScrollableFrame(self.container, corner_radius=10, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        quizzes = self.db.get_all_quizzes()
        if not quizzes:
            ctk.CTkLabel(scroll, text="No active quizzes found. Ask your teacher to publish one.").pack(pady=40)
            return

        for q in quizzes:
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=8, padx=10)

            title_row = ctk.CTkFrame(card, fg_color="transparent")
            title_row.pack(fill="x", padx=15, pady=(12, 2))

            ctk.CTkLabel(
                title_row,
                text=q["title"],
                font=ctk.CTkFont(size=16, weight="bold")
            ).pack(side="left")

            ctk.CTkLabel(
                title_row,
                text=f"Code: {q['joinCode']}",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#06b6d4",
                fg_color="#082f49",
                corner_radius=6,
                padx=8,
                pady=2
            ).pack(side="right")

            ctk.CTkLabel(
                card,
                text=f"Instructor: {q['teacherName']}   |   Category: {q['category']}",
                font=ctk.CTkFont(size=12),
                text_color="#94a3b8"
            ).pack(anchor="w", padx=15, pady=(0, 6))

            meta_text = f"⏱️ Duration: {q['durationMinutes']} mins   |   ❓ Questions: {len(q['questions'])}   |   🎯 Passing: {q['passingScore']}%"
            ctk.CTkLabel(card, text=meta_text, font=ctk.CTkFont(size=12), text_color="#38bdf8").pack(anchor="w", padx=15, pady=(0, 10))

            start_btn = ctk.CTkButton(
                card,
                text="Start Test 🚀",
                fg_color="#6366f1",
                hover_color="#4f46e5",
                font=ctk.CTkFont(weight="bold"),
                command=lambda quiz=q: self.start_student_exam(quiz)
            )
            start_btn.pack(anchor="e", padx=15, pady=(0, 12))

    def join_quiz_via_code(self):
        code = self.quiz_code_entry.get().strip()
        if not code:
            messagebox.showwarning("Enter Code", "Please enter a valid Quiz Code (e.g. QZ-1001).")
            return

        quiz = self.db.get_quiz_by_code(code)
        if not quiz:
            messagebox.showerror("Not Found", f"No quiz found with code '{code}'. Please check with your teacher.")
            return

        self.student_name = self.student_name_entry.get().strip() or "Candidate Student"
        self.start_student_exam(quiz)

    def on_window_focus_loss(self, event):
        """Proctoring violation listener when student switches windows or tabs."""
        if self.timer_running and self.active_quiz:
            self.cheat_violations += 1
            if hasattr(self, "cheat_badge") and self.cheat_badge.winfo_exists():
                self.cheat_badge.configure(text=f"⚠️ Anti-Cheat Violations: {self.cheat_violations}")
            messagebox.showwarning(
                "Proctoring Violation",
                f"Window focus lost! Focus-out events are recorded and reported to your teacher.\nViolations: {self.cheat_violations}"
            )

    def start_student_exam(self, quiz):
        self.active_quiz = quiz
        self.current_q_index = 0
        self.user_answers = {}
        self.cheat_violations = 0
        self.time_left_seconds = quiz["durationMinutes"] * 60
        self.timer_running = True

        self.render_exam_arena()
        self.tick_exam_timer()

    def tick_exam_timer(self):
        if not self.timer_running:
            return

        mins = self.time_left_seconds // 60
        secs = self.time_left_seconds % 60
        time_text = f"⏱️ {mins:02d}:{secs:02d}"

        if hasattr(self, "timer_display") and self.timer_display.winfo_exists():
            self.timer_display.configure(text=time_text)
            if self.time_left_seconds <= 60:
                self.timer_display.configure(text_color="#ef4444")
            else:
                self.timer_display.configure(text_color="#06b6d4")

        if self.time_left_seconds <= 0:
            self.timer_running = False
            messagebox.showinfo("Time Up", "Your exam time has expired! Finalizing answers.")
            self.finalize_student_submission()
        else:
            self.time_left_seconds -= 1
            self.after(1000, self.tick_exam_timer)

    def render_exam_arena(self):
        self.clear_container()

        # Exam Header Bar
        top_bar = ctk.CTkFrame(self.container, fg_color="#1e293b", corner_radius=10)
        top_bar.pack(fill="x", padx=25, pady=(20, 10))

        ctk.CTkLabel(
            top_bar,
            text=f"Exam: {self.active_quiz['title']}",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left", padx=15, pady=12)

        self.cheat_badge = ctk.CTkLabel(
            top_bar,
            text=f"⚠️ Anti-Cheat Violations: {self.cheat_violations}",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#fca5a5"
        )
        self.cheat_badge.pack(side="left", padx=20, pady=12)

        self.timer_display = ctk.CTkLabel(
            top_bar,
            text="⏱️ 00:00",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#06b6d4"
        )
        self.timer_display.pack(side="right", padx=15, pady=12)

        # Question Content Card
        q = self.active_quiz["questions"][self.current_q_index]

        q_card = ctk.CTkFrame(self.container, fg_color="#182234", corner_radius=12)
        q_card.pack(fill="both", expand=True, padx=25, pady=10)

        ctk.CTkLabel(
            q_card,
            text=f"Question {self.current_q_index + 1} of {len(self.active_quiz['questions'])}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#818cf8"
        ).pack(anchor="w", padx=25, pady=(20, 5))

        ctk.CTkLabel(
            q_card,
            text=q["text"],
            font=ctk.CTkFont(size=17, weight="bold"),
            wraplength=800,
            justify="left",
            text_color="#ffffff"
        ).pack(anchor="w", padx=25, pady=(5, 15))

        if q.get("code"):
            code_box = ctk.CTkTextbox(q_card, height=85, font=ctk.CTkFont(family="Consolas", size=12), text_color="#38bdf8", fg_color="#050811")
            code_box.insert("1.0", q["code"])
            code_box.configure(state="disabled")
            code_box.pack(fill="x", padx=25, pady=(0, 15))

        # Options Radio Group
        self.selected_radio_var = tk.IntVar(value=self.user_answers.get(q["id"], -1))
        options_panel = ctk.CTkFrame(q_card, fg_color="transparent")
        options_panel.pack(fill="x", padx=25, pady=5)

        for opt_idx, opt_text in enumerate(q["options"]):
            radio = ctk.CTkRadioButton(
                options_panel,
                text=opt_text,
                variable=self.selected_radio_var,
                value=opt_idx,
                font=ctk.CTkFont(size=14),
                command=lambda idx=opt_idx: self.user_answers.update({q["id"]: idx})
            )
            radio.pack(anchor="w", pady=7)

        # Bottom Controls Bar
        action_bar = ctk.CTkFrame(self.container, fg_color="transparent")
        action_bar.pack(fill="x", padx=25, pady=(10, 20))

        prev_btn = ctk.CTkButton(
            action_bar,
            text="← Previous",
            state="normal" if self.current_q_index > 0 else "disabled",
            command=self.student_prev_q
        )
        prev_btn.pack(side="left")

        finish_early_btn = ctk.CTkButton(
            action_bar,
            text="Submit Assessment Early",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.student_confirm_submit
        )
        finish_early_btn.pack(side="left", padx=15)

        is_last = self.current_q_index == len(self.active_quiz["questions"]) - 1
        next_btn = ctk.CTkButton(
            action_bar,
            text="Finalize & Submit ✔️" if is_last else "Next Question →",
            fg_color="#10b981" if is_last else ["#3B8ED0", "#1F6AA5"],
            command=self.student_confirm_submit if is_last else self.student_next_q
        )
        next_btn.pack(side="right")

    def student_prev_q(self):
        if self.current_q_index > 0:
            self.current_q_index -= 1
            self.render_exam_arena()

    def student_next_q(self):
        if self.current_q_index < len(self.active_quiz["questions"]) - 1:
            self.current_q_index += 1
            self.render_exam_arena()

    def student_confirm_submit(self):
        answered = len(self.user_answers)
        total = len(self.active_quiz["questions"])
        msg = f"Candidate: {self.student_name}\nAnswered: {answered} / {total}\nProctor Violations: {self.cheat_violations}\n\nConfirm final submission to {self.active_quiz['teacherName']}?"
        if messagebox.askyesno("Submit Exam", msg):
            self.finalize_student_submission()

    def finalize_student_submission(self):
        self.timer_running = False
        correct_count = 0
        questions = self.active_quiz["questions"]
        for q in questions:
            if self.user_answers.get(q["id"]) == q["correct"]:
                correct_count += 1

        total = len(questions)
        pct = round((correct_count / total) * 100) if total > 0 else 0
        passed = pct >= self.active_quiz["passingScore"]

        attempt = {
            "id": f"att-{int(time.time()*1000)}",
            "quizId": self.active_quiz["id"],
            "joinCode": self.active_quiz["joinCode"],
            "quizTitle": self.active_quiz["title"],
            "teacherName": self.active_quiz["teacherName"],
            "studentName": self.student_name,
            "score": correct_count,
            "totalQuestions": total,
            "percentage": pct,
            "passed": passed,
            "cheatViolations": self.cheat_violations
        }

        # Save to database
        self.db.record_attempt(attempt)
        self.render_student_report_card(attempt)

    def render_student_report_card(self, attempt):
        self.clear_container()

        card = ctk.CTkFrame(self.container, fg_color="#111827", corner_radius=14)
        card.pack(fill="both", expand=True, padx=40, pady=30)

        status_text = "PASSED 🎉" if attempt["passed"] else "NEEDS IMPROVEMENT ⚠️"
        status_color = "#10b981" if attempt["passed"] else "#ef4444"

        ctk.CTkLabel(card, text=status_text, font=ctk.CTkFont(size=24, weight="bold"), text_color=status_color).pack(pady=(25, 5))
        ctk.CTkLabel(card, text=attempt["quizTitle"], font=ctk.CTkFont(size=20, weight="bold")).pack(pady=4)
        ctk.CTkLabel(card, text=f"Instructor: {attempt['teacherName']} (Report Synced)", text_color="#38bdf8").pack(pady=2)

        score_text = f"{attempt['score']} / {attempt['totalQuestions']}  ({attempt['percentage']}%)"
        ctk.CTkLabel(card, text=score_text, font=ctk.CTkFont(size=32, weight="bold"), text_color="#ffffff").pack(pady=15)

        info_frame = ctk.CTkFrame(card, fg_color="#1f2937", corner_radius=8)
        info_frame.pack(padx=30, pady=10, fill="x")

        ctk.CTkLabel(info_frame, text=f"Candidate: {attempt['studentName']}   |   Violations Recorded: {attempt['cheatViolations']}").pack(pady=10)

        # Questions Review Scroll
        review_scroll = ctk.CTkScrollableFrame(card, height=220, corner_radius=8, fg_color="#0f172a")
        review_scroll.pack(fill="both", expand=True, padx=30, pady=10)

        for idx, q in enumerate(self.active_quiz["questions"]):
            user_choice = self.user_answers.get(q["id"])
            is_correct = user_choice == q["correct"]

            q_row = ctk.CTkFrame(review_scroll, fg_color="#1e293b", corner_radius=6)
            q_row.pack(fill="x", pady=4, padx=5)

            status_icon = "✅ Correct" if is_correct else ("⚠️ Skipped" if user_choice is None else "❌ Incorrect")
            color = "#10b981" if is_correct else "#ef4444"

            ctk.CTkLabel(q_row, text=f"Q{idx+1}: {q['text'][:55]}...   [{status_icon}]", text_color=color, font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=10, pady=(6, 2))
            ctk.CTkLabel(q_row, text=f"Correct Answer: {q['options'][q['correct']]}", text_color="gray", font=ctk.CTkFont(size=11)).pack(anchor="w", padx=10, pady=(0, 6))

        back_btn = ctk.CTkButton(
            card,
            text="Return to Student Dashboard",
            command=self.render_student_lobby
        )
        back_btn.pack(pady=(10, 20))

    def render_student_history(self):
        self.clear_container()

        ctk.CTkLabel(
            self.container,
            text="My Examination Attempts & Gradebook",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=30, pady=(25, 5))

        scroll = ctk.CTkScrollableFrame(self.container, corner_radius=10, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=30, pady=(15, 25))

        reports = self.db.get_teacher_reports()
        if not reports:
            ctk.CTkLabel(scroll, text="No tests completed yet.").pack(pady=40)
            return

        for r in reports:
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=6, padx=10)

            status_color = "#10b981" if r["passed"] else "#ef4444"
            ctk.CTkLabel(card, text=f"{r['quizTitle']} — {r['score']}/{r['totalQuestions']} ({r['percentage']}%)", font=ctk.CTkFont(size=15, weight="bold"), text_color=status_color).pack(anchor="w", padx=15, pady=(10, 2))
            meta = f"Teacher: {r['teacherName']}   |   Code: {r['joinCode']}   |   Violations: {r['cheatViolations']}   |   Date: {r['submittedAt']}"
            ctk.CTkLabel(card, text=meta, font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(anchor="w", padx=15, pady=(0, 10))

    # =============================================================
    # 2. TEACHER / FACULTY DASHBOARD (Manual + AI Generator + Reports)
    # =============================================================
    def render_teacher_quizzes(self):
        self.clear_container()

        header = ctk.CTkFrame(self.container, fg_color="transparent")
        header.pack(fill="x", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            header,
            text="Teacher & Faculty Question Banks",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(side="left")

        actions = ctk.CTkFrame(header, fg_color="transparent")
        actions.pack(side="right")

        ai_btn = ctk.CTkButton(
            actions,
            text="🤖 Generate with AI",
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            command=self.render_teacher_ai_generator
        )
        ai_btn.pack(side="left", padx=5)

        manual_btn = ctk.CTkButton(
            actions,
            text="+ Manual Create",
            fg_color="#06b6d4",
            hover_color="#0891b2",
            text_color="#030712",
            font=ctk.CTkFont(weight="bold"),
            command=self.open_teacher_manual_quiz_dialog
        )
        manual_btn.pack(side="left", padx=5)

        # Quizzes Catalog
        scroll = ctk.CTkScrollableFrame(self.container, corner_radius=10, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=30, pady=(15, 25))

        quizzes = self.db.get_all_quizzes()
        if not quizzes:
            ctk.CTkLabel(scroll, text="No quizzes created yet. Use '+ Manual Create' or '🤖 Generate with AI'.").pack(pady=40)
            return

        for q in quizzes:
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=8, padx=10)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 2))

            ctk.CTkLabel(top, text=q["title"], font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            
            # Prominent Join Code Badge for Students
            code_badge = ctk.CTkLabel(
                top,
                text=f"Student Code: {q['joinCode']}",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#38bdf8",
                fg_color="#082f49",
                corner_radius=6,
                padx=10,
                pady=4
            )
            code_badge.pack(side="right")

            meta = f"Category: {q['category']}   |   Questions: {len(q['questions'])}   |   Duration: {q['durationMinutes']}m   |   Pass: {q['passingScore']}%"
            ctk.CTkLabel(card, text=meta, text_color="#94a3b8", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(0, 10))

            btn_row = ctk.CTkFrame(card, fg_color="transparent")
            btn_row.pack(anchor="e", padx=15, pady=(0, 10))

            del_btn = ctk.CTkButton(
                btn_row,
                text="Delete",
                width=75,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda qid=q["id"]: self.delete_teacher_quiz(qid)
            )
            del_btn.pack(side="right", padx=5)

    def delete_teacher_quiz(self, quiz_id):
        if messagebox.askyesno("Delete Quiz", "Delete this quiz and all student reports?"):
            self.db.delete_quiz(quiz_id)
            self.render_teacher_quizzes()

    # AI Quiz Generator View
    def render_teacher_ai_generator(self):
        self.clear_container()

        ctk.CTkLabel(
            self.container,
            text="🤖 AI-Powered Quiz Generator",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=30, pady=(25, 5))

        ctk.CTkLabel(
            self.container,
            text="Provide your subject or syllabus topic, and the AI engine will construct structured questions, distractors, and explanations.",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        form_box = ctk.CTkFrame(self.container, fg_color="#182234", corner_radius=12)
        form_box.pack(fill="x", padx=30, pady=10)

        # Subject / Topic
        ctk.CTkLabel(form_box, text="Subject / Topic:", font=ctk.CTkFont(weight="bold")).pack(anchor="w", padx=20, pady=(15, 2))
        self.ai_topic_entry = ctk.CTkEntry(form_box, placeholder_text="e.g. Python Object-Oriented Programming, Operating Systems, Database Normalization")
        self.ai_topic_entry.insert(0, "Python Data Structures & Memory Management")
        self.ai_topic_entry.pack(fill="x", padx=20, pady=(0, 12))

        # Row with count & difficulty
        row = ctk.CTkFrame(form_box, fg_color="transparent")
        row.pack(fill="x", padx=20, pady=(0, 15))

        ctk.CTkLabel(row, text="Questions Count:").pack(side="left", padx=(0, 5))
        self.ai_count_selector = ctk.CTkOptionMenu(row, values=["3", "5", "8", "10"], width=90)
        self.ai_count_selector.set("5")
        self.ai_count_selector.pack(side="left", padx=(0, 25))

        ctk.CTkLabel(row, text="Difficulty:").pack(side="left", padx=(0, 5))
        self.ai_diff_selector = ctk.CTkOptionMenu(row, values=["Beginner", "Medium", "Advanced"], width=110)
        self.ai_diff_selector.set("Medium")
        self.ai_diff_selector.pack(side="left", padx=(0, 25))

        ctk.CTkLabel(row, text="Duration (Mins):").pack(side="left", padx=(0, 5))
        self.ai_dur_entry = ctk.CTkEntry(row, width=70)
        self.ai_dur_entry.insert(0, "10")
        self.ai_dur_entry.pack(side="left")

        gen_btn = ctk.CTkButton(
            form_box,
            text="⚡ Generate & Publish Quiz with AI",
            fg_color="#8b5cf6",
            hover_color="#7c3aed",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.run_ai_quiz_generation
        )
        gen_btn.pack(padx=20, pady=(5, 20), fill="x")

    def run_ai_quiz_generation(self):
        topic = self.ai_topic_entry.get().strip() or "General Science"
        count = int(self.ai_count_selector.get())
        diff = self.ai_diff_selector.get()
        dur = int(self.ai_dur_entry.get().strip() or 10)

        # Generate questions
        questions = generate_quiz_with_ai(topic=topic, num_questions=count, difficulty=diff)

        new_quiz = {
            "id": f"quiz-ai-{int(time.time()*1000)}",
            "title": f"{topic} ({diff})",
            "category": "Academic / AI Generated",
            "description": f"Curriculum quiz generated for {topic} with {count} questions at {diff} level.",
            "durationMinutes": dur,
            "passingScore": 70,
            "teacherName": self.teacher_name,
            "tags": [topic.split()[0], diff, "AI-Generated"],
            "questions": questions
        }

        join_code = self.db.save_quiz(new_quiz)
        messagebox.showinfo(
            "Quiz Generated! 🎉",
            f"Successfully created '{new_quiz['title']}' with {len(questions)} questions!\n\n🔑 Student Join Code: {join_code}\n\nShare this code with your students to take the exam!"
        )
        self.render_teacher_quizzes()

    # Teacher Manual Quiz Dialog
    def open_teacher_manual_quiz_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Manual Assessment Builder")
        dialog.geometry("620x680")

        ctk.CTkLabel(dialog, text="Create New Quiz", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        title_e = ctk.CTkEntry(dialog, placeholder_text="Quiz Title (e.g. Database Transactions)", width=480)
        title_e.pack(pady=6)

        cat_e = ctk.CTkEntry(dialog, placeholder_text="Category (e.g. Computer Science)", width=480)
        cat_e.pack(pady=6)

        dur_e = ctk.CTkEntry(dialog, placeholder_text="Duration in Minutes (e.g. 15)", width=480)
        dur_e.insert(0, "15")
        dur_e.pack(pady=6)

        ctk.CTkLabel(dialog, text="Question 1 Prompt:", font=ctk.CTkFont(weight="bold")).pack(pady=(12, 4))
        prompt_e = ctk.CTkTextbox(dialog, height=55, width=480)
        prompt_e.insert("1.0", "Which SQL command is used to remove a table and its structure from a database?")
        prompt_e.pack(pady=4)

        opt1 = ctk.CTkEntry(dialog, placeholder_text="Option 1 (Correct)", width=480)
        opt1.insert(0, "DROP TABLE")
        opt1.pack(pady=4)

        opt2 = ctk.CTkEntry(dialog, placeholder_text="Option 2", width=480)
        opt2.insert(0, "DELETE FROM")
        opt2.pack(pady=4)

        opt3 = ctk.CTkEntry(dialog, placeholder_text="Option 3", width=480)
        opt3.insert(0, "TRUNCATE")
        opt3.pack(pady=4)

        opt4 = ctk.CTkEntry(dialog, placeholder_text="Option 4", width=480)
        opt4.insert(0, "REMOVE")
        opt4.pack(pady=4)

        def save_manual():
            title = title_e.get().strip() or "Custom Quiz"
            q_data = {
                "id": f"quiz-{int(time.time()*1000)}",
                "title": title,
                "category": cat_e.get().strip() or "General",
                "durationMinutes": int(dur_e.get().strip() or 10),
                "passingScore": 70,
                "teacherName": self.teacher_name,
                "questions": [
                    {
                        "id": "q1",
                        "text": prompt_e.get("1.0", "end-1c"),
                        "options": [opt1.get(), opt2.get(), opt3.get(), opt4.get()],
                        "correct": 0,
                        "explanation": "DROP TABLE deletes the table definition and all rows completely."
                    }
                ]
            }
            code = self.db.save_quiz(q_data)
            dialog.destroy()
            messagebox.showinfo("Published!", f"Quiz saved successfully!\nStudent Join Code: {code}")
            self.render_teacher_quizzes()

        ctk.CTkButton(dialog, text="Publish Quiz", fg_color="#10b981", command=save_manual).pack(pady=20)

    # Teacher Class Reports
    def render_teacher_reports(self):
        self.clear_container()

        ctk.CTkLabel(
            self.container,
            text="Class Examination Reports & Submissions",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=30, pady=(25, 5))

        ctk.CTkLabel(
            self.container,
            text="Real-time gradebook showing every student who submitted quizzes created by faculty.",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=30, pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(self.container, corner_radius=10, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        reports = self.db.get_teacher_reports()
        if not reports:
            ctk.CTkLabel(scroll, text="No student submissions recorded yet. Share your Quiz Code with students!").pack(pady=40)
            return

        for r in reports:
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=6, padx=10)

            top = ctk.CTkFrame(card, fg_color="transparent")
            top.pack(fill="x", padx=15, pady=(10, 2))

            status_color = "#10b981" if r["passed"] else "#ef4444"
            status_text = "PASSED" if r["passed"] else "FAILED"

            ctk.CTkLabel(top, text=f"Student: {r['studentName']}", font=ctk.CTkFont(size=16, weight="bold")).pack(side="left")
            ctk.CTkLabel(top, text=f"{status_text} ({r['percentage']}%)", font=ctk.CTkFont(size=13, weight="bold"), text_color=status_color).pack(side="right")

            meta = f"Quiz: {r['quizTitle']}   |   Code: {r['joinCode']}   |   Score: {r['score']}/{r['totalQuestions']}   |   ⚠️ Violations: {r['cheatViolations']}   |   Date: {r['submittedAt']}"
            ctk.CTkLabel(card, text=meta, text_color="#94a3b8", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(0, 10))

    # =============================================================
    # 3. ADMINISTRATOR DASHBOARD (Global Metrics & Auditing)
    # =============================================================
    def render_admin_overview(self):
        self.clear_container()

        ctk.CTkLabel(
            self.container,
            text="🛡️ Administrator Global Command Center",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=30, pady=(25, 5))

        ctk.CTkLabel(
            self.container,
            text="High-level platform metrics, active faculty members, and global candidate engagement.",
            font=ctk.CTkFont(size=13),
            text_color="#94a3b8"
        ).pack(anchor="w", padx=30, pady=(0, 20))

        stats = self.db.get_global_stats()

        # Stats Cards Grid
        grid_frame = ctk.CTkFrame(self.container, fg_color="transparent")
        grid_frame.pack(fill="x", padx=30, pady=(0, 20))
        grid_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        def make_stat_card(col, label, val, color):
            card = ctk.CTkFrame(grid_frame, fg_color="#182234", corner_radius=10)
            card.grid(row=0, column=col, padx=8, pady=5, sticky="ew")
            ctk.CTkLabel(card, text=val, font=ctk.CTkFont(size=26, weight="bold"), text_color=color).pack(pady=(15, 2))
            ctk.CTkLabel(card, text=label, font=ctk.CTkFont(size=12), text_color="#94a3b8").pack(pady=(0, 15))

        make_stat_card(0, "Total Quizzes", str(stats["totalQuizzes"]), "#06b6d4")
        make_stat_card(1, "Total Submissions", str(stats["totalAttempts"]), "#8b5cf6")
        make_stat_card(2, "Pass Rate", f"{stats['passRate']}%", "#10b981")
        make_stat_card(3, "Active Teachers", str(stats["activeTeachers"]), "#f59e0b")

        # Global Activity Feed
        ctk.CTkLabel(
            self.container,
            text="Recent Global Activity Audit:",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#ffffff"
        ).pack(anchor="w", padx=30, pady=(15, 8))

        scroll = ctk.CTkScrollableFrame(self.container, corner_radius=10, fg_color="#111827")
        scroll.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        reports = self.db.get_teacher_reports()
        if not reports:
            ctk.CTkLabel(scroll, text="No submissions recorded platform-wide yet.").pack(pady=30)
            return

        for r in reports:
            card = ctk.CTkFrame(scroll, corner_radius=8, fg_color="#1e293b")
            card.pack(fill="x", pady=4, padx=5)
            ctk.CTkLabel(card, text=f"[SUBMISSION] {r['studentName']} completed '{r['quizTitle']}' under {r['teacherName']} — Score: {r['percentage']}%", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=12, pady=8)

    def render_admin_quizzes(self):
        self.render_teacher_quizzes()

    def render_admin_attempts(self):
        self.render_teacher_reports()


if __name__ == "__main__":
    app = OnlineQuizDesktopApp()
    app.mainloop()
