"""
Authentication and Identity Endpoints (/v1/auth).
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.core.security import hash_password, verify_password, create_access_token, get_current_user
from backend.core.config import settings
from backend.models.tenancy import User, Tenant
from backend.schemas.auth import UserRegisterRequest, UserLoginRequest, TokenResponse, UserProfileResponse

router = APIRouter(prefix="/auth", tags=["Identity & Auth"])

@router.post("/register", response_model=TokenResponse)
def register(req: UserRegisterRequest, db: Session = Depends(get_db)):
    existing = db.query(User).filter(User.username == req.username).first()
    if existing:
        raise HTTPException(status_code=400, detail="Username already registered")

    tenant_id = req.tenant_id or settings.DEFAULT_TENANT_ID
    # Ensure tenant exists
    tenant = db.query(Tenant).filter(Tenant.id == tenant_id).first()
    if not tenant:
        tenant = Tenant(id=tenant_id, name=settings.DEFAULT_TENANT_NAME)
        db.add(tenant)
        db.flush()

    user = User(
        tenant_id=tenant_id,
        username=req.username,
        hashed_password=hash_password(req.password),
        full_name=req.full_name,
        role=req.role.lower(),
        department=req.department or "General"
    )
    db.add(user)
    db.commit()
    db.refresh(user)

    token = create_access_token({"sub": user.id, "role": user.role, "tenant_id": user.tenant_id})
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user_id=user.id,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        tenant_id=user.tenant_id
    )

@router.post("/login", response_model=TokenResponse)
def login(req: UserLoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == req.username).first()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password"
        )

    token = create_access_token({"sub": user.id, "role": user.role, "tenant_id": user.tenant_id})
    return TokenResponse(
        access_token=token,
        expires_in_minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES,
        user_id=user.id,
        username=user.username,
        role=user.role,
        full_name=user.full_name,
        tenant_id=user.tenant_id
    )

@router.get("/me", response_model=UserProfileResponse)
def get_profile(current_user: User = Depends(get_current_user)):
    return UserProfileResponse(
        id=current_user.id,
        username=current_user.username,
        full_name=current_user.full_name,
        role=current_user.role,
        department=current_user.department,
        tenant_id=current_user.tenant_id,
        accommodations_extra_time_percent=current_user.accommodations_extra_time_percent or 0
    )
