"""
Quiz Authoring and Immutable Snapshot Domain Models.
Guarantees that published quizzes are immutable snapshots so existing/past attempts remain 100% reproducible.
"""

import uuid
import datetime
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Quiz(Base):
    __tablename__ = "quizzes_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"qz-{uuid.uuid4().hex[:12]}")
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    category = Column(String(100), default="General", index=True)
    description = Column(Text, nullable=True)
    join_code = Column(String(20), unique=True, index=True, nullable=False)
    teacher_name = Column(String(150), default="Faculty Evaluator")
    duration_minutes = Column(Integer, default=15)
    passing_score = Column(Integer, default=70)
    status = Column(String(30), default="published", index=True) # draft, published, archived
    current_version_id = Column(String(64), nullable=True)
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), onupdate=lambda: datetime.datetime.now(datetime.timezone.utc))

    tenant = relationship("Tenant", back_populates="quizzes")
    versions = relationship("QuizVersion", back_populates="quiz", cascade="all, delete-orphan")
    attempts = relationship("Attempt", back_populates="quiz")

class QuizVersion(Base):
    """
    Immutable published snapshot.
    Contains frozen questions, correct keys, rubrics, and scoring policies.
    """
    __tablename__ = "quiz_versions"

    id = Column(String(64), primary_key=True, default=lambda: f"qv-{uuid.uuid4().hex[:12]}")
    quiz_id = Column(String(64), ForeignKey("quizzes_v2.id"), nullable=False, index=True)
    version_number = Column(Integer, default=1, nullable=False)
    snapshot_json = Column(Text, nullable=False) # JSON: [{id, text, options, correct, explanation, points, type}]
    published_by_id = Column(String(64), nullable=True)
    published_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    quiz = relationship("Quiz", back_populates="versions")
    attempts = relationship("Attempt", back_populates="quiz_version")
