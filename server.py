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
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from ai_quiz_generator import generate_quiz_with_ai

app = FastAPI(
    title="Online Quiz System API",
    description="Multi-platform backend for Admin, Teacher, and Student workflows",
    version="2.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_PATH = "quiz_system.db"

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
    conn.commit()
    conn.close()

init_db()


# ---------------- API ENDPOINTS ----------------

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
