"""
Online Quiz System - Unified Python Backend (FastAPI + WebSockets)
Features:
- 3 Roles: Administrator, Teacher/Faculty, Student
- 🤖 AI Quiz Generator endpoint (/api/ai-generate)
- Quiz Join Code endpoint (/api/quizzes/code/{code})
- Teacher Class Reports endpoint (/api/teacher/reports)
- Mobile & Desktop static client hosting
"""

import os
import json
import random
import sqlite3
import datetime
import io
import csv
from contextlib import asynccontextmanager
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ai_quiz_generator import generate_quiz_with_ai
from backend.core.telemetry import RequestIDMiddleware
from backend.core.bootstrap import init_and_seed_db
from backend.api.v1.router import api_v1_router

DB_PATH = "quiz_system.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
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
    # Migrate existing database columns
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
    conn.close()

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    init_and_seed_db()
    yield

app = FastAPI(
    title="Online Quiz System API",
    description="Enterprise Multi-Tenant Assessment Engine with Server Deadlines & Durable Autosave",
    version="2.2.0",
    lifespan=lifespan
)

app.add_middleware(RequestIDMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_v1_router)

# Pydantic Schemas
class QuestionSchema(BaseModel):
    id: str
    text: str
    code: Optional[str] = None
    options: List[str]
    correct: int
    explanation: Optional[str] = ""

class QuizCreateSchema(BaseModel):
    id: Optional[str] = None
    joinCode: Optional[str] = None
    teacherName: str = "Prof. Alan Turing"
    title: str
    category: str = "General"
    description: Optional[str] = ""
    durationMinutes: int = 10
    passingScore: int = 70
    tags: List[str] = []
    questions: List[QuestionSchema]

class SubmitAnswersSchema(BaseModel):
    studentName: str
    answers: Dict[str, int]
    cheatViolations: int = 0

class AIGenerateRequest(BaseModel):
    topic: str
    numQuestions: int = 5
    difficulty: str = "Medium"

class UserLoginSchema(BaseModel):
    username: str
    password: str

class UserRegisterSchema(BaseModel):
    username: str
    password: str
    role: str = "student"
    full_name: str
    department: Optional[str] = "Computer Science & Engineering"

class CurrentUserQuery(BaseModel):
    username: Optional[str] = None
    user_id: Optional[str] = None


# ---------------- API ENDPOINTS ----------------

@app.get("/favicon.ico", include_in_schema=False)
def favicon():
    return Response(status_code=204)

@app.api_route("/api/get_current_user", methods=["GET", "POST"])
def api_get_current_user(query: Optional[CurrentUserQuery] = None):
    uname = query.username if query else None
    uid = query.user_id if query else None
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if uid:
        cursor.execute("SELECT * FROM users WHERE id = ?", (uid,))
    elif uname:
        cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (uname.strip(),))
    else:
        cursor.execute("SELECT * FROM users ORDER BY created_at ASC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="User not found")
    keys = row.keys()
    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"].lower(),
        "full_name": row["full_name"],
        "department": row["department"] if "department" in keys else "General"
    }

@app.post("/api/auth/login")
def api_auth_login(req: UserLoginSchema):
    """Authenticates username and password against users table."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE LOWER(username) = LOWER(?)", (req.username.strip(),))
    row = cursor.fetchone()
    conn.close()
    if not row or row["password"] != req.password.strip():
        raise HTTPException(status_code=401, detail="Invalid credentials. Check your username and password.")
    keys = row.keys()
    return {
        "id": row["id"],
        "username": row["username"],
        "role": row["role"].lower(),
        "full_name": row["full_name"],
        "department": row["department"] if "department" in keys else "General"
    }

@app.post("/api/auth/register")
def api_auth_register(req: UserRegisterSchema):
    """Registers a new student or faculty account."""
    username = req.username.strip()
    password = req.password.strip()
    full_name = req.full_name.strip()
    department = (req.department or "General").strip()
    role = req.role.strip().lower()

    if len(username) < 3:
        raise HTTPException(status_code=400, detail="Username must be at least 3 characters.")
    if len(password) < 4:
        raise HTTPException(status_code=400, detail="Password must be at least 4 characters.")
    if not full_name:
        raise HTTPException(status_code=400, detail="Full name is required.")

    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    if cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=400, detail=f"Username '{username}' already exists. Please choose a different username.")

    user_id = f"usr-{int(datetime.datetime.now().timestamp() * 1000)}"
    cursor.execute("""
        INSERT INTO users (id, username, password, role, full_name, department)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (user_id, username, password, role, full_name, department))
    conn.commit()
    conn.close()

    return {
        "id": user_id,
        "username": username,
        "role": role,
        "full_name": full_name,
        "department": department
    }


