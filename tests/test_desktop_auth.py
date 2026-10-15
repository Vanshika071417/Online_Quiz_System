import pytest
from desktop_app import DatabaseManager

def test_database_user_authentication():
    db = DatabaseManager()

    # 1. Authenticate default student
    student = db.authenticate_user("student", "student123")
    assert student is not None
    assert student["username"] == "student"
    assert student["role"] == "student"
    assert "full_name" in student

    # 2. Authenticate default faculty
    faculty = db.authenticate_user("faculty", "faculty123")
    assert faculty is not None
    assert faculty["role"] == "faculty"

    # 3. Authenticate default admin
    admin = db.authenticate_user("admin", "admin123")
    assert admin is not None
    assert admin["role"] == "admin"

    # 4. Failed authentication
    assert db.authenticate_user("student", "wrongpass") is None
    assert db.authenticate_user("nonexistent_user", "any") is None

def test_database_user_registration():
    db = DatabaseManager()
    import time

    test_username = f"testuser_{int(time.time() * 1000)}"
    
    # 1. Successful registration
    ok, user = db.register_user(
        username=test_username,
        password="securepassword123",
        role="student",
        full_name="Samantha Ray",
        department="Information Science"
    )
    assert ok is True
    assert user["username"] == test_username
    assert user["full_name"] == "Samantha Ray"
    assert user["role"] == "student"

    # 2. Authenticate the newly registered user
    auth_user = db.authenticate_user(test_username, "securepassword123")
    assert auth_user is not None
    assert auth_user["full_name"] == "Samantha Ray"

    # 3. Duplicate username rejection
    ok_dup, err_dup = db.register_user(
        username=test_username,
        password="anotherpassword",
        role="student",
        full_name="Duplicate Name"
    )
    assert ok_dup is False
    assert "already exists" in err_dup

    # 4. Short password validation
    ok_short, err_short = db.register_user(
        username=f"short_{int(time.time())}",
        password="12",
        role="student",
        full_name="Short Pass"
    )
    assert ok_short is False
    assert "at least 4 characters" in err_short
