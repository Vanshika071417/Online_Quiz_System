"""
Pydantic v2 Schemas for Grading, Results, and Appeals.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class ItemResultBreakdown(BaseModel):
    item_id: str
    question_text: str
    student_selected_option: Optional[int]
    correct_option: int
    is_correct: bool
    points_earned: float
    max_points: float
    explanation: Optional[str] = ""

class ResultResponse(BaseModel):
    attempt_id: str
    quiz_title: str
    learner_name: str
    score: float
    total_points: float
    percentage: float
    passed: bool
    cheat_violations: int
    status: str # released, provisional
    submitted_at: Optional[str]
    breakdown: Optional[List[ItemResultBreakdown]] = None

class ManualGradeRequest(BaseModel):
    item_scores: Dict[str, float]
    reviewer_notes: Optional[str] = None
    override_passed: Optional[bool] = None

class AppealCreateRequest(BaseModel):
    reason: str

class AppealResponse(BaseModel):
    id: str
    grade_id: str
    status: str
    reason: str
    created_at: str
