"""
API v1 Root Router.
Aggregates all domain endpoints according to the architecture specification.
"""

from fastapi import APIRouter
from backend.api.v1.endpoints.auth import router as auth_router
from backend.api.v1.endpoints.quizzes import router as quizzes_router
from backend.api.v1.endpoints.attempts import router as attempts_router
from backend.api.v1.endpoints.results import router as results_router
from backend.api.v1.endpoints.admin import router as admin_router

api_v1_router = APIRouter(prefix="/v1")

api_v1_router.include_router(auth_router)
api_v1_router.include_router(quizzes_router)
api_v1_router.include_router(attempts_router)
api_v1_router.include_router(results_router)
api_v1_router.include_router(admin_router)
