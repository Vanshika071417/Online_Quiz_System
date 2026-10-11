"""
Pydantic v2 Schemas for Audit Trail and Operational Monitoring.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel

class AuditEventResponse(BaseModel):
    id: str
    tenant_id: str
    actor_name: str
    action: str
    target_resource: str
    request_id: Optional[str]
    timestamp: str
    payload: Dict[str, Any]

class OperationalDashboardResponse(BaseModel):
    total_tenants: int
    total_users: int
    total_quizzes: int
    total_attempts: int
    active_in_progress_attempts: int
    completed_attempts: int
    average_pass_rate: float
    system_status: str
