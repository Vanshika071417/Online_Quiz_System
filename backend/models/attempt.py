"""
Timed Attempts and Durable Answer Domain Models.
Guarantees server-authoritative deadlines, monotonic answer revisions, and idempotent writes.
"""

import uuid
import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, UniqueConstraint, Index
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Attempt(Base):
    """Authoritative attempt lifecycle record."""
    __tablename__ = "attempts_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"att-{uuid.uuid4().hex[:12]}")
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    quiz_id = Column(String(64), ForeignKey("quizzes_v2.id"), nullable=False, index=True)
    quiz_version_id = Column(String(64), ForeignKey("quiz_versions.id"), nullable=False, index=True)
    learner_id = Column(String(64), ForeignKey("platform_users.id"), nullable=False, index=True)
    learner_name = Column(String(255), nullable=False)
    
    # Lifecycle: in_progress, submitted, timed_out, evaluated
    state = Column(String(30), default="in_progress", index=True, nullable=False)
    
    # Server Authoritative Time
    started_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)
    deadline_at = Column(DateTime, nullable=False) # Server calculated from quiz duration + learner accommodation
    submitted_at = Column(DateTime, nullable=True)
    
    # Deterministic form seed for item / option shuffling
    form_seed = Column(Integer, default=lambda: uuid.uuid4().int % 100000)
    cheat_violations = Column(Integer, default=0)
    idempotency_key = Column(String(128), unique=True, nullable=True, index=True)
    
    quiz = relationship("Quiz", back_populates="attempts")
    quiz_version = relationship("QuizVersion", back_populates="attempts")
    learner = relationship("User", back_populates="attempts")
    answers = relationship("AttemptAnswer", back_populates="attempt", cascade="all, delete-orphan")
    grade = relationship("Grade", back_populates="attempt", uselist=False, cascade="all, delete-orphan")

class AttemptAnswer(Base):
    """
    Durable individual item response.
    Uses monotonic revisions to guarantee that concurrent tabs do not overwrite newer answers.
    """
    __tablename__ = "attempt_answers_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"ans-{uuid.uuid4().hex[:12]}")
    attempt_id = Column(String(64), ForeignKey("attempts_v2.id"), nullable=False, index=True)
    item_id = Column(String(64), nullable=False, index=True)
    answer_payload_json = Column(Text, nullable=False) # E.g. {"selectedOption": 1}
    revision = Column(Integer, default=1, nullable=False) # Monotonic revision counter
    idempotency_key = Column(String(128), nullable=True)
    saved_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), nullable=False)

    __table_args__ = (
        UniqueConstraint('attempt_id', 'item_id', name='uq_attempt_item'),
    )

    attempt = relationship("Attempt", back_populates="answers")
