"""Compliance exception model."""

from sqlalchemy import (
    Column, String, Text, Integer, Date, DateTime,
    ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class ComplianceException(Base):
    """Exception to compliance requirements."""

    __tablename__ = "compliance_exceptions"

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE")
    )
    control_id = Column(
        UUID(as_uuid=True),
        ForeignKey("compliance_controls.id", ondelete="CASCADE")
    )

    exception_type = Column(String(50))
    justification = Column(Text, nullable=False)
    compensating_controls = Column(Text)

    approved_by = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    approved_at = Column(DateTime(timezone=True))

    valid_from = Column(Date, nullable=False)
    valid_until = Column(Date)
    review_frequency_days = Column(Integer, default=90)
    next_review_date = Column(Date)

    status = Column(String(50))
    metadata = Column(JSONB, default={})

    # Relationships
    organization = relationship("Organization", back_populates="exceptions")

    __table_args__ = (
        CheckConstraint(
            "exception_type IN ('TEMPORARY', 'PERMANENT', 'RISK_ACCEPTED')",
            name="check_exception_type"
        ),
        CheckConstraint(
            "status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', 'REVOKED')",
            name="check_exception_status"
        ),
    )

    def __repr__(self) -> str:
        return f"<ComplianceException(id={self.id}, type='{self.exception_type}', status='{self.status}')>"
