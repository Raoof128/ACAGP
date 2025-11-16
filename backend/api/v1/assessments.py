"""
Compliance assessments API endpoints.
"""

from typing import List, Optional
from uuid import UUID
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc

from database import get_db
from models import ComplianceAssessment, Organization

router = APIRouter()


@router.get("/", response_model=List[dict])
async def list_assessments(
    db: AsyncSession = Depends(get_db),
    organization_id: Optional[UUID] = None,
    status_filter: Optional[str] = None,
    limit: int = 50
) -> List[dict]:
    """List compliance assessments."""
    query = select(ComplianceAssessment).order_by(desc(ComplianceAssessment.created_at))

    if organization_id:
        query = query.where(ComplianceAssessment.organization_id == organization_id)

    if status_filter:
        query = query.where(ComplianceAssessment.status == status_filter)

    query = query.limit(limit)

    result = await db.execute(query)
    assessments = result.scalars().all()

    return [
        {
            "id": str(assessment.id),
            "organization_id": str(assessment.organization_id),
            "framework_id": str(assessment.framework_id),
            "assessment_type": assessment.assessment_type,
            "status": assessment.status,
            "overall_score": float(assessment.overall_score) if assessment.overall_score else None,
            "controls_passed": assessment.controls_passed,
            "controls_failed": assessment.controls_failed,
            "critical_findings": assessment.critical_findings,
            "high_findings": assessment.high_findings,
            "started_at": assessment.started_at.isoformat() if assessment.started_at else None,
            "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
            "created_at": assessment.created_at.isoformat(),
        }
        for assessment in assessments
    ]


@router.get("/{assessment_id}", response_model=dict)
async def get_assessment(
    assessment_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get detailed assessment results."""
    result = await db.execute(
        select(ComplianceAssessment).where(ComplianceAssessment.id == assessment_id)
    )
    assessment = result.scalar_one_or_none()

    if not assessment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Assessment {assessment_id} not found"
        )

    return {
        "id": str(assessment.id),
        "organization_id": str(assessment.organization_id),
        "framework_id": str(assessment.framework_id),
        "assessment_type": assessment.assessment_type,
        "status": assessment.status,
        "overall_score": float(assessment.overall_score) if assessment.overall_score else None,
        "controls_passed": assessment.controls_passed,
        "controls_failed": assessment.controls_failed,
        "controls_not_applicable": assessment.controls_not_applicable,
        "critical_findings": assessment.critical_findings,
        "high_findings": assessment.high_findings,
        "medium_findings": assessment.medium_findings,
        "low_findings": assessment.low_findings,
        "started_at": assessment.started_at.isoformat() if assessment.started_at else None,
        "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
        "created_at": assessment.created_at.isoformat(),
        "updated_at": assessment.updated_at.isoformat(),
    }