@app.post("/api/ai-generate")
def ai_generate_quiz(req: AIGenerateRequest):
    """Generates structured multiple-choice questions for teachers based on topic & difficulty."""
    questions = generate_quiz_with_ai(
        topic=req.topic,
        num_questions=req.numQuestions,
        difficulty=req.difficulty
    )
    return {
        "topic": req.topic,
        "difficulty": req.difficulty,
        "questions": questions
    }

@app.get("/api/quizzes")
def get_all_quizzes():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes ORDER BY created_at DESC")
    rows = cursor.fetchall()
    quizzes = []
    for r in rows:
        quizzes.append({
            "id": r["id"],
            "joinCode": r["join_code"],
            "teacherName": r["teacher_name"],
            "title": r["title"],
            "category": r["category"],
            "description": r["description"],
            "durationMinutes": r["duration_minutes"],
            "passingScore": r["passing_score"],
            "tags": json.loads(r["tags"] or "[]"),
            "questions": json.loads(r["questions_json"]),
            "createdAt": r["created_at"]
        })
    conn.close()
    return quizzes

@app.get("/api/quizzes/code/{code}")
def get_quiz_by_join_code(code: str):
    """Enables students to join an assessment via 6-char Quiz Code."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE UPPER(join_code) = UPPER(?)", (code.strip(),))
    r = cursor.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail=f"No quiz found with code '{code}'")
    return {
        "id": r["id"],
        "joinCode": r["join_code"],
        "teacherName": r["teacher_name"],
        "title": r["title"],
        "category": r["category"],
        "description": r["description"],
        "durationMinutes": r["duration_minutes"],
        "passingScore": r["passing_score"],
        "tags": json.loads(r["tags"] or "[]"),
        "questions": json.loads(r["questions_json"])
    }

@app.post("/api/quizzes")
def save_or_update_quiz(quiz: QuizCreateSchema):
    quiz_id = quiz.id or f"quiz-{int(datetime.datetime.now().timestamp() * 1000)}"
    join_code = quiz.joinCode or f"QZ-{random.randint(1000, 9999)}"
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO quizzes (id, join_code, teacher_name, title, category, description, duration_minutes, passing_score, tags, questions_json)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title = excluded.title,
            category = excluded.category,
            description = excluded.description,
            duration_minutes = excluded.duration_minutes,
            passing_score = excluded.passing_score,
            tags = excluded.tags,
            questions_json = excluded.questions_json
    """, (
        quiz_id,
        join_code,
        quiz.teacherName,
        quiz.title,
        quiz.category,
        quiz.description,
        quiz.durationMinutes,
        quiz.passingScore,
        json.dumps(quiz.tags),
        json.dumps([q.model_dump() for q in quiz.questions])
    ))
    conn.commit()
    conn.close()
    return {"status": "success", "id": quiz_id, "joinCode": join_code}

@app.post("/api/quizzes/{quiz_id}/submit")
def submit_quiz_attempt(quiz_id: str, payload: SubmitAnswersSchema):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    quiz_row = cursor.fetchone()
    if not quiz_row:
        conn.close()
        raise HTTPException(status_code=404, detail="Quiz not found")

    questions = json.loads(quiz_row["questions_json"])
    total_questions = len(questions)
    correct_count = 0
    feedback = []

    for q in questions:
        user_choice = payload.answers.get(q["id"])
        is_correct = user_choice == q["correct"]
        if is_correct:
            correct_count += 1
        feedback.append({
            "id": q["id"],
            "prompt": q["text"],
            "userChoice": user_choice,
            "correctChoice": q["correct"],
            "isCorrect": is_correct,
            "explanation": q.get("explanation", "")
        })

    percentage = round((correct_count / total_questions) * 100) if total_questions > 0 else 0
    passed = 1 if percentage >= quiz_row["passing_score"] else 0
    attempt_id = f"attempt-{int(datetime.datetime.now().timestamp() * 1000)}"

    cursor.execute("PRAGMA table_info(attempts)")
    attempt_cols = [c[1] for c in cursor.fetchall()]

    if "candidate_name" in attempt_cols:
        cursor.execute("""
            INSERT INTO attempts (id, quiz_id, join_code, quiz_title, teacher_name, student_name, candidate_name, score, total_questions, percentage, passed, cheat_violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            attempt_id,
            quiz_id,
            quiz_row["join_code"],
            quiz_row["title"],
            quiz_row["teacher_name"],
            payload.studentName,
            payload.studentName,
            correct_count,
            total_questions,
            percentage,
            passed,
            payload.cheatViolations
        ))
    else:
        cursor.execute("""
            INSERT INTO attempts (id, quiz_id, join_code, quiz_title, teacher_name, student_name, score, total_questions, percentage, passed, cheat_violations)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            attempt_id,
            quiz_id,
            quiz_row["join_code"],
            quiz_row["title"],
            quiz_row["teacher_name"],
            payload.studentName,
            correct_count,
            total_questions,
            percentage,
            passed,
            payload.cheatViolations
        ))
    conn.commit()
    conn.close()

    return {
        "attemptId": attempt_id,
        "score": correct_count,
        "totalQuestions": total_questions,
        "percentage": percentage,
        "passed": bool(passed),
        "passingScore": quiz_row["passing_score"],
        "cheatViolations": payload.cheatViolations,
        "teacherName": quiz_row["teacher_name"],
        "feedback": feedback
    }

