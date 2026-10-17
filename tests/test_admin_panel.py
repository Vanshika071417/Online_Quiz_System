import pytest
from fastapi.testclient import TestClient
from server import app
from desktop_app import DatabaseManager

client = TestClient(app)

def test_admin_users_endpoint():
    response = client.get("/api/admin/users")
    assert response.status_code == 200
    users = response.json()
    assert isinstance(users, list)
    assert len(users) >= 3
    # Check fields of user record
    first_user = users[0]
    assert "userNo" in first_user
    assert "id" in first_user
    assert "username" in first_user
    assert "role" in first_user
    assert "totalAttempts" in first_user
    assert "avgScore" in first_user
    assert "passRate" in first_user
    assert "totalViolations" in first_user

def test_admin_user_report_endpoint():
    users_resp = client.get("/api/admin/users")
    users = users_resp.json()
    student_user = next((u for u in users if u["role"] == "student"), users[0])
    
    report_resp = client.get(f"/api/admin/users/{student_user['id']}/report")
    assert report_resp.status_code == 200
    report = report_resp.json()
    assert "user" in report
    assert "summary" in report
    assert "attempts" in report
    assert report["user"]["id"] == student_user["id"]
    assert "passRate" in report["summary"]
    assert "avgScore" in report["summary"]
    assert isinstance(report["attempts"], list)

def test_admin_analytics_endpoint():
    response = client.get("/api/admin/analytics")
    assert response.status_code == 200
    data = response.json()
    assert "kpis" in data
    assert "quizzesAnalytics" in data
    assert "recentSubmissions" in data
    
    kpis = data["kpis"]
    assert "totalUsers" in kpis
    assert "totalQuizzes" in kpis
    assert "totalAttempts" in kpis
    assert "overallPassRate" in kpis
    assert "platformAvgScore" in kpis

    quizzes = data["quizzesAnalytics"]
    assert len(quizzes) >= 1
    first_q = quizzes[0]
    assert "joinCode" in first_q
    assert "difficultyRating" in first_q
    assert "attemptsCount" in first_q

def test_admin_csv_exports():
    res_users = client.get("/api/admin/export/users.csv")
    assert res_users.status_code == 200
    assert "text/csv" in res_users.headers.get("content-type", "")
    assert "User No,User ID,Full Name,Username" in res_users.text

    res_subs = client.get("/api/admin/export/submissions.csv")
    assert res_subs.status_code == 200
    assert "text/csv" in res_subs.headers.get("content-type", "")
    assert "Attempt ID,Candidate Name,Quiz Title,Join Code" in res_subs.text

def test_desktop_database_admin_methods():
    db = DatabaseManager()
    users = db.get_admin_users_with_stats()
    assert isinstance(users, list)
    assert len(users) >= 3
    assert users[0]["user_no"] == 1

    analytics = db.get_admin_quiz_analytics()
    assert "kpis" in analytics
    assert "quizzes" in analytics

    user_id = users[0]["id"]
    report = db.get_admin_user_report(user_id)
    assert report is not None
    assert report["user"]["id"] == user_id
