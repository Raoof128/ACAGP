"""API v1 routes."""

from fastapi import APIRouter

from .compliance import router as compliance_router
from .assessments import router as assessments_router
from .organizations import router as organizations_router

api_router = APIRouter()

api_router.include_router(compliance_router, prefix="/compliance", tags=["Compliance"])
api_router.include_router(assessments_router, prefix="/assessments", tags=["Assessments"])
api_router.include_router(organizations_router, prefix="/organizations", tags=["Organizations"])

__all__ = ["api_router"]
