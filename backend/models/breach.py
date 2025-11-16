"""Breach notification model (OAIC)."""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Date, DateTime,
    ForeignKey, CheckConstraint, ARRAY
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class BreachNotification(Base):
    """OAIC Notifiable Data Breach tracking."""

    __tablename__ = "breach_notifications"

    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE")
    )

    incident_id = Column(String(100), unique=True)
    breach_type = Column(String(100))
    affected_individuals_count = Column(Integer)
    data_types_compromised = Column(ARRAY(Text))

    breach_date = Column(Date, nullable=False)
    discovered_date = Column(Date, nullable=False)

    notification_required = Column(Boolean, default=False)
    oaic_notified = Column(Boolean, default=False)
    oaic_notification_date = Column(DateTime(timezone=True))

    individuals_notified = Column(Boolean, default=False)
    notification_method = Column(String(100))

    remediation_actions = Column(Text)
    status = Column(String(50))

    metadata = Column(JSONB, default={})

    # Relationships
    organization = relationship("Organization", back_populates="breaches")

    __table_args__ = (
        CheckConstraint(
            "status IN ('DETECTED', 'ASSESSING', 'NOTIFIED', 'REMEDIATED', 'CLOSED')",
            name="check_breach_status"
        ),
    )

    def __repr__(self) -> str:
        return f"<BreachNotification(id={self.id}, incident_id='{self.incident_id}', status='{self.status}')>"
