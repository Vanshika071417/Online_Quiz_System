"""
Audit and Transactional Outbox Domain Models.
Guarantees full forensic audibility and reliable asynchronous event delivery.
"""

import uuid
import datetime
from sqlalchemy import Column, String, DateTime, Text, Index
from backend.core.database import Base

class AuditEvent(Base):
    """Immutable audit trail for security and regulatory compliance."""
    __tablename__ = "audit_events_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"aud-{uuid.uuid4().hex[:12]}")
    tenant_id = Column(String(64), nullable=False, index=True)
    actor_id = Column(String(64), nullable=False, index=True)
    actor_name = Column(String(255), nullable=False)
    action = Column(String(100), nullable=False, index=True) # e.g. ATTEMPT_START, ANSWER_UPSERT, SUBMIT_FINALIZE, GRADE_RELEASE
    target_resource = Column(String(255), nullable=False)
    request_id = Column(String(64), nullable=True, index=True)
    payload_json = Column(Text, default="{}")
    timestamp = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)

class OutboxEvent(Base):
    """
    Transactional Outbox pattern.
    Committed atomically in the same database transaction as the domain state change.
    Workers poll or consume outbox events for background jobs without data loss.
    """
    __tablename__ = "outbox_events_v2"

    id = Column(String(64), primary_key=True, default=lambda: f"obx-{uuid.uuid4().hex[:12]}")
    event_type = Column(String(100), nullable=False, index=True) # e.g. ATTEMPT_SUBMITTED, GRADE_CALCULATED, QUIZ_PUBLISHED
    aggregate_type = Column(String(100), nullable=False) # Attempt, Grade, Quiz
    aggregate_id = Column(String(64), nullable=False, index=True)
    payload_json = Column(Text, nullable=False)
    status = Column(String(30), default="pending", index=True) # pending, processed, dead_letter
    retry_count = Column(String(10), default="0")
    created_at = Column(DateTime, default=lambda: datetime.datetime.now(datetime.timezone.utc), index=True)
    processed_at = Column(DateTime, nullable=True)
