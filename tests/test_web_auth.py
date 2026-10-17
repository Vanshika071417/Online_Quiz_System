import pytest
from fastapi.testclient import TestClient
from server import app

client = TestClient(app)

def test_web_auth_login_student():
    response = client.post("/api/auth/login", json={"username": "student", "password": "student123"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "student"
    assert data["role"] == "student"
    assert data["full_name"] == "Alex Mercer"

def test_web_auth_login_faculty():
    response = client.post("/api/auth/login", json={"username": "faculty", "password": "faculty123"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "faculty"
    assert data["role"] == "faculty"

def test_web_auth_login_admin():
    response = client.post("/api/auth/login", json={"username": "admin", "password": "admin123"})
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == "admin"
    assert data["role"] == "admin"

def test_web_auth_login_invalid_password():
    response = client.post("/api/auth/login", json={"username": "student", "password": "wrongpassword"})
    assert response.status_code == 401
    assert "Invalid credentials" in response.json()["detail"]

def test_web_auth_register_and_login():
    import uuid
    unique_user = f"newuser_{uuid.uuid4().hex[:6]}"
    reg_response = client.post("/api/auth/register", json={
        "username": unique_user,
        "password": "pass1234",
        "role": "student",
        "full_name": "Web Test Candidate",
        "department": "CSE AI & ML"
    })
    assert reg_response.status_code == 200
    user_data = reg_response.json()
    assert user_data["username"] == unique_user
    assert user_data["role"] == "student"

    # Login with newly created user
    login_res = client.post("/api/auth/login", json={
        "username": unique_user,
        "password": "pass1234"
    })
    assert login_res.status_code == 200
    assert login_res.json()["full_name"] == "Web Test Candidate"

def test_web_auth_register_duplicate():
    response = client.post("/api/auth/register", json={
        "username": "student",
        "password": "password123",
        "role": "student",
        "full_name": "Duplicate Student"
    })
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]

def test_api_get_current_user():
    # 1. GET with no params returns default user
    res_get = client.get("/api/get_current_user")
    assert res_get.status_code == 200
    assert "username" in res_get.json()

    # 2. POST with username
    res_post = client.post("/api/get_current_user", json={"username": "faculty"})
    assert res_post.status_code == 200
    data = res_post.json()
    assert data["username"] == "faculty"
    assert data["role"] == "faculty"

    # 3. GET favicon.ico returns 204
    res_fav = client.get("/favicon.ico")
    assert res_fav.status_code == 204

