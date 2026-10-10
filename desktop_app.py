"""
Online Quiz System - Native Python Desktop Application
Built with CustomTkinter for high-performance Windows & Desktop native experience.
Features:
- Student Candidate Arena (Take tests, interactive options, live countdown, anti-cheat detection)
- Examiner Studio (Create quizzes, add questions, set options & correct answer, manage bank)
- Analytics & Exam History (Detailed scores, accuracy, proctor violations)
"""

import sys
import json
import time
import sqlite3
import datetime
import tkinter as tk
from tkinter import messagebox
import customtkinter as ctk

# Configure CustomTkinter Appearance
ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

DB_PATH = "quiz_system.db"


class DatabaseManager:
    """Manages SQLite persistence for the Desktop application."""
    def __init__(self):
        self.init_db()

    def get_connection(self):
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS quizzes (
                id TEXT PRIMARY KEY,
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
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS attempts (
                id TEXT PRIMARY KEY,
                quiz_id TEXT NOT NULL,
                quiz_title TEXT NOT NULL,
                candidate_name TEXT NOT NULL,
                score INTEGER NOT NULL,
                total_questions INTEGER NOT NULL,
                percentage INTEGER NOT NULL,
                passed INTEGER NOT NULL,
                cheat_violations INTEGER DEFAULT 0,
                submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()
        conn.close()

    def get_quizzes(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM quizzes ORDER BY created_at DESC")
        rows = cursor.fetchall()
        quizzes = []
        for r in rows:
            quizzes.append({
                "id": r["id"],
                "title": r["title"],
                "category": r["category"],
                "description": r["description"],
                "durationMinutes": r["duration_minutes"],
                "passingScore": r["passing_score"],
                "questions": json.loads(r["questions_json"])
            })
        conn.close()
        return quizzes

    def save_quiz(self, quiz):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO quizzes (id, title, category, description, duration_minutes, passing_score, tags, questions_json)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                title = excluded.title,
                category = excluded.category,
                description = excluded.description,
                duration_minutes = excluded.duration_minutes,
                passing_score = excluded.passing_score,
                questions_json = excluded.questions_json
        """, (
            quiz["id"],
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

    def save_attempt(self, attempt):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO attempts (id, quiz_id, quiz_title, candidate_name, score, total_questions, percentage, passed, cheat_violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            attempt["id"],
            attempt["quizId"],
            attempt["quizTitle"],
            attempt["candidateName"],
            attempt["score"],
            attempt["totalQuestions"],
            attempt["percentage"],
            1 if attempt["passed"] else 0,
            attempt["cheatViolations"]
        ))
        conn.commit()
        conn.close()

    def get_attempts(self):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM attempts ORDER BY submitted_at DESC")
        rows = cursor.fetchall()
        attempts = []
        for r in rows:
            attempts.append({
                "id": r["id"],
                "quizTitle": r["quiz_title"],
                "candidateName": r["candidate_name"],
                "score": r["score"],
                "totalQuestions": r["total_questions"],
                "percentage": r["percentage"],
                "passed": bool(r["passed"]),
                "cheatViolations": r["cheat_violations"],
                "submittedAt": r["submitted_at"]
            })
        conn.close()
        return attempts


class OnlineQuizApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Online Quiz System — Pro Desktop")
        self.geometry("1100x720")
        self.minsize(950, 620)

        self.db = DatabaseManager()

        # Exam Session Variables
        self.active_quiz = None
        self.current_q_index = 0
        self.user_answers = {}
        self.time_left_seconds = 0
        self.timer_running = False
        self.candidate_name = "Candidate"
        self.cheat_violations = 0

        # Anti-cheat listener: bind window focus loss
        self.bind("<FocusOut>", self.on_focus_loss)

        # Setup Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_sidebar()
        self.setup_content_frames()

        # Show Candidate Arena by default
        self.show_view("candidate")

    def setup_sidebar(self):
        self.sidebar_frame = ctk.CTkFrame(self, width=220, corner_radius=0)
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(5, weight=1)

        # Brand Title
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="⚡ QuizSphere",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(20, 10))

        self.sub_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Desktop Edition 2.0",
            font=ctk.CTkFont(size=11),
            text_color="gray"
        )
        self.sub_label.grid(row=1, column=0, padx=20, pady=(0, 20))

        # Nav Buttons
        self.btn_candidate = ctk.CTkButton(
            self.sidebar_frame,
            text="🎓 Candidate Arena",
            anchor="w",
            command=lambda: self.show_view("candidate")
        )
        self.btn_candidate.grid(row=2, column=0, padx=15, pady=6, sticky="ew")

        self.btn_examiner = ctk.CTkButton(
            self.sidebar_frame,
            text="🛠️ Examiner Studio",
            anchor="w",
            fg_color="transparent",
            hover_color="#1f2937",
            command=lambda: self.show_view("examiner")
        )
        self.btn_examiner.grid(row=3, column=0, padx=15, pady=6, sticky="ew")

        self.btn_analytics = ctk.CTkButton(
            self.sidebar_frame,
            text="📊 Results History",
            anchor="w",
            fg_color="transparent",
            hover_color="#1f2937",
            command=lambda: self.show_view("analytics")
        )
        self.btn_analytics.grid(row=4, column=0, padx=15, pady=6, sticky="ew")

        # Bottom Status
        self.status_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="● Local SQLite Active",
            font=ctk.CTkFont(size=11),
            text_color="#10b981"
        )
        self.status_label.grid(row=6, column=0, padx=20, pady=20)

    def setup_content_frames(self):
        # 1. Candidate View (Lobby & Exam)
        self.candidate_frame = ctk.CTkFrame(self, corner_radius=12)
        self.candidate_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # 2. Examiner View
        self.examiner_frame = ctk.CTkFrame(self, corner_radius=12)
        self.examiner_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

        # 3. Analytics View
        self.analytics_frame = ctk.CTkFrame(self, corner_radius=12)
        self.analytics_frame.grid(row=0, column=1, padx=20, pady=20, sticky="nsew")

    def show_view(self, view_name):
        # Hide all frames
        self.candidate_frame.grid_remove()
        self.examiner_frame.grid_remove()
        self.analytics_frame.grid_remove()

        # Reset button styles
        for btn in [self.btn_candidate, self.btn_examiner, self.btn_analytics]:
            btn.configure(fg_color="transparent")

        if view_name == "candidate":
            self.candidate_frame.grid()
            self.btn_candidate.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            self.render_candidate_lobby()
        elif view_name == "examiner":
            self.examiner_frame.grid()
            self.btn_examiner.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            self.render_examiner_studio()
        elif view_name == "analytics":
            self.analytics_frame.grid()
            self.btn_analytics.configure(fg_color=["#3B8ED0", "#1F6AA5"])
            self.render_analytics_history()

    # -------------------------------------------------------------
    # CANDIDATE ARENA & EXAM ENGINE
    # -------------------------------------------------------------
    def render_candidate_lobby(self):
        for widget in self.candidate_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(
            self.candidate_frame,
            text="Candidate Examination Arena",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(anchor="w", padx=25, pady=(20, 5))

        sub = ctk.CTkLabel(
            self.candidate_frame,
            text="Select an assessment below to launch a proctored examination session.",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        sub.pack(anchor="w", padx=25, pady=(0, 20))

        # Candidate Name Entry
        name_box = ctk.CTkFrame(self.candidate_frame, fg_color="#182234", corner_radius=10)
        name_box.pack(fill="x", padx=25, pady=(0, 15))

        name_lbl = ctk.CTkLabel(name_box, text="Candidate Name:", font=ctk.CTkFont(weight="bold"))
        name_lbl.pack(side="left", padx=15, pady=10)

        self.name_entry = ctk.CTkEntry(name_box, width=250, placeholder_text="Enter your full name")
        self.name_entry.insert(0, self.candidate_name)
        self.name_entry.pack(side="left", padx=10, pady=10)

        # Quizzes Scrollable Container
        scroll = ctk.CTkScrollableFrame(self.candidate_frame, corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        quizzes = self.db.get_quizzes()
        if not quizzes:
            ctk.CTkLabel(scroll, text="No quizzes found. Please create one in Examiner Studio.").pack(pady=40)
            return

        for q in quizzes:
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=8, padx=5)

            title = ctk.CTkLabel(card, text=q["title"], font=ctk.CTkFont(size=16, weight="bold"))
            title.pack(anchor="w", padx=15, pady=(12, 2))

            desc = ctk.CTkLabel(card, text=q.get("description", ""), text_color="gray", font=ctk.CTkFont(size=12))
            desc.pack(anchor="w", padx=15, pady=(0, 8))

            meta_text = f"⏱️ Duration: {q['durationMinutes']} mins   |   ❓ Questions: {len(q['questions'])}   |   🎯 Pass Score: {q['passingScore']}%"
            meta = ctk.CTkLabel(card, text=meta_text, font=ctk.CTkFont(size=12), text_color="#38bdf8")
            meta.pack(anchor="w", padx=15, pady=(0, 10))

            start_btn = ctk.CTkButton(
                card,
                text="Start Assessment ⚡",
                fg_color="#06b6d4",
                hover_color="#0891b2",
                text_color="#030712",
                font=ctk.CTkFont(weight="bold"),
                command=lambda quiz=q: self.start_exam_session(quiz)
            )
            start_btn.pack(anchor="e", padx=15, pady=(0, 12))

    def on_focus_loss(self, event):
        """Proctoring violation listener when window loses focus."""
        if self.timer_running and self.active_quiz:
            self.cheat_violations += 1
            if hasattr(self, "violation_lbl") and self.violation_lbl.winfo_exists():
                self.violation_lbl.configure(text=f"⚠️ Violations: {self.cheat_violations}")
            messagebox.showwarning(
                "Anti-Cheat Alert",
                f"Window focus lost! Focus outside examination window is strictly recorded.\nTotal Violations: {self.cheat_violations}"
            )

    def start_exam_session(self, quiz):
        self.candidate_name = self.name_entry.get().strip() or "Candidate"
        self.active_quiz = quiz
        self.current_q_index = 0
        self.user_answers = {}
        self.cheat_violations = 0
        self.time_left_seconds = quiz["durationMinutes"] * 60
        self.timer_running = True

        self.render_active_exam()
        self.tick_timer()

    def tick_timer(self):
        if not self.timer_running:
            return

        mins = self.time_left_seconds // 60
        secs = self.time_left_seconds % 60
        time_str = f"⏱️ {mins:02d}:{secs:02d}"

        if hasattr(self, "timer_lbl") and self.timer_lbl.winfo_exists():
            self.timer_lbl.configure(text=time_str)
            if self.time_left_seconds <= 60:
                self.timer_lbl.configure(text_color="#ef4444")
            else:
                self.timer_lbl.configure(text_color="#06b6d4")

        if self.time_left_seconds <= 0:
            self.timer_running = False
            messagebox.showinfo("Time Expired", "Exam time is up! Submitting answers automatically.")
            self.submit_exam()
        else:
            self.time_left_seconds -= 1
            self.after(1000, self.tick_timer)

    def render_active_exam(self):
        for widget in self.candidate_frame.winfo_children():
            widget.destroy()

        # Top Bar
        top_bar = ctk.CTkFrame(self.candidate_frame, fg_color="#0f172a", corner_radius=10)
        top_bar.pack(fill="x", padx=20, pady=(15, 10))

        title = ctk.CTkLabel(top_bar, text=self.active_quiz["title"], font=ctk.CTkFont(size=16, weight="bold"))
        title.pack(side="left", padx=15, pady=10)

        self.violation_lbl = ctk.CTkLabel(top_bar, text="⚠️ Violations: 0", text_color="#fca5a5", font=ctk.CTkFont(weight="bold"))
        self.violation_lbl.pack(side="left", padx=20, pady=10)

        self.timer_lbl = ctk.CTkLabel(top_bar, text="⏱️ 00:00", font=ctk.CTkFont(size=18, weight="bold"), text_color="#06b6d4")
        self.timer_lbl.pack(side="right", padx=15, pady=10)

        # Question Content Area
        q = self.active_quiz["questions"][self.current_q_index]

        q_frame = ctk.CTkFrame(self.candidate_frame, fg_color="#1e293b", corner_radius=10)
        q_frame.pack(fill="both", expand=True, padx=20, pady=10)

        q_num = ctk.CTkLabel(
            q_frame,
            text=f"Question {self.current_q_index + 1} of {len(self.active_quiz['questions'])}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#818cf8"
        )
        q_num.pack(anchor="w", padx=20, pady=(15, 5))

        q_text = ctk.CTkLabel(
            q_frame,
            text=q["text"],
            font=ctk.CTkFont(size=16, weight="bold"),
            wraplength=750,
            justify="left"
        )
        q_text.pack(anchor="w", padx=20, pady=(5, 15))

        # Code snippet if present
        if q.get("code"):
            code_box = ctk.CTkTextbox(q_frame, height=90, font=ctk.CTkFont(family="Consolas", size=12), text_color="#38bdf8", fg_color="#050811")
            code_box.insert("1.0", q["code"])
            code_box.configure(state="disabled")
            code_box.pack(fill="x", padx=20, pady=(0, 15))

        # Options Radio Group
        self.selected_opt_var = tk.IntVar(value=self.user_answers.get(q["id"], -1))

        options_container = ctk.CTkFrame(q_frame, fg_color="transparent")
        options_container.pack(fill="x", padx=20, pady=5)

        for idx, opt_text in enumerate(q["options"]):
            radio = ctk.CTkRadioButton(
                options_container,
                text=opt_text,
                variable=self.selected_opt_var,
                value=idx,
                font=ctk.CTkFont(size=14),
                command=lambda opt_idx=idx: self.record_answer(q["id"], opt_idx)
            )
            radio.pack(anchor="w", pady=6)

        # Bottom Action Bar
        action_bar = ctk.CTkFrame(self.candidate_frame, fg_color="transparent")
        action_bar.pack(fill="x", padx=20, pady=(10, 15))

        prev_btn = ctk.CTkButton(
            action_bar,
            text="← Previous",
            state="normal" if self.current_q_index > 0 else "disabled",
            command=self.prev_question
        )
        prev_btn.pack(side="left")

        finish_btn = ctk.CTkButton(
            action_bar,
            text="Finish Early",
            fg_color="#ef4444",
            hover_color="#dc2626",
            command=self.confirm_finish_exam
        )
        finish_btn.pack(side="left", padx=15)

        is_last = self.current_q_index == len(self.active_quiz["questions"]) - 1
        next_text = "Submit Exam ✔️" if is_last else "Next Question →"
        next_cmd = self.confirm_finish_exam if is_last else self.next_question

        next_btn = ctk.CTkButton(
            action_bar,
            text=next_text,
            fg_color="#10b981" if is_last else ["#3B8ED0", "#1F6AA5"],
            command=next_cmd
        )
        next_btn.pack(side="right")

    def record_answer(self, q_id, opt_idx):
        self.user_answers[q_id] = opt_idx

    def prev_question(self):
        if self.current_q_index > 0:
            self.current_q_index -= 1
            self.render_active_exam()

    def next_question(self):
        if self.current_q_index < len(self.active_quiz["questions"]) - 1:
            self.current_q_index += 1
            self.render_active_exam()

    def confirm_finish_exam(self):
        answered = len(self.user_answers)
        total = len(self.active_quiz["questions"])
        msg = f"Candidate: {self.candidate_name}\nAnswered: {answered} of {total}\nProctor Violations: {self.cheat_violations}\n\nAre you sure you want to finalize and submit?"
        if messagebox.askyesno("Confirm Submission", msg):
            self.submit_exam()

    def submit_exam(self):
        self.timer_running = False
        correct = 0
        questions = self.active_quiz["questions"]
        for q in questions:
            if self.user_answers.get(q["id"]) == q["correct"]:
                correct += 1

        total = len(questions)
        pct = round((correct / total) * 100) if total > 0 else 0
        passed = pct >= self.active_quiz["passingScore"]

        attempt = {
            "id": f"att-{int(time.time()*1000)}",
            "quizId": self.active_quiz["id"],
            "quizTitle": self.active_quiz["title"],
            "candidateName": self.candidate_name,
            "score": correct,
            "totalQuestions": total,
            "percentage": pct,
            "passed": passed,
            "cheatViolations": self.cheat_violations
        }

        self.db.save_attempt(attempt)
        self.render_result_screen(attempt)

    def render_result_screen(self, attempt):
        for widget in self.candidate_frame.winfo_children():
            widget.destroy()

        card = ctk.CTkFrame(self.candidate_frame, fg_color="#111827", corner_radius=12)
        card.pack(fill="both", expand=True, padx=30, pady=30)

        status_text = "PASSED 🎉" if attempt["passed"] else "NEEDS IMPROVEMENT ⚠️"
        status_color = "#10b981" if attempt["passed"] else "#ef4444"

        badge = ctk.CTkLabel(card, text=status_text, font=ctk.CTkFont(size=22, weight="bold"), text_color=status_color)
        badge.pack(pady=(30, 5))

        title = ctk.CTkLabel(card, text=attempt["quizTitle"], font=ctk.CTkFont(size=18, weight="bold"))
        title.pack(pady=5)

        candidate = ctk.CTkLabel(card, text=f"Candidate: {attempt['candidateName']}", font=ctk.CTkFont(size=14), text_color="#38bdf8")
        candidate.pack(pady=5)

        score_lbl = ctk.CTkLabel(card, text=f"Score: {attempt['score']} / {attempt['totalQuestions']} ({attempt['percentage']}%)", font=ctk.CTkFont(size=24, weight="bold"))
        score_lbl.pack(pady=15)

        cheat_lbl = ctk.CTkLabel(card, text=f"Proctor Violations Logged: {attempt['cheatViolations']}", text_color="#fca5a5")
        cheat_lbl.pack(pady=5)

        back_btn = ctk.CTkButton(
            card,
            text="Back to Lobby",
            command=self.render_candidate_lobby
        )
        back_btn.pack(pady=25)

    # -------------------------------------------------------------
    # EXAMINER STUDIO
    # -------------------------------------------------------------
    def render_examiner_studio(self):
        for widget in self.examiner_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(
            self.examiner_frame,
            text="Examiner Studio & Quiz Builder",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(anchor="w", padx=25, pady=(20, 5))

        sub = ctk.CTkLabel(
            self.examiner_frame,
            text="Create, edit, and organize question banks directly on your system.",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        sub.pack(anchor="w", padx=25, pady=(0, 15))

        top_actions = ctk.CTkFrame(self.examiner_frame, fg_color="transparent")
        top_actions.pack(fill="x", padx=25, pady=(0, 15))

        new_btn = ctk.CTkButton(
            top_actions,
            text="+ Create New Quiz",
            fg_color="#6366f1",
            hover_color="#4f46e5",
            command=self.open_new_quiz_dialog
        )
        new_btn.pack(side="left")

        # Scrollable Quizzes
        scroll = ctk.CTkScrollableFrame(self.examiner_frame, corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        quizzes = self.db.get_quizzes()
        for q in quizzes:
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=6, padx=5)

            ctk.CTkLabel(card, text=q["title"], font=ctk.CTkFont(size=15, weight="bold")).pack(anchor="w", padx=15, pady=(10, 2))
            ctk.CTkLabel(card, text=f"{q['category']} | {len(q['questions'])} Questions | {q['durationMinutes']} mins", text_color="gray", font=ctk.CTkFont(size=12)).pack(anchor="w", padx=15, pady=(0, 8))

            action_row = ctk.CTkFrame(card, fg_color="transparent")
            action_row.pack(anchor="e", padx=15, pady=(0, 10))

            del_btn = ctk.CTkButton(
                action_row,
                text="Delete",
                width=75,
                fg_color="#ef4444",
                hover_color="#dc2626",
                command=lambda quiz_id=q["id"]: self.delete_quiz_action(quiz_id)
            )
            del_btn.pack(side="right", padx=5)

    def delete_quiz_action(self, quiz_id):
        if messagebox.askyesno("Delete Quiz", "Are you sure you want to delete this quiz?"):
            self.db.delete_quiz(quiz_id)
            self.render_examiner_studio()

    def open_new_quiz_dialog(self):
        dialog = ctk.CTkToplevel(self)
        dialog.title("Create Assessment")
        dialog.geometry("600x650")

        ctk.CTkLabel(dialog, text="New Quiz Details", font=ctk.CTkFont(size=18, weight="bold")).pack(pady=15)

        title_e = ctk.CTkEntry(dialog, placeholder_text="Quiz Title", width=450)
        title_e.pack(pady=8)

        cat_e = ctk.CTkEntry(dialog, placeholder_text="Category (e.g. Python, Algorithms)", width=450)
        cat_e.pack(pady=8)

        dur_e = ctk.CTkEntry(dialog, placeholder_text="Duration in minutes (e.g. 10)", width=450)
        dur_e.insert(0, "10")
        dur_e.pack(pady=8)

        pass_e = ctk.CTkEntry(dialog, placeholder_text="Passing Score % (e.g. 70)", width=450)
        pass_e.insert(0, "70")
        pass_e.pack(pady=8)

        ctk.CTkLabel(dialog, text="First Question Prompt:", font=ctk.CTkFont(weight="bold")).pack(pady=(15, 5))
        q_text = ctk.CTkTextbox(dialog, height=60, width=450)
        q_text.insert("1.0", "What is the primary function of Python's pip command?")
        q_text.pack(pady=5)

        opt1 = ctk.CTkEntry(dialog, placeholder_text="Option 1 (Correct)", width=450)
        opt1.insert(0, "Package installer and manager")
        opt1.pack(pady=4)

        opt2 = ctk.CTkEntry(dialog, placeholder_text="Option 2", width=450)
        opt2.insert(0, "Compiler optimization engine")
        opt2.pack(pady=4)

        opt3 = ctk.CTkEntry(dialog, placeholder_text="Option 3", width=450)
        opt3.insert(0, "Database migration runner")
        opt3.pack(pady=4)

        opt4 = ctk.CTkEntry(dialog, placeholder_text="Option 4", width=450)
        opt4.insert(0, "Web server gateway interface")
        opt4.pack(pady=4)

        def save_action():
            title = title_e.get().strip() or "Untitled Quiz"
            new_quiz = {
                "id": f"quiz-{int(time.time()*1000)}",
                "title": title,
                "category": cat_e.get().strip() or "General",
                "durationMinutes": int(dur_e.get().strip() or 10),
                "passingScore": int(pass_e.get().strip() or 70),
                "questions": [
                    {
                        "id": "q1",
                        "text": q_text.get("1.0", "end-1c"),
                        "options": [opt1.get(), opt2.get(), opt3.get(), opt4.get()],
                        "correct": 0,
                        "explanation": "pip is the official standard package manager for Python."
                    }
                ]
            }
            self.db.save_quiz(new_quiz)
            dialog.destroy()
            self.render_examiner_studio()
            messagebox.showinfo("Saved", f"Quiz '{title}' created successfully!")

        save_btn = ctk.CTkButton(dialog, text="Save Quiz", fg_color="#10b981", command=save_action)
        save_btn.pack(pady=20)

    # -------------------------------------------------------------
    # ANALYTICS & RESULTS HISTORY
    # -------------------------------------------------------------
    def render_analytics_history(self):
        for widget in self.analytics_frame.winfo_children():
            widget.destroy()

        header = ctk.CTkLabel(
            self.analytics_frame,
            text="Candidate Exam Records & History",
            font=ctk.CTkFont(size=22, weight="bold")
        )
        header.pack(anchor="w", padx=25, pady=(20, 5))

        sub = ctk.CTkLabel(
            self.analytics_frame,
            text="Audit log of candidate submissions, scores, and proctoring metrics.",
            font=ctk.CTkFont(size=13),
            text_color="gray"
        )
        sub.pack(anchor="w", padx=25, pady=(0, 15))

        scroll = ctk.CTkScrollableFrame(self.analytics_frame, corner_radius=10)
        scroll.pack(fill="both", expand=True, padx=25, pady=(0, 20))

        attempts = self.db.get_attempts()
        if not attempts:
            ctk.CTkLabel(scroll, text="No examination attempts logged yet.").pack(pady=40)
            return

        for a in attempts:
            card = ctk.CTkFrame(scroll, corner_radius=10, fg_color="#1e293b")
            card.pack(fill="x", pady=6, padx=5)

            status_color = "#10b981" if a["passed"] else "#ef4444"
            status_text = "PASSED" if a["passed"] else "FAILED"

            ctk.CTkLabel(card, text=f"{a['quizTitle']} — {status_text}", font=ctk.CTkFont(size=15, weight="bold"), text_color=status_color).pack(anchor="w", padx=15, pady=(10, 2))
            meta = f"Candidate: {a['candidateName']}   |   Score: {a['score']}/{a['totalQuestions']} ({a['percentage']}%)   |   Violations: {a['cheatViolations']}   |   Date: {a['submittedAt']}"
            ctk.CTkLabel(card, text=meta, font=ctk.CTkFont(size=12), text_color="gray").pack(anchor="w", padx=15, pady=(0, 10))


if __name__ == "__main__":
    app = OnlineQuizApp()
    app.mainloop()
