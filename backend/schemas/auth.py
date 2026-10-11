"""
Pydantic v2 Schemas for Identity and Authentication.
"""

from typing import Optional
from pydantic import BaseModel, EmailStr, Field

class UserRegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=2)
    role: str = Field(default="learner") # learner, instructor, grader, tenant_admin
    department: Optional[str] = "General"
    tenant_id: Optional[str] = None

class UserLoginRequest(BaseModel):
    username: str
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in_minutes: int
    user_id: str
    username: str
    role: str
    full_name: str
    tenant_id: str

class UserProfileResponse(BaseModel):
    id: str
    username: str
    full_name: str
    role: str
    department: Optional[str]
    tenant_id: str
    accommodations_extra_time_percent: int
