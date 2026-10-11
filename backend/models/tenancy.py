"""
Tenancy and Identity Domain Models (PostgreSQL / SQLite).
Enforces multi-tenancy boundaries and role attributes.
"""

import uuid
import datetime
from sqlalchemy import Column, String, Boolean, Integer, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from backend.core.database import Base

class Tenant(Base):
    __tablename__ = "tenants"

    id = Column(String(64), primary_key=True, default=lambda: f"ten-{uuid.uuid4().hex[:12]}")
    name = Column(String(255), nullable=False)
    domain = Column(String(255), nullable=True)
    settings_json = Column(Text, default="{}")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="tenant", cascade="all, delete-orphan")

class User(Base):
    __tablename__ = "platform_users"

    id = Column(String(64), primary_key=True, default=lambda: f"usr-{uuid.uuid4().hex[:12]}")
    tenant_id = Column(String(64), ForeignKey("tenants.id"), nullable=False, index=True)
    username = Column(String(100), nullable=False, unique=True, index=True)
    email = Column(String(255), nullable=True)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), nullable=False, default="learner") # learner, instructor, grader, tenant_admin, platform_support
    department = Column(String(150), nullable=True, default="General")
    is_active = Column(Boolean, default=True)
    accommodations_extra_time_percent = Column(Integer, default=0) # e.g. 50 = +50% extra time
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc))

    tenant = relationship("Tenant", back_populates="users")
    attempts = relationship("Attempt", back_populates="learner")