@app.get("/api/teacher/reports")
def get_teacher_class_reports(teacher: Optional[str] = None):
    """Returns student submission records for the teacher's quizzes."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    if teacher:
        cursor.execute("SELECT * FROM attempts WHERE teacher_name = ? ORDER BY submitted_at DESC", (teacher,))
    else:
        cursor.execute("SELECT * FROM attempts ORDER BY submitted_at DESC")
    rows = cursor.fetchall()
    reports = []
    for r in rows:
        reports.append({
            "id": r["id"],
            "quizTitle": r["quiz_title"],
            "joinCode": r["join_code"],
            "teacherName": r["teacher_name"],
            "studentName": r["student_name"],
            "score": r["score"],
            "totalQuestions": r["total_questions"],
            "percentage": r["percentage"],
            "passed": bool(r["passed"]),
            "cheatViolations": r["cheat_violations"],
            "submittedAt": r["submitted_at"]
        })
    conn.close()
    return reports

@app.get("/api/admin/stats")
def get_admin_global_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM quizzes")
    total_quizzes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), SUM(passed) FROM attempts")
    row = cursor.fetchone()
    total_attempts = row[0] or 0
    total_passed = row[1] or 0
    pass_rate = round((total_passed / total_attempts) * 100) if total_attempts > 0 else 0

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

@app.get("/api/admin/users")
def get_admin_all_users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name, department, created_at FROM users ORDER BY created_at ASC")
    users_rows = cursor.fetchall()

    users_list = []
    for idx, u in enumerate(users_rows, start=1):
        uname = u["username"].strip()
        fname = u["full_name"].strip()
        cursor.execute("""
            SELECT COUNT(*), SUM(passed), AVG(percentage), MAX(percentage), SUM(cheat_violations), MAX(submitted_at)
            FROM attempts
            WHERE LOWER(student_name) = LOWER(?) OR LOWER(student_name) = LOWER(?)
        """, (fname, uname))
        stat_row = cursor.fetchone()
        attempts_count = stat_row[0] or 0
        passed_count = stat_row[1] or 0
        avg_score = round(stat_row[2]) if stat_row[2] is not None else 0
        highest_score = stat_row[3] or 0
        violations = stat_row[4] or 0
        last_attempt = stat_row[5] or None

        pass_rate = round((passed_count / attempts_count) * 100) if attempts_count > 0 else 0

        users_list.append({
            "userNo": idx,
            "id": u["id"],
            "username": u["username"],
            "fullName": u["full_name"],
            "role": u["role"].lower(),
            "department": u["department"] or "General",
            "createdAt": u["created_at"],
            "totalAttempts": attempts_count,
            "passedAttempts": passed_count,
            "failedAttempts": max(0, attempts_count - passed_count),
            "passRate": pass_rate,
            "avgScore": avg_score,
            "highestScore": highest_score,
            "totalViolations": violations,
            "latestAttempt": last_attempt
        })
    conn.close()
    return users_list

@app.get("/api/admin/users/{user_id}/report")
def get_admin_user_report(user_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT id, username, role, full_name, department, created_at FROM users WHERE id = ?", (user_id,))
    user_row = cursor.fetchone()
    if not user_row:
        conn.close()
        raise HTTPException(status_code=404, detail="User not found")

    uname = user_row["username"].strip()
    fname = user_row["full_name"].strip()

    cursor.execute("""
        SELECT * FROM attempts
        WHERE LOWER(student_name) = LOWER(?) OR LOWER(student_name) = LOWER(?)
        ORDER BY submitted_at DESC
    """, (fname, uname))
    attempts_rows = cursor.fetchall()
    attempts_list = []
    total_passed = 0
    total_violations = 0
    percentages = []

    for r in attempts_rows:
        keys = r.keys()
        pct = r["percentage"]
        percentages.append(pct)
        passed = bool(r["passed"])
        if passed:
            total_passed += 1
        violations = r["cheat_violations"] if "cheat_violations" in keys else 0
        total_violations += violations

        attempts_list.append({
            "id": r["id"],
            "quizId": r["quiz_id"],
            "quizTitle": r["quiz_title"],
            "joinCode": r["join_code"] if "join_code" in keys else "QZ-1001",
            "teacherName": r["teacher_name"] if "teacher_name" in keys else "Prof. Alan Turing",
            "studentName": r["student_name"] if "student_name" in keys else fname,
            "score": r["score"],
            "totalQuestions": r["total_questions"],
            "percentage": pct,
            "passed": passed,
            "cheatViolations": violations,
            "submittedAt": r["submitted_at"]
        })
    conn.close()

    total_attempts = len(attempts_list)
    avg_score = round(sum(percentages) / total_attempts) if total_attempts > 0 else 0
    highest_score = max(percentages) if percentages else 0
    lowest_score = min(percentages) if percentages else 0
    pass_rate = round((total_passed / total_attempts) * 100) if total_attempts > 0 else 0

    return {
        "user": {
            "id": user_row["id"],
            "username": user_row["username"],
            "fullName": user_row["full_name"],
            "role": user_row["role"].lower(),
            "department": user_row["department"] or "General",
            "createdAt": user_row["created_at"]
        },
        "summary": {
            "totalAttempts": total_attempts,
            "passedAttempts": total_passed,
            "failedAttempts": max(0, total_attempts - total_passed),
            "passRate": pass_rate,
            "avgScore": avg_score,
            "highestScore": highest_score,
            "lowestScore": lowest_score,
            "totalViolations": total_violations
        },
        "attempts": attempts_list
    }

@app.get("/api/admin/analytics")
def get_admin_comprehensive_analytics():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # User counts
    cursor.execute("SELECT COUNT(*), SUM(CASE WHEN LOWER(role) = 'student' THEN 1 ELSE 0 END), SUM(CASE WHEN LOWER(role) = 'faculty' THEN 1 ELSE 0 END) FROM users")
    user_counts = cursor.fetchone()
    total_users = user_counts[0] or 0
    total_students = user_counts[1] or 0
    total_faculty = user_counts[2] or 0

    # Attempts counts & aggregate metrics
    cursor.execute("SELECT COUNT(*), SUM(passed), AVG(percentage), SUM(cheat_violations) FROM attempts")
    att_stats = cursor.fetchone()
    total_attempts = att_stats[0] or 0
    total_passed = att_stats[1] or 0
    overall_pass_rate = round((total_passed / total_attempts) * 100) if total_attempts > 0 else 0
    platform_avg_score = round(att_stats[2]) if att_stats[2] is not None else 0
    total_violations = att_stats[3] or 0

    # Quizzes count & breakdown
    cursor.execute("SELECT id, title, category, join_code, teacher_name, duration_minutes, passing_score FROM quizzes ORDER BY created_at DESC")
    quiz_rows = cursor.fetchall()
    quizzes_analytics = []

    for q in quiz_rows:
        qid = q["id"]
        cursor.execute("""
            SELECT COUNT(*), SUM(passed), AVG(percentage), MAX(percentage), MIN(percentage), SUM(cheat_violations)
            FROM attempts
            WHERE quiz_id = ?
        """, (qid,))
        q_stats = cursor.fetchone()
        q_attempts = q_stats[0] or 0
        q_passed = q_stats[1] or 0
        q_pass_rate = round((q_passed / q_attempts) * 100) if q_attempts > 0 else 0
        q_avg_score = round(q_stats[2]) if q_stats[2] is not None else 0
        q_highest = q_stats[3] if q_stats[3] is not None else 0
        q_lowest = q_stats[4] if q_stats[4] is not None else 0
        q_violations = q_stats[5] or 0

        # Difficulty rating calculation
        if q_attempts == 0:
            difficulty = "Balanced"
        elif q_pass_rate >= 80:
            difficulty = "Beginner (High Pass)"
        elif q_pass_rate >= 50:
            difficulty = "Balanced (Standard)"
        else:
            difficulty = "Rigorous (Challenging)"

        quizzes_analytics.append({
            "id": q["id"],
            "title": q["title"],
            "category": q["category"],
            "joinCode": q["join_code"],
            "teacherName": q["teacher_name"],
            "durationMinutes": q["duration_minutes"],
            "passingScore": q["passing_score"],
            "attemptsCount": q_attempts,
            "passRate": q_pass_rate,
            "avgScore": q_avg_score,
            "highestScore": q_highest,
            "lowestScore": q_lowest,
            "totalViolations": q_violations,
            "difficultyRating": difficulty
        })

    # Recent submissions audit
    cursor.execute("SELECT * FROM attempts ORDER BY submitted_at DESC LIMIT 50")
    sub_rows = cursor.fetchall()
    recent_submissions = []
    for r in sub_rows:
        keys = r.keys()
        recent_submissions.append({
            "id": r["id"],
            "quizTitle": r["quiz_title"],
            "joinCode": r["join_code"] if "join_code" in keys else "QZ-1001",
            "teacherName": r["teacher_name"] if "teacher_name" in keys else "Prof. Alan Turing",
            "studentName": r["student_name"] if "student_name" in keys else "Candidate",
            "score": r["score"],
            "totalQuestions": r["total_questions"],
            "percentage": r["percentage"],
            "passed": bool(r["passed"]),
            "cheatViolations": r["cheat_violations"] if "cheat_violations" in keys else 0,
            "submittedAt": r["submitted_at"]
        })

    conn.close()

    return {
        "kpis": {
            "totalUsers": total_users,
            "totalStudents": total_students,
            "totalFaculty": total_faculty,
            "totalQuizzes": len(quiz_rows),
            "totalAttempts": total_attempts,
            "overallPassRate": overall_pass_rate,
            "platformAvgScore": platform_avg_score,
            "totalViolations": total_violations
        },
        "quizzesAnalytics": quizzes_analytics,
        "recentSubmissions": recent_submissions
    }

@app.get("/api/admin/export/users.csv")
def export_admin_users_csv():
    users_data = get_admin_all_users()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "User No", "User ID", "Full Name", "Username", "Role", "Department",
        "Total Attempts", "Passed Attempts", "Failed Attempts", "Pass Rate (%)",
        "Average Score (%)", "Highest Score (%)", "Total Violations", "Registered At"
    ])
    for u in users_data:
        writer.writerow([
            u["userNo"], u["id"], u["fullName"], u["username"], u["role"].upper(), u["department"],
            u["totalAttempts"], u["passedAttempts"], u["failedAttempts"], f"{u['passRate']}%",
            f"{u['avgScore']}%", f"{u['highestScore']}%", u["totalViolations"], u["createdAt"]
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=quizsphere_users_roster.csv"}
    )

@app.get("/api/admin/export/submissions.csv")
def export_admin_submissions_csv():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM attempts ORDER BY submitted_at DESC")
    rows = cursor.fetchall()
    conn.close()

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        "Attempt ID", "Candidate Name", "Quiz Title", "Join Code", "Teacher / Examiner",
        "Score", "Total Questions", "Percentage (%)", "Result", "Proctoring Violations", "Submitted At"
    ])
    for r in rows:
        keys = r.keys()
        writer.writerow([
            r["id"],
            r["student_name"] if "student_name" in keys else "Candidate",
            r["quiz_title"],
            r["join_code"] if "join_code" in keys else "QZ-1001",
            r["teacher_name"] if "teacher_name" in keys else "Prof. Alan Turing",
            r["score"],
            r["total_questions"],
            f"{r['percentage']}%",
            "PASSED" if r["passed"] else "FAILED",
            r["cheat_violations"] if "cheat_violations" in keys else 0,
            r["submitted_at"]
        ])
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=all_quiz_submissions_audit.csv"}
    )


# WebSocket Real-Time Clock & Proctoring Hub
class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, List[WebSocket]] = {}

    async def connect(self, session_id: str, websocket: WebSocket):
        await websocket.accept()
        if session_id not in self.active_connections:
            self.active_connections[session_id] = []
        self.active_connections[session_id].append(websocket)

    def disconnect(self, session_id: str, websocket: WebSocket):
        if session_id in self.active_connections:
            self.active_connections[session_id].remove(websocket)

manager = ConnectionManager()

@app.websocket("/ws/exam/{session_id}")
async def exam_websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            if data.get("type") == "HEARTBEAT":
                await websocket.send_json({"type": "PONG", "timestamp": datetime.datetime.now().isoformat()})
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)

# Mount static files for Android/mobile/web access
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Starting Online Quiz System Server on http://localhost:8000 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
