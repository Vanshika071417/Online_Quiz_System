"""
Online Quiz System - Unified Python Backend (FastAPI + WebSockets)
Provides RESTful APIs for Quizzes, Submissions, Analytics, and Real-Time Examination Sync.
Also mounts static files to serve the Mobile and Web clients simultaneously.
"""

import os
import json
import sqlite3
import datetime
from typing import List, Optional, Dict, Any
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

app = FastAPI(
    title="Online Quiz System API",
    description="High-performance Python backend for Desktop and Mobile quiz assessment",
    version="2.0.0"
)

# CORS Middleware
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
    title: str
    category: str = "General"
    description: Optional[str] = ""
    durationMinutes: int = 10
    passingScore: int = 70
    tags: List[str] = []
    questions: List[QuestionSchema]

class SubmitAnswersSchema(BaseModel):
    candidateName: str
    answers: Dict[str, int]
    cheatViolations: int = 0


def init_db():
    conn = sqlite3.connect(DB_PATH)
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
            submitted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (quiz_id) REFERENCES quizzes(id)
        )
    """)
    conn.commit()

    # Seed initial quizzes if empty
    cursor.execute("SELECT COUNT(*) FROM quizzes")
    count = cursor.fetchone()[0]
    if count == 0:
        seed_quizzes = [
            {
                "id": "quiz-web-dev",
                "title": "Full Stack Web & System Architecture",
                "category": "Software Engineering",
                "description": "Evaluate your core knowledge of modern web protocols, asynchronous JavaScript, database transactions, and scalable architecture.",
                "durationMinutes": 10,
                "passingScore": 70,
                "tags": ["JavaScript", "HTTP", "Databases"],
                "questions": [
                    {
                        "id": "q1",
                        "text": "What will be logged to the console by the following asynchronous JavaScript execution?",
                        "code": "console.log('1');\nsetTimeout(() => console.log('2'), 0);\nPromise.resolve().then(() => console.log('3'));\nconsole.log('4');",
                        "options": ["1, 2, 3, 4", "1, 4, 3, 2", "1, 4, 2, 3", "3, 1, 4, 2"],
                        "correct": 1,
                        "explanation": "Synchronous statements run first ('1', '4'), followed by microtasks in the job queue (Promise '3'), and then macrotasks ('2')."
                    },
                    {
                        "id": "q2",
                        "text": "In the CAP theorem of distributed systems, which combination is guaranteed by a traditional single-leader relational database system (e.g. standard PostgreSQL)?",
                        "code": None,
                        "options": [
                            "Consistency and Partition Tolerance (CP)",
                            "Availability and Partition Tolerance (AP)",
                            "Consistency and Availability (CA) under single-partition guarantees",
                            "Availability, Consistency, and Partition Tolerance simultaneously"
                        ],
                        "correct": 2,
                        "explanation": "Single-node relational systems prioritize Consistency and Availability without built-in network partitioning tolerance across distributed clusters."
                    },
                    {
                        "id": "q3",
                        "text": "Which HTTP header is primarily used to prevent Cross-Site Scripting (XSS) attacks by restricting the origins of executable scripts?",
                        "code": None,
                        "options": [
                            "Access-Control-Allow-Origin",
                            "Content-Security-Policy (CSP)",
                            "X-Frame-Options",
                            "Strict-Transport-Security (HSTS)"
                        ],
                        "correct": 1,
                        "explanation": "Content-Security-Policy (CSP) allows server operators to restrict where executable scripts and stylesheets can be loaded."
                    }
                ]
            },
            {
                "id": "quiz-python-cs",
                "title": "Python Core & Data Structures",
                "category": "Computer Science",
                "description": "Test your mastery of Python memory management, GIL, generators, and algorithm complexity.",
                "durationMinutes": 8,
                "passingScore": 60,
                "tags": ["Python", "Algorithms", "Memory"],
                "questions": [
                    {
                        "id": "py-q1",
                        "text": "What is the average time complexity of item lookup in a Python dictionary (hash table)?",
                        "code": None,
                        "options": ["O(1)", "O(log N)", "O(N)", "O(N log N)"],
                        "correct": 0,
                        "explanation": "Python dictionaries are implemented using open-addressing hash tables, giving average O(1) key lookups."
                    },
                    {
                        "id": "py-q2",
                        "text": "Which statement best describes Python's Global Interpreter Lock (GIL)?",
                        "code": None,
                        "options": [
                            "A mechanism allowing multiple native threads to execute Python bytecode simultaneously",
                            "A mutex that prevents multiple native threads from executing Python bytecodes at once",
                            "A garbage collection module responsible for circular reference cleanup",
                            "A compiler optimization for vectorized math calculations"
                        ],
                        "correct": 1,
                        "explanation": "The GIL is a mutex used by CPython to prevent race conditions and synchronize thread access to Python object memory."
                    }
                ]
            }
        ]

        for q in seed_quizzes:
            cursor.execute("""
                INSERT INTO quizzes (id, title, category, description, duration_minutes, passing_score, tags, questions_json)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                q["id"],
                q["title"],
                q["category"],
                q["description"],
                q["durationMinutes"],
                q["passingScore"],
                json.dumps(q["tags"]),
                json.dumps(q["questions"])
            ))
        conn.commit()
    conn.close()

