"""
Attempt Lifecycle Endpoints (/v1/quizzes/.../attempts & /v1/attempts/...).
Enforces server-authoritative deadlines, monotonic answer revisions, and idempotent finalization.
"""

from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.tenancy import User
from backend.schemas.attempt import (
    AttemptStartRequest,
    LearnerFormResponse,
    AnswerUpsertRequest,
    AnswerUpsertResponse,
    SubmitAttemptRequest,
    SubmitAttemptResponse
)
from backend.services.attempt_service import AttemptService

router = APIRouter(tags=["Timed Attempts & Autosave"])

@router.post("/quizzes/{quiz_id}/attempts", response_model=LearnerFormResponse)
def start_or_resume_quiz_attempt(
    quiz_id: str,
    req: Optional[AttemptStartRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /v1/quizzes/{id}/attempts
    Checks eligibility, applies accommodations, calculates server deadline,
    and returns learner-safe form (stripping answer keys).
    """
    idempotency_key = req.idempotency_key if req else None
    return AttemptService.start_or_resume_attempt(
        db=db,
        quiz_id=quiz_id,
        learner=current_user,
        idempotency_key=idempotency_key
    )

@router.get("/attempts/{attempt_id}", response_model=LearnerFormResponse)
def get_attempt(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /v1/attempts/{id}
    Authorized resume with server deadline and accepted answer revisions.
    """
    return AttemptService.get_attempt_for_resume(
        db=db,
        attempt_id=attempt_id,
        learner_id=current_user.id
    )

@router.put("/attempts/{attempt_id}/answers/{item_id}", response_model=AnswerUpsertResponse)
def upsert_answer(
    attempt_id: str,
    item_id: str,
    req: AnswerUpsertRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    PUT /v1/attempts/{id}/answers/{item_id}
    Enforces ownership, active in_progress state, server deadline,
    and monotonic revision guard against stale concurrent tab writes.
    """
    res = AttemptService.upsert_answer(
        db=db,
        attempt_id=attempt_id,
        item_id=item_id,
        selected_option=req.selected_option,
        revision=req.revision,
        learner_id=current_user.id,
        idempotency_key=req.idempotency_key
    )
    return AnswerUpsertResponse(**res)

@router.post("/attempts/{attempt_id}/submit", response_model=SubmitAttemptResponse)
def submit_attempt(
    attempt_id: str,
    req: Optional[SubmitAttemptRequest] = None,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /v1/attempts/{id}/submit
    Idempotent finalization: freezes boundary, writes outbox event, and evaluates submission.
    """
    violations = req.cheat_violations if req else 0
    attempt = AttemptService.submit_attempt(
        db=db,
        attempt_id=attempt_id,
        learner_id=current_user.id,
        cheat_violations=violations
    )
    return SubmitAttemptResponse(
        attempt_id=attempt.id,
        state=attempt.state,
        submitted_at=attempt.submitted_at.isoformat() if attempt.submitted_at else "",
        message="Assessment finalized and evaluated successfully"
    )
