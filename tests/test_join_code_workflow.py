import pytest
from fastapi.testclient import TestClient
from server import app, init_db

client = TestClient(app)

def setup_module(module):
    init_db()

def test_join_code_teacher_student_workflow():
    # 1. Teacher creates quiz with specific join code
    quiz_payload = {
        "id": "quiz-quantum-test",
        "title": "Quantum Computing Fundamentals",
        "category": "Physics",
        "description": "Introductory quiz on quantum gates and qubits.",
        "durationMinutes": 15,
        "passingScore": 70,
        "joinCode": "QZ-7777",
        "teacherName": "Prof. Erwin Schrodinger",
        "tags": ["Physics", "Quantum"],
        "questions": [
            {
                "id": "q-101",
                "text": "What is the quantum counterpart of a classical bit?",
                "options": ["Qubit", "Byte", "Trit", "Packet"],
                "correct": 0,
                "explanation": "A qubit represents a two-state quantum system."
            }
        ]
    }
    create_res = client.post("/api/quizzes", json=quiz_payload)
    assert create_res.status_code == 200
    created_data = create_res.json()
    quiz_id = created_data["id"]
    assert created_data["joinCode"] == "QZ-7777"

    # 2. Student joins quiz using join code
    code_res = client.get("/api/quizzes/code/QZ-7777")
    assert code_res.status_code == 200
    found_quiz = code_res.json()
    assert found_quiz["id"] == quiz_id
    assert found_quiz["title"] == "Quantum Computing Fundamentals"
    assert found_quiz["joinCode"] == "QZ-7777"

    # 3. Student submits test attempt
    submit_payload = {
        "studentName": "Jane Doe",
        "answers": {
            "q-101": 0
        },
        "cheatViolations": 0
    }
    submit_res = client.post(f"/api/quizzes/{quiz_id}/submit", json=submit_payload)
    assert submit_res.status_code == 200
    sub_data = submit_res.json()
    assert sub_data["score"] == 1
    assert sub_data["totalQuestions"] == 1
    assert sub_data["percentage"] == 100
    assert sub_data["passed"] is True

    # 4. Teacher retrieves class reports and verifies student is in roster
    reports_res = client.get("/api/teacher/reports?teacher=Prof.+Erwin+Schrodinger")
    assert reports_res.status_code == 200
    reports = reports_res.json()
    assert isinstance(reports, list)

    student_records = [r for r in reports if r["studentName"] == "Jane Doe" and r["joinCode"] == "QZ-7777"]
    assert len(student_records) >= 1
    record = student_records[0]
    assert record["quizTitle"] == "Quantum Computing Fundamentals"
    assert record["score"] == 1
    assert record["percentage"] == 100
    assert record["passed"] is True
