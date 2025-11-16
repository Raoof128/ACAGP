"""
Compliance API endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from database import get_db
from models import ComplianceFramework, ComplianceControl
from compliance_engine import APRACPS234Engine

router = APIRouter()


@router.get("/frameworks", response_model=List[dict])
async def list_frameworks(
    db: AsyncSession = Depends(get_db),
    is_active: Optional[bool] = True
) -> List[dict]:
    """List all compliance frameworks."""
    query = select(ComplianceFramework)
    if is_active is not None:
        query = query.where(ComplianceFramework.is_active == is_active)

    result = await db.execute(query)
    frameworks = result.scalars().all()

    return [
        {
            "id": str(framework.id),
            "code": framework.code,
            "name": framework.name,
            "description": framework.description,
            "version": framework.version,
            "issuing_authority": framework.issuing_authority,
            "is_active": framework.is_active,
        }
        for framework in frameworks
    ]


@router.get("/frameworks/{framework_code}/controls", response_model=List[dict])
async def list_controls(
    framework_code: str,
    db: AsyncSession = Depends(get_db)
) -> List[dict]:
    """List all controls for a specific framework."""
    # Get framework
    framework_result = await db.execute(
        select(ComplianceFramework).where(ComplianceFramework.code == framework_code)
    )
    framework = framework_result.scalar_one_or_none()

    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework {framework_code} not found"
        )

    # Get controls
    controls_result = await db.execute(
        select(ComplianceControl).where(
            ComplianceControl.framework_id == framework.id
        )
    )
    controls = controls_result.scalars().all()

    return [
        {
            "id": str(control.id),
            "control_id": control.control_id,
            "name": control.name,
            "description": control.description,
            "severity": control.severity,
            "automated_check_available": control.automated_check_available,
        }
        for control in controls
    ]


@router.post("/assess/{framework_code}")
async def run_assessment(
    framework_code: str,
    organization_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    Run compliance assessment for a specific framework.

    This is a simplified MVP version. In production, this would:
    1. Queue assessment as Celery task
    2. Collect evidence from cloud providers
    3. Store results in database
    4. Return assessment ID for polling
    """
    # Validate framework exists
    framework_result = await db.execute(
        select(ComplianceFramework).where(ComplianceFramework.code == framework_code)
    )
    framework = framework_result.scalar_one_or_none()

    if not framework:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Framework {framework_code} not found"
        )

    # Run assessment based on framework
    if framework_code == "APRA_CPS_234":
        engine = APRACPS234Engine()

        # Mock context data (in production, fetch from AWS/Azure)
        context = {
            "organization_id": str(organization_id),
            "organization_config": {
                "ciso_appointed": True,
                "ciso_name": "Jane Smith",
                "ciso_appointment_date": "2023-01-15",
            },
            "policies": {
                "information_security_policy": {
                    "documented": True,
                    "board_approved": True,
                    "last_review_date": "2024-06-01",
                }
            },
            "risk_assessments": [
                {"date": "2024-03-15", "type": "annual"}
            ],
            "incident_response_plan": {
                "documented": True,
                "last_test_date": "2024-10-01",
            },
            "security_training": {
                "completion_rate": 96,
                "last_training_date": "2024-08-01",
            },
            "aws_config": {
                "guardduty_enabled": True,
                "cloudtrail_enabled": True,
                "rds_instances": [
                    {"identifier": "prod-db", "encrypted": True}
                ],
                "s3_buckets": [
                    {"name": "data-bucket", "encryption_enabled": True}
                ],
            },
            "aws_iam_users": [
                {"username": "admin1", "is_privileged": True, "mfa_enabled": True},
                {"username": "dev1", "is_privileged": False, "mfa_enabled": True},
            ],
            "patch_management": {
                "critical_patches_outstanding": []
            },
            "aws_security_groups": [
                {
                    "id": "sg-123",
                    "ingress_rules": [
                        {"cidr": "10.0.0.0/16", "port": 22}
                    ]
                }
            ],
            "log_retention": {
                "cloudtrail_retention_days": 2555,  # 7 years
                "s3_log_retention_days": 2555,
            },
            "third_party_vendors": [
                {
                    "name": "Vendor A",
                    "criticality": "CRITICAL",
                    "last_security_assessment": "2024-05-01",
                }
            ],
        }

        # Run assessment
        results = await engine.run_assessment(context)

        # Calculate score
        score_data = engine.calculate_compliance_score(results)

        return {
            "assessment_id": "mock-assessment-id",
            "framework": framework_code,
            "organization_id": str(organization_id),
            "status": "completed",
            **score_data,
            "results": [result.to_dict() for result in results],
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED,
            detail=f"Assessment engine for {framework_code} not yet implemented"
        )
