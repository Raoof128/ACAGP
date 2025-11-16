"""Compliance-related models."""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Date, DateTime,
    ForeignKey, CheckConstraint, Numeric
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class ComplianceFramework(Base):
    """Compliance framework (APRA CPS 234, Essential Eight, etc.)."""

    __tablename__ = "compliance_frameworks"

    code = Column(String(50), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    version = Column(String(20))
    issuing_authority = Column(String(100))
    effective_date = Column(Date)
    jurisdiction = Column(String(50), default='Australia')
    is_active = Column(Boolean, default=True)
    metadata = Column(JSONB, default={})

    # Relationships
    controls = relationship("ComplianceControl", back_populates="framework")
    assessments = relationship("ComplianceAssessment", back_populates="framework")

    def __repr__(self) -> str:
        return f"<ComplianceFramework(code='{self.code}', name='{self.name}')>"


class ComplianceControl(Base):
    """Individual compliance control within a framework."""

    __tablename__ = "compliance_controls"

    framework_id = Column(UUID(as_uuid=True), ForeignKey("compliance_frameworks.id", ondelete="CASCADE"))
    control_id = Column(String(100), nullable=False)
    parent_control_id = Column(UUID(as_uuid=True), ForeignKey("compliance_controls.id"))
    name = Column(String(255), nullable=False)
    description = Column(Text)
    control_type = Column(String(50))
    severity = Column(String(20))
    automated_check_available = Column(Boolean, default=False)
    maturity_level = Column(Integer)  # For Essential Eight (0-3)
    metadata = Column(JSONB, default={})

    # Relationships
    framework = relationship("ComplianceFramework", back_populates="controls")
    parent_control = relationship("ComplianceControl", remote_side="ComplianceControl.id")
    assessment_results = relationship("AssessmentResult", back_populates="control")

    __table_args__ = (
        CheckConstraint(
            "control_type IN ('PREVENTIVE', 'DETECTIVE', 'CORRECTIVE', 'COMPENSATING')",
            name="check_control_type"
        ),
        CheckConstraint(
            "severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO')",
            name="check_severity"
        ),
        CheckConstraint(
            "maturity_level BETWEEN 0 AND 3",
            name="check_maturity_level"
        ),
    )

    def __repr__(self) -> str:
        return f"<ComplianceControl(control_id='{self.control_id}', name='{self.name}')>"


class ComplianceAssessment(Base):
    """Compliance assessment run against an organization."""

    __tablename__ = "compliance_assessments"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    framework_id = Column(UUID(as_uuid=True), ForeignKey("compliance_frameworks.id", ondelete="CASCADE"))
    assessment_type = Column(String(50))
    status = Column(String(50))

    overall_score = Column(Numeric(5, 2))  # Percentage 0-100
    controls_passed = Column(Integer, default=0)
    controls_failed = Column(Integer, default=0)
    controls_not_applicable = Column(Integer, default=0)

    critical_findings = Column(Integer, default=0)
    high_findings = Column(Integer, default=0)
    medium_findings = Column(Integer, default=0)
    low_findings = Column(Integer, default=0)

    started_at = Column(DateTime(timezone=True))
    completed_at = Column(DateTime(timezone=True))
    conducted_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    metadata = Column(JSONB, default={})

    # Relationships
    organization = relationship("Organization", back_populates="assessments")
    framework = relationship("ComplianceFramework", back_populates="assessments")
    results = relationship("AssessmentResult", back_populates="assessment")
    reports = relationship("AuditReport", back_populates="assessment")

    __table_args__ = (
        CheckConstraint(
            "assessment_type IN ('FULL', 'PARTIAL', 'CONTINUOUS', 'AUDIT')",
            name="check_assessment_type"
        ),
        CheckConstraint(
            "status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED')",
            name="check_status"
        ),
    )

    def __repr__(self) -> str:
        return f"<ComplianceAssessment(id={self.id}, status='{self.status}', score={self.overall_score})>"


class AssessmentResult(Base):
    """Result of a single control assessment."""

    __tablename__ = "assessment_results"

    assessment_id = Column(UUID(as_uuid=True), ForeignKey("compliance_assessments.id", ondelete="CASCADE"))
    control_id = Column(UUID(as_uuid=True), ForeignKey("compliance_controls.id", ondelete="CASCADE"))
    status = Column(String(50))
    evidence_collected = Column(JSONB, default=[])
    findings = Column(Text)

    remediation_required = Column(Boolean, default=False)
    remediation_priority = Column(String(20))
    remediation_deadline = Column(Date)

    tested_at = Column(DateTime(timezone=True))
    tested_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))

    metadata = Column(JSONB, default={})

    # Relationships
    assessment = relationship("ComplianceAssessment", back_populates="results")
    control = relationship("ComplianceControl", back_populates="assessment_results")
    evidence_artifacts = relationship("EvidenceArtifact", back_populates="assessment_result")
    remediation_tasks = relationship("RemediationTask", back_populates="assessment_result")

    __table_args__ = (
        CheckConstraint(
            "status IN ('PASS', 'FAIL', 'NOT_APPLICABLE', 'MANUAL_REVIEW', 'COMPENSATING_CONTROL')",
            name="check_result_status"
        ),
        CheckConstraint(
            "remediation_priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')",
            name="check_remediation_priority"
        ),
    )

    def __repr__(self) -> str:
        return f"<AssessmentResult(id={self.id}, status='{self.status}')>"
