"""
Organizations API endpoints.
"""

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, EmailStr

from database import get_db
from models import Organization

router = APIRouter()


class OrganizationCreate(BaseModel):
    """Schema for creating organization."""
    name: str
    industry: Optional[str] = None
    abn: Optional[str] = None
    regulatory_body: Optional[str] = None
    risk_tier: Optional[str] = "MEDIUM"
    contact_email: Optional[EmailStr] = None
    contact_phone: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    postcode: Optional[str] = None


@router.get("/", response_model=List[dict])
async def list_organizations(
    db: AsyncSession = Depends(get_db),
    limit: int = 100
) -> List[dict]:
    """List all organizations."""
    result = await db.execute(
        select(Organization)
        .where(Organization.deleted_at.is_(None))
        .limit(limit)
    )
    organizations = result.scalars().all()

    return [
        {
            "id": str(org.id),
            "name": org.name,
            "industry": org.industry,
            "abn": org.abn,
            "regulatory_body": org.regulatory_body,
            "risk_tier": org.risk_tier,
            "contact_email": org.contact_email,
            "state": org.state,
            "created_at": org.created_at.isoformat(),
        }
        for org in organizations
    ]


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def create_organization(
    org_data: OrganizationCreate,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Create a new organization."""
    # Check if ABN already exists
    if org_data.abn:
        existing = await db.execute(
            select(Organization).where(Organization.abn == org_data.abn)
        )
        if existing.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Organization with ABN {org_data.abn} already exists"
            )

    # Create organization
    organization = Organization(**org_data.model_dump())
    db.add(organization)
    await db.commit()
    await db.refresh(organization)

    return {
        "id": str(organization.id),
        "name": organization.name,
        "industry": organization.industry,
        "abn": organization.abn,
        "regulatory_body": organization.regulatory_body,
        "risk_tier": organization.risk_tier,
        "created_at": organization.created_at.isoformat(),
    }


@router.get("/{organization_id}", response_model=dict)
async def get_organization(
    organization_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> dict:
    """Get organization details."""
    result = await db.execute(
        select(Organization).where(Organization.id == organization_id)
    )
    organization = result.scalar_one_or_none()

    if not organization or organization.deleted_at is not None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Organization {organization_id} not found"
        )

    return {
        "id": str(organization.id),
        "name": organization.name,
        "industry": organization.industry,
        "abn": organization.abn,
        "regulatory_body": organization.regulatory_body,
        "risk_tier": organization.risk_tier,
        "contact_email": organization.contact_email,
        "contact_phone": organization.contact_phone,
        "address_line1": organization.address_line1,
        "address_line2": organization.address_line2,
        "city": organization.city,
        "state": organization.state,
        "postcode": organization.postcode,
        "country": organization.country,
        "created_at": organization.created_at.isoformat(),
        "updated_at": organization.updated_at.isoformat(),
    }
