"""
Seed database with example data for development and testing.

Usage:
    python -m scripts.seed_data
"""

import asyncio
import sys
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timedelta

# Add backend directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database import AsyncSessionLocal
from models import (
    Organization,
    User,
    ComplianceFramework,
    ComplianceControl,
    ComplianceAssessment,
    AssessmentResult,
)
from sqlalchemy import select
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def seed_organizations():
    """Seed example organizations."""
    print("Seeding organizations...")

    organizations = [
        Organization(
            name="Demo Bank Australia Pty Ltd",
            industry="Financial Services",
            abn="12345678901",
            regulatory_body="APRA",
            risk_tier="HIGH",
            contact_email="compliance@demobank.com.au",
            contact_phone="02 9000 0000",
            address_line1="Level 20, 100 George Street",
            city="Sydney",
            state="NSW",
            postcode="2000",
            country="AU",
        ),
        Organization(
            name="SecureHealth Insurance Ltd",
            industry="Health Insurance",
            abn="23456789012",
            regulatory_body="APRA",
            risk_tier="MEDIUM",
            contact_email="it@securehealth.com.au",
            city="Melbourne",
            state="VIC",
            postcode="3000",
            country="AU",
        ),
        Organization(
            name="TechStart Solutions Pty Ltd",
            industry="Technology",
            abn="34567890123",
            regulatory_body="OAIC",
            risk_tier="LOW",
            contact_email="security@techstart.com.au",
            city="Brisbane",
            state="QLD",
            postcode="4000",
            country="AU",
        ),
    ]

    async with AsyncSessionLocal() as session:
        # Check if data already exists
        result = await session.execute(select(Organization).limit(1))
        if result.scalar_one_or_none():
            print("  Organizations already exist, skipping...")
            return organizations

        session.add_all(organizations)
        await session.commit()

        for org in organizations:
            await session.refresh(org)

    print(f"  ✓ Created {len(organizations)} organizations")
    return organizations


async def seed_users(organizations):
    """Seed example users."""
    print("Seeding users...")

    users = []
    for org in organizations[:1]:  # Only first org for demo
        users.extend([
            User(
                organization_id=org.id,
                email="admin@demobank.com.au",
                hashed_password=pwd_context.hash("Demo@123456"),
                full_name="Admin User",
                role="ADMIN",
                is_active=True,
            ),
            User(
                organization_id=org.id,
                email="compliance@demobank.com.au",
                hashed_password=pwd_context.hash("Demo@123456"),
                full_name="Compliance Officer",
                role="COMPLIANCE_OFFICER",
                is_active=True,
            ),
            User(
                organization_id=org.id,
                email="auditor@demobank.com.au",
                hashed_password=pwd_context.hash("Demo@123456"),
                full_name="External Auditor",
                role="AUDITOR",
                is_active=True,
            ),
        ])

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(User).limit(1))
        if result.scalar_one_or_none():
            print("  Users already exist, skipping...")
            return users

        session.add_all(users)
        await session.commit()

        for user in users:
            await session.refresh(user)

    print(f"  ✓ Created {len(users)} users")
    print("  📧 Default password for all users: Demo@123456")
    return users


async def seed_frameworks():
    """Seed compliance frameworks."""
    print("Seeding compliance frameworks...")

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ComplianceFramework))
        frameworks = result.scalars().all()

        if frameworks:
            print("  Frameworks already exist, skipping...")
            return frameworks

        # Frameworks should be created by init.sql, but add if missing
        print("  ⚠ No frameworks found. Run database/schemas/init.sql first")
        return []


