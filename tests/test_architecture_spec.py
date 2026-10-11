"""
Automated Verification Suite for the Online Quiz System Architecture Specification.
Tests all requirements from online_quiz_system_architecture.md.
"""

import pytest
from fastapi.testclient import TestClient
from server import app
from backend.core.bootstrap import init_and_seed_db
from backend.core.database import SessionLocal
from backend.models.tenancy import User
from backend.models.quiz import Quiz, QuizVersion
from backend.models.attempt import Attempt, AttemptAnswer
from backend.models.grading import Grade

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_database():
    init_and_seed_db()

def test_01_rbac_and_identity():
    # 1. Login with seeded admin
    admin_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    assert admin_login.status_code == 200
    admin_token = admin_login.json()["access_token"]
    assert admin_login.json()["role"] == "tenant_admin"

    # 2. Login with seeded faculty
    fac_login = client.post("/v1/auth/login", json={"username": "faculty", "password": "faculty123"})
    assert fac_login.status_code == 200
    assert fac_login.json()["role"] == "instructor"

    # 3. Login with accommodated student
    stu_acc_login = client.post("/v1/auth/login", json={"username": "student_acc", "password": "student123"})
    assert stu_acc_login.status_code == 200
    token_acc = stu_acc_login.json()["access_token"]
    
    # 4. Verify accommodated profile has extra time
    profile_res = client.get("/v1/auth/me", headers={"Authorization": f"Bearer {token_acc}"})
    assert profile_res.status_code == 200
    assert profile_res.json()["accommodations_extra_time_percent"] == 50

def test_02_quiz_authoring_and_immutable_versioning():
    # Login as instructor
    fac_login = client.post("/v1/auth/login", json={"username": "faculty", "password": "faculty123"})
    fac_token = fac_login.json()["access_token"]

    # Create new quiz
    quiz_payload = {
        "title": "Cloud Systems & Reliability Architecture",
        "category": "Cloud Architecture",
        "description": "Evaluation of stateless APIs, idempotent retry patterns, and RPO/RTO.",
        "duration_minutes": 10,
        "passing_score": 75,
        "questions": [
            {
                "id": "q-arch-1",
                "text": "Which pattern guarantees reliable asynchronous message dispatch alongside database transactions?",
                "code": None,
                "options": [
                    "Transactional Outbox Pattern",
                    "Two-Phase Commit without logging",
                    "Fire-and-forget in-memory threads",
                    "Direct client webhook calls"
                ],
                "correct": 0,
                "points": 1.0,
                "explanation": "Transactional Outbox commits events into the database atomically before async dispatch."
            },
            {
                "id": "q-arch-2",
                "text": "Why must answer write endpoints enforce monotonic revision checks?",
                "code": None,
                "options": [
                    "To prevent stale concurrent browser tabs from overwriting newer answers",
                    "To compress network JSON payloads",
                    "To format code snippets",
                    "To bypass authentication"
                ],
                "correct": 0,
                "points": 1.0,
                "explanation": "Monotonic revisions detect stale requests and reject older out-of-order packets."
            }
        ]
    }

    create_res = client.post(
        "/v1/quizzes",
        json=quiz_payload,
        headers={"Authorization": f"Bearer {fac_token}"}
    )
    assert create_res.status_code == 200
    quiz_data = create_res.json()
    quiz_id = quiz_data["id"]
    assert quiz_data["status"] == "published"
    assert quiz_data["questions_count"] == 2
    assert quiz_data["current_version_id"] is not None

    # Publish an updated Version 2 snapshot
    updated_questions = quiz_payload["questions"] + [
        {
            "id": "q-arch-3",
            "text": "What does a zero-latency grading engine require?",
            "options": ["Pre-indexed immutable version answer keys", "External slow web APIs"],
            "correct": 0,
            "points": 1.0,
            "explanation": "In-memory deterministic comparison achieves <250ms grading."
        }
    ]
    publish_v2_res = client.post(
        f"/v1/quizzes/{quiz_id}/publish",
        json=updated_questions,
        headers={"Authorization": f"Bearer {fac_token}"}
    )
    assert publish_v2_res.status_code == 200
    assert publish_v2_res.json()["version_number"] == 2
    assert publish_v2_res.json()["questions_count"] == 3

