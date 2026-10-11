"""
Grading, Rubrics, Results Release, and Grade Appeal Domain Models.
Separates score calculation from release visibility policy.
"""

import uuid
import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Grade(Base):
    __tablename__ = "grades_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"grd-{uuid.uuid4().hex[:12]}")
    attempt_id = Column(String(64), ForeignKey("attempts_v2.id"), unique=True, nullable=False, index=True)
    score = Column(Float, nullable=False, default=0.0)
    total_points = Column(Float, nullable=False, default=0.0)
    percentage = Column(Float, nullable=False, default=0.0)
    passed = Column(Boolean, nullable=False, default=False)
    grading_policy_version = Column(String(32), default="v1.0-deterministic")
    
    # Release Visibility Policy: immediate, scheduled, manual_hold
    status = Column(String(30), default="released", index=True) # provisional, released, under_appeal
    released_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    released_by_id = Column(String(64), nullable=True) # None for automatic release
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    attempt = relationship("Attempt", back_populates="grade")
    feedbacks = relationship("Feedback", back_populates="grade", cascade="all, delete-orphan")
    appeals = relationship("Appeal", back_populates="grade", cascade="all, delete-orphan")

class Feedback(Base):
    __tablename__ = "grade_feedbacks_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"fb-{uuid.uuid4().hex[:12]}")
    grade_id = Column(String(64), ForeignKey("grades_v2.id"), nullable=False, index=True)
    feedback_text = Column(Text, nullable=True)
    item_breakdown_json = Column(Text, nullable=False) # JSON: [{itemId, isCorrect, earnedPoints, explanation}]
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    grade = relationship("Grade", back_populates="feedbacks")

class Appeal(Base):
    """Grade appeal submitted by a student for instructor review."""
    __tablename__ = "grade_appeals_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"apl-{uuid.uuid4().hex[:12]}")
    grade_id = Column(String(64), ForeignKey("grades_v2.id"), nullable=False, index=True)
    learner_id = Column(String(64), nullable=False)
    reason = Column(Text, nullable=False)
    status = Column(String(30), default="pending", index=True) # pending, approved, rejected
    reviewer_notes = Column(Text, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    grade = relationship("Grade", back_populates="appeals")
