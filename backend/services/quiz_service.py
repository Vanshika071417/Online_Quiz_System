"""
Quiz Authoring, Snapshot Publication, and Learner Sanitization Domain Service.
"""

import json
import uuid
import datetime
from typing import List, Dict, Any, Optional
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from backend.models.quiz import Quiz, QuizVersion
from backend.models.audit import AuditEvent, OutboxEvent
from backend.schemas.quiz import QuizCreateRequest, QuestionItemSchema, LearnerQuestionItemSchema

class QuizService:
    @staticmethod
    def create_quiz(db: Session, tenant_id: str, author_id: str, author_name: str, req: QuizCreateRequest) -> Quiz:
        join_code = req.join_code or f"QZ-{uuid.uuid4().hex[:4].upper()}"
        
        # Check duplicate join code
        existing = db.query(Quiz).filter(Quiz.join_code == join_code).first()
        if existing:
            join_code = f"QZ-{uuid.uuid4().hex[:4].upper()}"

        quiz = Quiz(
            tenant_id=tenant_id,
            title=req.title,
            category=req.category,
            description=req.description,
            join_code=join_code,
            teacher_name=author_name,
            duration_minutes=req.duration_minutes,
            passing_score=req.passing_score,
            status="published"
        )
        db.add(quiz)
        db.flush()

        # Create Initial Immutable Version 1 Snapshot
        questions_dict_list = [q.model_dump() for q in req.questions]
        quiz_version = QuizVersion(
            quiz_id=quiz.id,
            version_number=1,
            snapshot_json=json.dumps(questions_dict_list),
            published_by_id=author_id
        )
        db.add(quiz_version)
        db.flush()

        quiz.current_version_id = quiz_version.id

        # Record Audit and Outbox Events
        db.add(AuditEvent(
            tenant_id=tenant_id,
            actor_id=author_id,
            actor_name=author_name,
            action="QUIZ_PUBLISHED",
            target_resource=quiz.id,
            payload_json=json.dumps({"title": quiz.title, "version": 1})
        ))
        db.add(OutboxEvent(
            event_type="QUIZ_PUBLISHED",
            aggregate_type="Quiz",
            aggregate_id=quiz.id,
            payload_json=json.dumps({"quiz_id": quiz.id, "join_code": quiz.join_code})
        ))

        db.commit()
        db.refresh(quiz)
        return quiz

    @staticmethod
    def publish_new_version(db: Session, quiz_id: str, author_id: str, author_name: str, questions: List[QuestionItemSchema]) -> QuizVersion:
        """Publishes an immutable snapshot with incremented version number."""
        quiz = db.query(Quiz).filter(Quiz.id == quiz_id).first()
        if not quiz:
            raise HTTPException(status_code=404, detail="Quiz not found")

        last_version = db.query(QuizVersion).filter(QuizVersion.quiz_id == quiz_id).order_by(QuizVersion.version_number.desc()).first()
        new_version_num = (last_version.version_number + 1) if last_version else 1

        questions_dict_list = [q.model_dump() for q in questions]
        new_qv = QuizVersion(
            quiz_id=quiz.id,
            version_number=new_version_num,
            snapshot_json=json.dumps(questions_dict_list),
            published_by_id=author_id
        )
        db.add(new_qv)
        db.flush()

        quiz.current_version_id = new_qv.id
        quiz.updated_at = datetime.datetime.now(datetime.timezone.utc)

        db.add(AuditEvent(
            tenant_id=quiz.tenant_id,
            actor_id=author_id,
            actor_name=author_name,
            action="QUIZ_NEW_VERSION_PUBLISHED",
            target_resource=quiz.id,
            payload_json=json.dumps({"version": new_version_num})
        ))

        db.commit()
        db.refresh(new_qv)
        return new_qv

    @staticmethod
    def get_learner_safe_questions(snapshot_json_str: str) -> List[LearnerQuestionItemSchema]:
        """Strips correct answer indices and explanations to guarantee answer key security."""
        raw_list = json.loads(snapshot_json_str)
        learner_items = []
        for item in raw_list:
            learner_items.append(LearnerQuestionItemSchema(
                id=item["id"],
                text=item["text"],
                code=item.get("code"),
                options=item["options"],
                points=item.get("points", 1.0),
                question_type=item.get("question_type", "single_choice")
            ))
        return learner_items
