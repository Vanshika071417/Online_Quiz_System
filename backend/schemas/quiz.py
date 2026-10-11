"""
Pydantic v2 Schemas for Quiz Authoring and Catalog.
Enforces allowlisted learner-safe shapes to prevent answer key leakage.
"""

from typing import List, Optional, Any
from pydantic import BaseModel, Field

class QuestionItemSchema(BaseModel):
    id: str
    text: str
    code: Optional[str] = None
    options: List[str]
    correct: int # 0-indexed choice
    points: float = 1.0
    explanation: Optional[str] = ""
    question_type: str = "single_choice" # single_choice, multiple_choice, true_false, ordering

class LearnerQuestionItemSchema(BaseModel):
    """Allowlisted schema delivered to candidates during active assessment."""
    id: str
    text: str
    code: Optional[str] = None
    options: List[str]
    points: float = 1.0
    question_type: str = "single_choice"

class QuizCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    category: str = "General"
    description: Optional[str] = ""
    duration_minutes: int = Field(default=15, ge=1, le=360)
    passing_score: int = Field(default=70, ge=1, le=100)
    join_code: Optional[str] = None
    questions: List[QuestionItemSchema]

class QuizResponse(BaseModel):
    id: str
    title: str
    category: str
    description: Optional[str]
    join_code: str
    teacher_name: str
    duration_minutes: int
    passing_score: int
    status: str
    questions_count: int
    current_version_id: Optional[str]
    created_at: str

class QuizVersionResponse(BaseModel):
    id: str
    quiz_id: str
    version_number: int
    questions_count: int
    published_at: str
