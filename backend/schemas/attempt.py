"""
Pydantic v2 Schemas for Timed Attempts, Autosave, and Submissions.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from backend.schemas.quiz import LearnerQuestionItemSchema

class AttemptStartRequest(BaseModel):
    idempotency_key: Optional[str] = None

class SavedAnswerItem(BaseModel):
    item_id: str
    selected_option: Optional[int]
    revision: int
    saved_at: str

class LearnerFormResponse(BaseModel):
    attempt_id: str
    quiz_id: str
    quiz_version_id: str
    quiz_title: str
    state: str
    started_at: str
    deadline_at: str
    server_now: str
    remaining_seconds: int
    form_seed: int
    questions: List[LearnerQuestionItemSchema]
    saved_answers: Dict[str, Any]

class AnswerUpsertRequest(BaseModel):
    selected_option: int = Field(..., ge=0, le=10)
    revision: int = Field(default=1, ge=1, description="Client monotonic revision to prevent stale overwrites")
    idempotency_key: Optional[str] = None

class AnswerUpsertResponse(BaseModel):
    success: bool
    item_id: str
    accepted_revision: int
    saved_at: str

class SubmitAttemptRequest(BaseModel):
    cheat_violations: int = 0

class SubmitAttemptResponse(BaseModel):
    attempt_id: str
    state: str
    submitted_at: str
    message: str