async def seed_controls():
    """Seed example compliance controls."""
    print("Seeding compliance controls...")

    async with AsyncSessionLocal() as session:
        # Get APRA CPS 234 framework
        result = await session.execute(
            select(ComplianceFramework).where(ComplianceFramework.code == "APRA_CPS_234")
        )
        framework = result.scalar_one_or_none()

        if not framework:
            print("  ⚠ APRA CPS 234 framework not found. Run init.sql first")
            return []

        # Check if controls exist
        result = await session.execute(
            select(ComplianceControl).where(ComplianceControl.framework_id == framework.id).limit(1)
        )
        if result.scalar_one_or_none():
            print("  Controls already exist, skipping...")
            return []

        # Add sample controls
        controls = [
            ComplianceControl(
                framework_id=framework.id,
                control_id="CPS_234.1.1",
                name="CISO Appointment",
                description="Ensure Chief Information Security Officer is appointed",
                control_type="PREVENTIVE",
                severity="CRITICAL",
                automated_check_available=True,
            ),
            ComplianceControl(
                framework_id=framework.id,
                control_id="CPS_234.1.2",
                name="Information Security Policy",
                description="Documented and board-approved information security policy",
                control_type="PREVENTIVE",
                severity="CRITICAL",
                automated_check_available=True,
            ),
            ComplianceControl(
                framework_id=framework.id,
                control_id="CPS_234.4.1",
                name="Encryption at Rest",
                description="Ensure all sensitive data is encrypted at rest",
                control_type="PREVENTIVE",
                severity="HIGH",
                automated_check_available=True,
            ),
            ComplianceControl(
                framework_id=framework.id,
                control_id="CPS_234.4.2",
                name="Multi-Factor Authentication",
                description="MFA enabled for all privileged accounts",
                control_type="PREVENTIVE",
                severity="CRITICAL",
                automated_check_available=True,
            ),
        ]

        session.add_all(controls)
        await session.commit()

    print(f"  ✓ Created {len(controls)} compliance controls")
    return controls


async def seed_assessments(organizations, users, frameworks):
    """Seed example compliance assessments."""
    print("Seeding compliance assessments...")

    if not organizations or not users or not frameworks:
        print("  ⚠ Missing required data, skipping assessments")
        return []

    async with AsyncSessionLocal() as session:
        result = await session.execute(select(ComplianceAssessment).limit(1))
        if result.scalar_one_or_none():
            print("  Assessments already exist, skipping...")
            return []

        # Get APRA framework
        result = await session.execute(
            select(ComplianceFramework).where(ComplianceFramework.code == "APRA_CPS_234")
        )
        framework = result.scalar_one_or_none()

        if not framework:
            print("  ⚠ APRA framework not found")
            return []

        assessments = [
            ComplianceAssessment(
                organization_id=organizations[0].id,
                framework_id=framework.id,
                assessment_type="FULL",
                status="COMPLETED",
                overall_score=87.5,
                controls_passed=42,
                controls_failed=6,
                controls_not_applicable=2,
                critical_findings=2,
                high_findings=4,
                medium_findings=3,
                low_findings=1,
                started_at=datetime.utcnow() - timedelta(days=7),
                completed_at=datetime.utcnow() - timedelta(days=6),
                conducted_by=users[0].id if users else None,
            ),
            ComplianceAssessment(
                organization_id=organizations[0].id,
                framework_id=framework.id,
                assessment_type="CONTINUOUS",
                status="IN_PROGRESS",
                overall_score=89.2,
                controls_passed=45,
                controls_failed=5,
                critical_findings=1,
                high_findings=3,
                medium_findings=2,
                started_at=datetime.utcnow() - timedelta(hours=2),
                conducted_by=users[1].id if len(users) > 1 else None,
            ),
        ]

        session.add_all(assessments)
        await session.commit()

    print(f"  ✓ Created {len(assessments)} assessments")
    return assessments


async def main():
    """Main seeding function."""
    print("\n" + "="*60)
    print("ACAGP Database Seeding")
    print("="*60 + "\n")

    try:
        organizations = await seed_organizations()
        users = await seed_users(organizations)
        frameworks = await seed_frameworks()
        controls = await seed_controls()
        assessments = await seed_assessments(organizations, users, frameworks)

        print("\n" + "="*60)
        print("✓ Database seeding complete!")
        print("="*60)
        print(f"\n📊 Summary:")
        print(f"  • Organizations: {len(organizations)}")
        print(f"  • Users: {len(users)}")
        print(f"  • Frameworks: {len(frameworks) if frameworks else 'Run init.sql'}")
        print(f"  • Controls: {len(controls)}")
        print(f"  • Assessments: {len(assessments)}")

        if users:
            print(f"\n🔐 Login Credentials:")
            print(f"  Email: admin@demobank.com.au")
            print(f"  Password: Demo@123456")

        print(f"\n🚀 Next Steps:")
        print(f"  1. Start the application: docker-compose up -d")
        print(f"  2. Visit: http://localhost:8000/docs")
        print(f"  3. Test API endpoints with seeded data")
        print()

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
