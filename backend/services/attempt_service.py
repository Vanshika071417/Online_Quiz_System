"""
Timed Attempts, Autosave, Monotonic Revisions, and Server Deadlines Domain Service.
"""

import json
import uuid
import datetime
from typing import Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.quiz import Quiz, QuizVersion
from backend.models.attempt import Attempt, AttemptAnswer
from backend.models.tenancy import User
from backend.models.audit import AuditEvent, OutboxEvent
from backend.services.quiz_service import QuizService
from backend.schemas.attempt import LearnerFormResponse

def get_now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)

def to_naive(dt: Any) -> datetime.datetime:
    if dt is not None and hasattr(dt, "tzinfo") and dt.tzinfo is not None:
        return dt.astimezone(datetime.timezone.utc).replace(tzinfo=None)
    return dt

class AttemptService:
    @staticmethod
    def start_or_resume_attempt(
        db: Session,
        quiz_id: str,
        learner: User,
        idempotency_key: Optional[str] = None
    ) -> LearnerFormResponse:
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz or not quiz.current_version_id:
            raise HTTPException(status_code=404, detail="Quiz not found or not published")

        # Idempotent Resume: return active in_progress attempt if exists
        existing_attempt = db.query(Attempt).filter(
            Attempt.quiz_id == quiz.id,
            Attempt.learner_id == learner.id,
            Attempt.state == "in_progress"
        ).first()

        now = get_now()

        if existing_attempt:
            # Check if deadline passed while away
            if now > to_naive(existing_attempt.deadline_at):
                existing_attempt.state = "timed_out"
                db.commit()
                raise HTTPException(status_code=400, detail="The authoritative time deadline for this attempt has expired.")
            return AttemptService._build_learner_form_response(db, existing_attempt)

        # Calculate Authoritative Deadline including accommodations
        duration_minutes = quiz.duration_minutes
        extra_percent = learner.accommodations_extra_time_percent or 0
        effective_duration_minutes = duration_minutes * (1.0 + (extra_percent / 100.0))
        deadline_at = now + datetime.timedelta(minutes=effective_duration_minutes)

        attempt = Attempt(
            tenant_id=quiz.tenant_id,
            quiz_id=quiz.id,
            quiz_version_id=quiz.current_version_id,
            learner_id=learner.id,
            learner_name=learner.full_name,
            state="in_progress",
            started_at=now,
            deadline_at=deadline_at,
            idempotency_key=idempotency_key
        )
        db.add(attempt)
        db.flush()

        db.add(AuditEvent(
            tenant_id=quiz.tenant_id,
            actor_id=learner.id,
            actor_name=learner.full_name,
            action="ATTEMPT_STARTED",
            target_resource=attempt.id,
            payload_json=json.dumps({"quiz_id": quiz.id, "deadline": deadline_at.isoformat()})
        ))
        db.commit()
        db.refresh(attempt)

        return AttemptService._build_learner_form_response(db, attempt)

    @staticmethod
    def get_attempt_for_resume(db: Session, attempt_id: str, learner_id: str) -> LearnerFormResponse:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        if attempt.learner_id != learner_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to this attempt")

        now = get_now()
        if attempt.state == "in_progress" and now > to_naive(attempt.deadline_at):
            attempt.state = "timed_out"
            db.commit()
            raise HTTPException(status_code=400, detail="Attempt deadline has expired.")

        return AttemptService._build_learner_form_response(db, attempt)

    @staticmethod
    def upsert_answer(
        db: Session,
        attempt_id: str,
        item_id: str,
        selected_option: int,
        revision: int,
        learner_id: str,
        idempotency_key: Optional[str] = None
    ) -> Dict[str, Any]:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        if attempt.learner_id != learner_id:
            raise HTTPException(status_code=403, detail="Unauthorized access to attempt")
        if attempt.state != "in_progress":
            raise HTTPException(status_code=400, detail=f"Cannot save answer. Attempt is already {attempt.state}")

        # Authoritative Server Clock Deadline Enforcement (with 15s grace period)
        now = get_now()
        grace_deadline = to_naive(attempt.deadline_at) + datetime.timedelta(seconds=15)
        if now > grace_deadline:
            attempt.state = "timed_out"
            db.commit()
            raise HTTPException(status_code=400, detail="Authoritative exam deadline has expired. Attempt marked timed out.")

        # Check Existing Answer & Monotonic Revision Guard
        existing_answer = db.query(AttemptAnswer).filter(
            AttemptAnswer.attempt_id == attempt_id,
            AttemptAnswer.item_id == item_id
        ).first()

        payload = {"selectedOption": selected_option}
        payload_json = json.dumps(payload)

        if existing_answer:
            if revision <= existing_answer.revision:
                # Concurrent tab or stale packet detected
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Stale revision rejected. Existing revision is {existing_answer.revision}, incoming is {revision}"
                )
            existing_answer.answer_payload_json = payload_json
            existing_answer.revision = revision
            existing_answer.saved_at = now
            existing_answer.idempotency_key = idempotency_key
            accepted_rev = revision
        else:
            new_ans = AttemptAnswer(
                attempt_id=attempt_id,
                item_id=item_id,
                answer_payload_json=payload_json,
                revision=revision,
                idempotency_key=idempotency_key,
                saved_at=now
            )
            db.add(new_ans)
            accepted_rev = revision

        db.commit()

        return {
            "success": True,
            "item_id": item_id,
            "accepted_revision": accepted_rev,
            "saved_at": now.isoformat()
        }

    @staticmethod
    def submit_attempt(db: Session, attempt_id: str, learner_id: str, cheat_violations: int = 0) -> Attempt:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        if attempt.learner_id != learner_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        if attempt.state in ["submitted", "evaluated"]:
            return attempt # Idempotent finalization

        now = datetime.datetime.now(datetime.timezone.utc)
        attempt.state = "submitted"
        attempt.submitted_at = now
        attempt.cheat_violations = cheat_violations

        # Atomic Outbox Event
        db.add(OutboxEvent(
            event_type="ATTEMPT_SUBMITTED",
            aggregate_type="Attempt",
            aggregate_id=attempt.id,
            payload_json=json.dumps({"attempt_id": attempt.id, "violations": cheat_violations})
        ))
        db.commit()
        db.refresh(attempt)

        # Trigger Immediate Deterministic Auto-Grading
        from backend.services.grading_service import GradingService
        GradingService.auto_grade_attempt(db, attempt)

        return attempt

    @staticmethod
    def _build_learner_form_response(db: Session, attempt: Attempt) -> LearnerFormResponse:
        quiz_version = db.query(QuizVersion).filter(QuizVersion.id == attempt.quiz_version_id).first()
        learner_safe_questions = QuizService.get_learner_safe_questions(quiz_version.snapshot_json)

        # Hydrate saved answers
        saved_answers = {}
        for ans in attempt.answers:
            try:
                data = json.loads(ans.answer_payload_json)
                saved_answers[ans.item_id] = data.get("selectedOption")
            except Exception:
                pass

        now = get_now()
        remaining = max(0, int((to_naive(attempt.deadline_at) - now).total_seconds()))

        return LearnerFormResponse(
            attempt_id=attempt.id,
            quiz_id=attempt.quiz_id,
            quiz_version_id=attempt.quiz_version_id,
            quiz_title=attempt.quiz.title,
            state=attempt.state,
            started_at=attempt.started_at.isoformat(),
            deadline_at=attempt.deadline_at.isoformat(),
            server_now=now.isoformat(),
            remaining_seconds=remaining,
            form_seed=attempt.form_seed,
            questions=learner_safe_questions,
            saved_answers=saved_answers
        )