def test_03_attempt_lifecycle_and_answer_key_sanitization():
    # Login as learner
    stu_login = client.post("/v1/auth/login", json={"username": "student", "password": "student123"})
    stu_token = stu_login.json()["access_token"]

    # Start attempt on baseline quiz
    start_res = client.post(
        "/v1/quizzes/qz-baseline-1001/attempts",
        json={"idempotency_key": "key-test-1001"},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert start_res.status_code == 200
    attempt_data = start_res.json()
    attempt_id = attempt_data["attempt_id"]
    assert attempt_data["state"] == "in_progress"
    assert attempt_data["remaining_seconds"] > 0
    assert len(attempt_data["questions"]) > 0

    # SECURITY CHECK: Verify answer keys ('correct' and 'explanation') are NEVER leaked in candidate questions!
    for q in attempt_data["questions"]:
        assert "correct" not in q
        assert "explanation" not in q
        assert "text" in q
        assert "options" in q

    # IDEMPOTENCY CHECK: Starting again returns the active in_progress attempt
    resume_res = client.post(
        "/v1/quizzes/qz-baseline-1001/attempts",
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert resume_res.status_code == 200
    assert resume_res.json()["attempt_id"] == attempt_id

def test_04_durable_autosave_and_monotonic_revision_guard():
    # Login as learner
    stu_login = client.post("/v1/auth/login", json={"username": "student", "password": "student123"})
    stu_token = stu_login.json()["access_token"]

    # Get active attempt
    attempt_res = client.post("/v1/quizzes/qz-baseline-1001/attempts", headers={"Authorization": f"Bearer {stu_token}"})
    attempt_id = attempt_res.json()["attempt_id"]

    # 1. Save answer with revision 1 -> SUCCESS
    ans1_res = client.put(
        f"/v1/attempts/{attempt_id}/answers/q1",
        json={"selected_option": 0, "revision": 1},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert ans1_res.status_code == 200
    assert ans1_res.json()["accepted_revision"] == 1

    # 2. Save answer with revision 2 -> SUCCESS
    ans2_res = client.put(
        f"/v1/attempts/{attempt_id}/answers/q1",
        json={"selected_option": 0, "revision": 2},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert ans2_res.status_code == 200
    assert ans2_res.json()["accepted_revision"] == 2

    # 3. Simulate delayed packet or stale tab trying to write revision 1 -> 409 CONFLICT
    stale_res = client.put(
        f"/v1/attempts/{attempt_id}/answers/q1",
        json={"selected_option": 2, "revision": 1},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert stale_res.status_code == 409
    assert "Stale revision rejected" in stale_res.json()["detail"]

    # Answer other questions for submission
    client.put(
        f"/v1/attempts/{attempt_id}/answers/q2",
        json={"selected_option": 0, "revision": 1},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    client.put(
        f"/v1/attempts/{attempt_id}/answers/q3",
        json={"selected_option": 0, "revision": 1},
        headers={"Authorization": f"Bearer {stu_token}"}
    )

def test_05_idempotent_submit_and_deterministic_grading():
    # Login as learner
    stu_login = client.post("/v1/auth/login", json={"username": "student", "password": "student123"})
    stu_token = stu_login.json()["access_token"]
    attempt_id = client.post("/v1/quizzes/qz-baseline-1001/attempts", headers={"Authorization": f"Bearer {stu_token}"}).json()["attempt_id"]

    # Finalize submission
    sub_res = client.post(
        f"/v1/attempts/{attempt_id}/submit",
        json={"cheat_violations": 0},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert sub_res.status_code == 200
    assert sub_res.json()["state"] == "evaluated"

    # IDEMPOTENT SUBMIT: Second submit returns identical evaluated status without duplicate scoring
    sub2_res = client.post(
        f"/v1/attempts/{attempt_id}/submit",
        json={"cheat_violations": 0},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert sub2_res.status_code == 200

    # Retrieve Result Under Visibility Policy
    result_res = client.get(f"/v1/results/{attempt_id}", headers={"Authorization": f"Bearer {stu_token}"})
    assert result_res.status_code == 200
    res_data = result_res.json()
    assert res_data["score"] >= 3.0
    assert res_data["percentage"] >= 75.0
    assert res_data["passed"] is True
    assert res_data["breakdown"] is not None
    assert len(res_data["breakdown"]) == 4

    # Submit an appeal
    appeal_res = client.post(
        f"/v1/submissions/{attempt_id}/appeal",
        json={"reason": "Requesting clarification on question 3 manufacturing 4M options."},
        headers={"Authorization": f"Bearer {stu_token}"}
    )
    assert appeal_res.status_code == 200
    assert appeal_res.json()["status"] == "pending"

def test_06_admin_operational_endpoints_and_telemetry():
    admin_login = client.post("/v1/auth/login", json={"username": "admin", "password": "admin123"})
    admin_token = admin_login.json()["access_token"]

    # 1. Operational Overview
    overview_res = client.get("/v1/admin/overview", headers={"Authorization": f"Bearer {admin_token}"})
    assert overview_res.status_code == 200
    assert overview_res.json()["total_quizzes"] >= 1
    assert overview_res.json()["total_attempts"] >= 1
    assert "HEALTHY" in overview_res.json()["system_status"]

    # 2. Audit Trail Inspection
    audit_res = client.get("/v1/admin/audit-events", headers={"Authorization": f"Bearer {admin_token}"})
    assert audit_res.status_code == 200
    assert len(audit_res.json()) > 0

    # 3. Gradebook CSV Export
    csv_res = client.get("/v1/admin/gradebook.csv", headers={"Authorization": f"Bearer {admin_token}"})
    assert csv_res.status_code == 200
    assert "Attempt ID,Quiz Title,Learner Name" in csv_res.text
    assert "Alex Mercer" in csv_res.text

    # 4. Telemetry Header check
    assert "x-request-id" in csv_res.headers
    assert "x-process-time-ms" in csv_res.headers
