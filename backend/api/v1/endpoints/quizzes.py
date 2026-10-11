"""
Quiz Authoring and Catalog Endpoints (/v1/quizzes).
"""

import json
from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user, require_roles
from backend.models.tenancy import User
from backend.models.quiz import Quiz, QuizVersion
from backend.schemas.quiz import QuizCreateRequest, QuizResponse, QuizVersionResponse, QuestionItemSchema
from backend.services.quiz_service import QuizService

router = APIRouter(prefix="/quizzes", tags=["Quiz Authoring & Catalog"])

@router.get("", response_model=List[QuizResponse])
def list_quizzes(db: Session = Depends(get_db)):
    """Public / Learner Catalog: Lists all available published quizzes."""
    quizzes = db.query(Quiz).filter(Quiz.status == "published").all()
    res = []
    for q in quizzes:
        count = 0
        if q.current_version_id:
            qv = db.query(QuizVersion).filter(QuizVersion.id == q.current_version_id).first()
            if qv:
                count = len(json.loads(qv.snapshot_json))
        res.append(QuizResponse(
            id=q.id,
            title=q.title,
            category=q.category or "General",
            description=q.description or "",
            join_code=q.join_code,
            teacher_name=q.teacher_name,
            duration_minutes=q.duration_minutes,
            passing_score=q.passing_score,
            status=q.status,
            questions_count=count,
            current_version_id=q.current_version_id,
            created_at=q.created_at.isoformat()
        ))
    return res

@router.post("", response_model=QuizResponse)
def create_quiz(
    req: QuizCreateRequest,
    current_user: User = Depends(require_roles(["instructor", "admin", "tenant_admin"])),
    db: Session = Depends(get_db)
):
    """Instructor/Author Endpoint: Creates a quiz and publishes initial Version 1 snapshot."""
    quiz = QuizService.create_quiz(
        db=db,
        tenant_id=current_user.tenant_id,
        author_id=current_user.id,
        author_name=current_user.full_name,
        req=req
    )
    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        category=quiz.category,
        description=quiz.description,
        join_code=quiz.join_code,
        teacher_name=quiz.teacher_name,
        duration_minutes=quiz.duration_minutes,
        passing_score=quiz.passing_score,
        status=quiz.status,
        questions_count=len(req.questions),
        current_version_id=quiz.current_version_id,
        created_at=quiz.created_at.isoformat()
    )

@router.get("/{quiz_id}", response_model=QuizResponse)
def get_quiz(quiz_id: str, db: Session = Depends(get_db)):
    quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz not found")
    count = 0
    if quiz.current_version_id:
        qv = db.query(QuizVersion).filter(QuizVersion.id == quiz.current_version_id).first()
        if qv:
            count = len(json.loads(qv.snapshot_json))
    return QuizResponse(
        id=quiz.id,
        title=quiz.title,
        category=quiz.category,
        description=quiz.description,
        join_code=quiz.join_code,
        teacher_name=quiz.teacher_name,
        duration_minutes=quiz.duration_minutes,
        passing_score=quiz.passing_score,
        status=quiz.status,
        questions_count=count,
        current_version_id=quiz.current_version_id,
        created_at=quiz.created_at.isoformat()
    )

@router.post("/{quiz_id}/publish", response_model=QuizVersionResponse)
def publish_version(
    quiz_id: str,
    questions: List[QuestionItemSchema],
    current_user: User = Depends(require_roles(["instructor", "admin", "tenant_admin"])),
    db: Session = Depends(get_db)
):
    """Publishes a new immutable QuizVersion snapshot for active and future attempts."""
    qv = QuizService.publish_new_version(
        db=db,
        quiz_id=quiz_id,
        author_id=current_user.id,
        author_name=current_user.full_name,
        questions=questions
    )
    return QuizVersionResponse(
        id=qv.id,
        quiz_id=qv.quiz_id,
        version_number=qv.version_number,
        questions_count=len(questions),
        published_at=qv.published_at.isoformat()
    )
