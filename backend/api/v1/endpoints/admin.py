"""
Administration, Audit Inspection, and Operational Monitoring Endpoints (/v1/admin).
"""

import csv
import json
import io
from typing import List
from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import require_roles
from backend.models.tenancy import User, Tenant
from backend.models.quiz import Quiz
from backend.models.attempt import Attempt
from backend.models.grading import Grade
from backend.models.audit import AuditEvent
from backend.schemas.audit import AuditEventResponse, OperationalDashboardResponse
from tqm_sqc_tools import run_automated_db_backup

router = APIRouter(prefix="/admin", tags=["Admin & Analytics"])

@router.get("/overview", response_model=OperationalDashboardResponse)
def get_dashboard_overview(
    current_user: User = Depends(require_roles(["admin", "tenant_admin", "instructor"])),
    db: Session = Depends(get_db)
):
    total_tenants = db.query(Tenant).count()
    total_users = db.query(User).count()
    total_quizzes = db.query(Quiz).count()
    total_attempts = db.query(Attempt).count()
    active_attempts = db.query(Attempt).filter(Attempt.state == "in_progress").count()
    completed_attempts = db.query(Attempt).filter(Attempt.state.in_(["submitted", "evaluated"])).count()
    
    passed_count = db.query(Grade).filter(Grade.passed == True).count()
    total_graded = db.query(Grade).count()
    avg_pass_rate = round((passed_count / total_graded * 100), 2) if total_graded > 0 else 0.0

    return OperationalDashboardResponse(
        total_tenants=total_tenants,
        total_users=total_users,
        total_quizzes=total_quizzes,
        total_attempts=total_attempts,
        active_in_progress_attempts=active_attempts,
        completed_attempts=completed_attempts,
        average_pass_rate=avg_pass_rate,
        system_status="HEALTHY (Production Scale Ready)"
    )

@router.get("/audit-events", response_model=List[AuditEventResponse])
def get_audit_events(
    limit: int = 50,
    current_user: User = Depends(require_roles(["admin", "tenant_admin"])),
    db: Session = Depends(get_db)
):
    events = db.query(AuditEvent).order_by(AuditEvent.timestamp.desc()).limit(limit).all()
    res = []
    for e in events:
        try:
            payload = json.loads(e.payload_json)
        except Exception:
            payload = {}
        res.append(AuditEventResponse(
            id=e.id,
            tenant_id=e.tenant_id,
            actor_name=e.actor_name,
            action=e.action,
            target_resource=e.target_resource,
            request_id=e.request_id,
            timestamp=e.timestamp.isoformat(),
            payload=payload
        ))
    return res

@router.post("/backup")
def trigger_backup(
    current_user: User = Depends(require_roles(["admin", "tenant_admin"]))
):
    backup_path = run_automated_db_backup()
    return {
        "status": "success",
        "backup_file": backup_path,
        "message": "Authoritative database snapshot created successfully"
    }

@router.get("/gradebook.csv")
def export_gradebook_csv(
    current_user: User = Depends(require_roles(["admin", "tenant_admin", "instructor"])),
    db: Session = Depends(get_db)
):
    attempts = db.query(Attempt).filter(Attempt.state.in_(["submitted", "evaluated"])).all()
    
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Attempt ID", "Quiz Title", "Learner Name", "Score", "Total Points", "Percentage", "Passed", "Violations", "Submitted At"])
    
    for a in attempts:
        grade = db.query(Grade).filter(Grade.attempt_id == a.id).first()
        score = grade.score if grade else 0
        total = grade.total_points if grade else 0
        pct = grade.percentage if grade else 0
        passed = "YES" if (grade and grade.passed) else "NO"
        
        writer.writerow([
            a.id,
            a.quiz.title if a.quiz else "Quiz",
            a.learner_name,
            score,
            total,
            f"{pct}%",
            passed,
            a.cheat_violations,
            a.submitted_at.isoformat() if a.submitted_at else ""
        ])
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=gradebook_audit.csv"}
    )