init_db()


# API Endpoints
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
            "title": r["title"],
            "category": r["category"],
            "description": r["description"],
            "durationMinutes": r["duration_minutes"],
            "passingScore": r["passing_score"],
            "tags": json.loads(r["tags"] or "[]"),
            "questions": json.loads(r["questions_json"])
        })
    conn.close()
    return quizzes

@app.get("/api/quizzes/{quiz_id}")
def get_quiz_by_id(quiz_id: str):
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM quizzes WHERE id = ?", (quiz_id,))
    r = cursor.fetchone()
    conn.close()
    if not r:
        raise HTTPException(status_code=404, detail="Quiz not found")
    return {
        "id": r["id"],
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
    conn = sqlite3.connect(DB_PATH)
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
            tags = excluded.tags,
            questions_json = excluded.questions_json
    """, (
        quiz_id,
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
    return {"status": "success", "id": quiz_id}

@app.delete("/api/quizzes/{quiz_id}")
def delete_quiz(quiz_id: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM quizzes WHERE id = ?", (quiz_id,))
    conn.commit()
    conn.close()
    return {"status": "deleted"}

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
        INSERT INTO attempts (id, quiz_id, quiz_title, candidate_name, score, total_questions, percentage, passed, cheat_violations)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        attempt_id,
        quiz_id,
        quiz_row["title"],
        payload.candidateName,
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
        "feedback": feedback
    }

@app.get("/api/stats")
def get_dashboard_stats():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM quizzes")
    total_quizzes = cursor.fetchone()[0]

    cursor.execute("SELECT COUNT(*), SUM(passed) FROM attempts")
    row = cursor.fetchone()
    total_attempts = row[0] or 0
    total_passed = row[1] or 0
    pass_rate = round((total_passed / total_attempts) * 100) if total_attempts > 0 else 0

    cursor.execute("SELECT questions_json FROM quizzes")
    quizzes = cursor.fetchall()
    total_questions = sum(len(json.loads(q[0])) for q in quizzes)
    conn.close()

    return {
        "totalQuizzes": total_quizzes,
        "totalQuestions": total_questions,
        "totalAttempts": total_attempts,
        "passRate": pass_rate
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

    async def broadcast(self, session_id: str, message: dict):
        if session_id in self.active_connections:
            for connection in self.active_connections[session_id]:
                await connection.send_json(message)

manager = ConnectionManager()

@app.websocket("/ws/exam/{session_id}")
async def exam_websocket_endpoint(websocket: WebSocket, session_id: str):
    await manager.connect(session_id, websocket)
    try:
        while True:
            data = await websocket.receive_json()
            event_type = data.get("type")
            if event_type == "HEARTBEAT":
                await websocket.send_json({"type": "PONG", "timestamp": datetime.datetime.now().isoformat()})
            elif event_type == "VIOLATION":
                # Log anti-cheat violation
                await websocket.send_json({"type": "VIOLATION_ACK", "count": data.get("count", 1)})
    except WebSocketDisconnect:
        manager.disconnect(session_id, websocket)


# Mount static assets for web/mobile client
app.mount("/assets", StaticFiles(directory="assets"), name="assets")
app.mount("/", StaticFiles(directory=".", html=True), name="static")

if __name__ == "__main__":
    import uvicorn
    print("Starting Online Quiz System Server on http://localhost:8000 ...")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
