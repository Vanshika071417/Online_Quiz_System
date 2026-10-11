"""
Deterministic Auto-Grading, Rubrics, Result Release, and Grade Appeal Domain Service.
"""

import json
import datetime
from typing import Dict, Any, List, Optional
from fastapi import HTTPException
from sqlalchemy.orm import Session

from backend.models.attempt import Attempt, AttemptAnswer
from backend.models.quiz import QuizVersion
from backend.models.grading import Grade, Feedback, Appeal
from backend.models.audit import AuditEvent, OutboxEvent
from backend.schemas.grading import ResultResponse, ItemResultBreakdown

class GradingService:
    @staticmethod
    def auto_grade_attempt(db: Session, attempt: Attempt) -> Grade:
        quiz_version = db.query(QuizVersion).filter(QuizVersion.id == attempt.quiz_version_id).first()
        if not quiz_version:
            raise HTTPException(status_code=500, detail="Quiz version snapshot missing")

        questions = json.loads(quiz_version.snapshot_json)
        answers_map = {}
        for ans in attempt.answers:
            try:
                data = json.loads(ans.answer_payload_json)
                answers_map[ans.item_id] = data.get("selectedOption")
            except Exception:
                pass

        total_points = 0.0
        earned_points = 0.0
        breakdown_list = []

        for q in questions:
            q_id = q["id"]
            max_p = float(q.get("points", 1.0))
            total_points += max_p
            correct_idx = int(q["correct"])
            user_selection = answers_map.get(q_id)

            is_correct = (user_selection is not None and user_selection == correct_idx)
            points_for_item = max_p if is_correct else 0.0
            earned_points += points_for_item

            breakdown_list.append({
                "item_id": q_id,
                "question_text": q["text"],
                "student_selected_option": user_selection,
                "correct_option": correct_idx,
                "is_correct": is_correct,
                "points_earned": points_for_item,
                "max_points": max_p,
                "explanation": q.get("explanation", "")
            })

        percentage = round((earned_points / total_points * 100), 2) if total_points > 0 else 0.0
        passed = percentage >= float(attempt.quiz.passing_score)

        existing_grade = db.query(Grade).filter(Grade.attempt_id == attempt.id).first()
        if existing_grade:
            grade = existing_grade
            grade.score = earned_points
            grade.total_points = total_points
            grade.percentage = percentage
            grade.passed = passed
            grade.status = "released"
        else:
            grade = Grade(
                attempt_id=attempt.id,
                score=earned_points,
                total_points=total_points,
                percentage=percentage,
                passed=passed,
                status="released"
            )
            db.add(grade)
            db.flush()

        # Save Feedback Item Breakdown
        existing_feedback = db.query(Feedback).filter(Feedback.grade_id == grade.id).first()
        if existing_feedback:
            existing_feedback.item_breakdown_json = json.dumps(breakdown_list)
        else:
            feedback = Feedback(
                grade_id=grade.id,
                feedback_text=f"Completed with {percentage}% score. {'Passed' if passed else 'Needs improvement.'}",
                item_breakdown_json=json.dumps(breakdown_list)
            )
            db.add(feedback)

        attempt.state = "evaluated"

        # Record Outbox Event for downstream sync
        db.add(OutboxEvent(
            event_type="GRADE_CALCULATED",
            aggregate_type="Grade",
            aggregate_id=grade.id,
            payload_json=json.dumps({
                "attempt_id": attempt.id,
                "score": earned_points,
                "percentage": percentage,
                "passed": passed
            })
        ))

        db.commit()
        db.refresh(grade)
        return grade

    @staticmethod
    def get_result(db: Session, attempt_id: str, requester_id: str, is_instructor: bool = False) -> ResultResponse:
        attempt = db.query(Attempt).filter(Attempt.id == attempt_id).first()
        if not attempt:
            raise HTTPException(status_code=404, detail="Attempt not found")
        if not is_instructor and attempt.learner_id != requester_id:
            raise HTTPException(status_code=403, detail="Unauthorized")

        grade = db.query(Grade).filter(Grade.attempt_id == attempt.id).first()
        if not grade:
            # If submitted but un-evaluated, run auto-grading now
            if attempt.state in ["submitted", "timed_out"]:
                grade = GradingService.auto_grade_attempt(db, attempt)
            else:
                raise HTTPException(status_code=400, detail="Results are not yet available for this in-progress attempt")

        breakdown = None
        # Only return detailed explanation breakdown if grade is released
        if grade.status == "released" or is_instructor:
            feedback = db.query(Feedback).filter(Feedback.grade_id == grade.id).first()
            if feedback:
                raw_items = json.loads(feedback.item_breakdown_json)
                breakdown = [ItemResultBreakdown(**item) for item in raw_items]

        return ResultResponse(
            attempt_id=attempt.id,
            quiz_title=attempt.quiz.title,
            learner_name=attempt.learner_name,
            score=grade.score,
            total_points=grade.total_points,
            percentage=grade.percentage,
            passed=grade.passed,
            cheat_violations=attempt.cheat_violations,
            status=grade.status,
            submitted_at=attempt.submitted_at.isoformat() if attempt.submitted_at else None,
            breakdown=breakdown
        )

    @staticmethod
    def submit_appeal(db: Session, attempt_id: str, learner_id: str, reason: str) -> Appeal:
        grade = db.query(Grade).filter(Grade.attempt_id == attempt_id).first()
        if not grade:
            raise HTTPException(status_code=404, detail="Grade record not found")

        appeal = Appeal(
            grade_id=grade.id,
            learner_id=learner_id,
            reason=reason,
            status="pending"
        )
        db.add(appeal)
        db.commit()
        db.refresh(appeal)
        return appeal
