"""
Database Bootstrap and Initial Seeding Service.
Creates tables and seeds root tenant, role accounts, and baseline published quiz snapshots.
"""

import json
from sqlalchemy.orm import Session
from backend.core.database import engine, Base, SessionLocal
from backend.core.config import settings
from backend.core.security import hash_password
from backend.models.tenancy import Tenant, User
from backend.models.quiz import Quiz, QuizVersion

def init_and_seed_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        # 1. Seed Default Tenant
        tenant = db.query(Tenant).filter(Tenant.id == settings.DEFAULT_TENANT_ID).first()
        if not tenant:
            tenant = Tenant(
                id=settings.DEFAULT_TENANT_ID,
                name=settings.DEFAULT_TENANT_NAME,
                domain="assessment.enterprise.org"
            )
            db.add(tenant)
            db.flush()

        # 2. Seed Default Accounts
        default_accounts = [
            ("usr-admin", "admin", "admin123", "tenant_admin", "System Administrator", "Operations & QA", 0),
            ("usr-faculty", "faculty", "faculty123", "instructor", "Prof. Alan Turing", "Computer Science", 0),
            ("usr-student", "student", "student123", "learner", "Alex Mercer", "B.Tech CSE", 0),
            ("usr-student-acc", "student_acc", "student123", "learner", "Morgan Reed (Extra Time)", "B.Tech CSE", 50)
        ]

        for uid, uname, pwd, role, fname, dept, acc_time in default_accounts:
            existing_user = db.query(User).filter(User.username == uname).first()
            if not existing_user:
                db.add(User(
                    id=uid,
                    tenant_id=tenant.id,
                    username=uname,
                    hashed_password=hash_password(pwd),
                    full_name=fname,
                    role=role,
                    department=dept,
                    accommodations_extra_time_percent=acc_time
                ))
        db.flush()

        # 3. Seed Baseline Published Quiz with Version 1 Immutable Snapshot
        baseline_quiz = db.query(Quiz).filter(Quiz.join_code == "QZ-1001").first()
        if not baseline_quiz:
            quiz = Quiz(
                id="qz-baseline-1001",
                tenant_id=tenant.id,
                title="TQM Principles & Statistical Quality Control",
                category="Industrial Engineering",
                description="Comprehensive evaluation covering Ishikawa diagrams, Pareto 80/20 analysis, and Poka-Yoke error proofing.",
                join_code="QZ-1001",
                teacher_name="Prof. Alan Turing",
                duration_minutes=15,
                passing_score=70,
                status="published"
            )
            db.add(quiz)
            db.flush()

            sample_questions = [
                {
                    "id": "q1",
                    "text": "In Statistical Quality Control, which principle identifies that roughly 80% of process defects arise from 20% of root causes?",
                    "code": None,
                    "options": [
                        "Pareto Principle (80/20 Rule)",
                        "Central Limit Theorem",
                        "Normal Gaussian Curve",
                        "Taguchi Loss Function"
                    ],
                    "correct": 0,
                    "points": 1.0,
                    "explanation": "Vilfredo Pareto's principle isolates the vital few causes from the trivial many."
                },
                {
                    "id": "q2",
                    "text": "What is the primary role of a Poka-Yoke mechanism in modern software engineering?",
                    "code": "def process_submission(attempt):\n    assert attempt.is_valid(), 'Infallible precondition'",
                    "options": [
                        "Inadvertent error prevention and fail-safe design",
                        "Benchmarking maximum thread throughput",
                        "Executing scheduled data migrations",
                        "Generating random test datasets"
                    ],
                    "correct": 0,
                    "points": 1.0,
                    "explanation": "Poka-Yoke (mistake-proofing) guarantees that operations fail safely before causing system harm."
                },
                {
                    "id": "q3",
                    "text": "In the Ishikawa (Cause-and-Effect) diagram, which of the following is NOT one of the classic 4M manufacturing categories?",
                    "code": None,
                    "options": [
                        "Monopoly",
                        "Manpower (People)",
                        "Machine (Equipment)",
                        "Method (Process)"
                    ],
                    "correct": 0,
                    "points": 1.0,
                    "explanation": "The traditional categories are Manpower, Machine, Method, Material, Measurement, and Milieu."
                },
                {
                    "id": "q4",
                    "text": "Which phase of the Deming PDCA Cycle represents verifying empirical results against quality benchmarks?",
                    "code": None,
                    "options": [
                        "Check (Study)",
                        "Plan",
                        "Do",
                        "Act"
                    ],
                    "correct": 0,
                    "points": 1.0,
                    "explanation": "Check/Study compares observed metrics with the original target to evaluate effectiveness."
                }
            ]

            qv = QuizVersion(
                id="qv-baseline-1001-v1",
                quiz_id=quiz.id,
                version_number=1,
                snapshot_json=json.dumps(sample_questions),
                published_by_id="usr-faculty"
            )
            db.add(qv)
            db.flush()

            quiz.current_version_id = qv.id

        db.commit()
    finally:
        db.close()
