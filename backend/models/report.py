"""Audit report model."""

from sqlalchemy import Column, String, Text, Date, DateTime, ForeignKey, CheckConstraint, BigInteger
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class AuditReport(Base):
    """Generated audit and compliance reports."""

    __tablename__ = "audit_reports"

    assessment_id = Column(
        UUID(as_uuid=True),
        ForeignKey("compliance_assessments.id", ondelete="CASCADE")
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE")
    )

    report_type = Column(String(50))
    framework_code = Column(String(50))
    title = Column(String(255), nullable=False)

    report_period_start = Column(Date)
    report_period_end = Column(Date)

    file_path = Column(Text)
    file_format = Column(String(10), default='PDF')
    file_size_bytes = Column(BigInteger)

    generated_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    generated_at = Column(DateTime(timezone=True))

    metadata = Column(JSONB, default={})

    # Relationships
    assessment = relationship("ComplianceAssessment", back_populates="reports")
    organization = relationship("Organization", back_populates="reports")

    __table_args__ = (
        CheckConstraint(
            "report_type IN ('COMPLIANCE', 'AUDIT', 'BOARD', 'REGULATORY')",
            name="check_report_type"
        ),
    )

    def __repr__(self) -> str:
        return f"<AuditReport(id={self.id}, title='{self.title}', type='{self.report_type}')>"
