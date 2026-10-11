"""
Grading Results and Appeals Endpoints (/v1/results & /v1/submissions).
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import get_current_user
from backend.models.tenancy import User
from backend.schemas.grading import ResultResponse, AppealCreateRequest, AppealResponse
from backend.services.grading_service import GradingService

router = APIRouter(tags=["Results, Grading & Appeals"])

@router.get("/results/{attempt_id}", response_model=ResultResponse)
def get_assessment_result(
    attempt_id: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    GET /v1/results/{id}
    Returns score, passing status, and detailed explanations strictly under visibility policy.
    """
    is_faculty = current_user.role in ["instructor", "admin", "tenant_admin"]
    return GradingService.get_result(
        db=db,
        attempt_id=attempt_id,
        requester_id=current_user.id,
        is_instructor=is_faculty
    )

@router.post("/submissions/{attempt_id}/appeal", response_model=AppealResponse)
def appeal_grade(
    attempt_id: str,
    req: AppealCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    POST /v1/submissions/{id}/appeal
    Enables candidates to request instructor moderation/appeal for evaluations.
    """
    appeal = GradingService.submit_appeal(
        db=db,
        attempt_id=attempt_id,
        learner_id=current_user.id,
        reason=req.reason
    )
    return AppealResponse(
        id=appeal.id,
        grade_id=appeal.grade_id,
        status=appeal.status,
        reason=appeal.reason,
        created_at=appeal.created_at.isoformat()
    )
