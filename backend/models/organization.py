"""Organization model."""

from sqlalchemy import Column, String, DateTime, CheckConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import relationship

from .base import Base


class Organization(Base):
    """Organization model for companies using the platform."""

    __tablename__ = "organizations"

    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    abn = Column(String(11), unique=True)  # Australian Business Number
    regulatory_body = Column(String(100))  # APRA, ASIC, OAIC, etc.
    risk_tier = Column(String(20))

    # Contact information
    contact_email = Column(String(255))
    contact_phone = Column(String(20))

    # Address
    address_line1 = Column(String(255))
    address_line2 = Column(String(255))
    city = Column(String(100))
    state = Column(String(3))  # NSW, VIC, QLD, etc.
    postcode = Column(String(4))
    country = Column(String(2), default='AU')

    # Metadata
    metadata = Column(JSONB, default={})
    deleted_at = Column(DateTime(timezone=True))

    # Relationships
    users = relationship("User", back_populates="organization")
    assessments = relationship("ComplianceAssessment", back_populates="organization")
    remediation_tasks = relationship("RemediationTask", back_populates="organization")
    exceptions = relationship("ComplianceException", back_populates="organization")
    reports = relationship("AuditReport", back_populates="organization")
    breaches = relationship("BreachNotification", back_populates="organization")

    __table_args__ = (
        CheckConstraint(
            "risk_tier IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')",
            name="check_risk_tier"
        ),
    )

    def __repr__(self) -> str:
        return f"<Organization(id={self.id}, name='{self.name}', abn='{self.abn}')>"
