"""Remediation task model."""

from sqlalchemy import (
    Column, String, Text, Boolean, Integer, Date, DateTime,
    ForeignKey, CheckConstraint
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class RemediationTask(Base):
    """Remediation task for compliance gaps."""

    __tablename__ = "remediation_tasks"

    assessment_result_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessment_results.id", ondelete="CASCADE")
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE")
    )

    title = Column(String(255), nullable=False)
    description = Column(Text)
    priority = Column(String(20))
    status = Column(String(50))

    assigned_to = Column(UUID(as_uuid=True), ForeignKey("users.id"))
    due_date = Column(Date)

    estimated_effort_hours = Column(Integer)
    actual_effort_hours = Column(Integer)

    auto_remediation_available = Column(Boolean, default=False)
    auto_remediation_script = Column(Text)

    completed_at = Column(DateTime(timezone=True))
    metadata = Column(JSONB, default={})

    # Relationships
    assessment_result = relationship("AssessmentResult", back_populates="remediation_tasks")
    organization = relationship("Organization", back_populates="remediation_tasks")

    __table_args__ = (
        CheckConstraint(
            "priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')",
            name="check_priority"
        ),
        CheckConstraint(
            "status IN ('OPEN', 'IN_PROGRESS', 'BLOCKED', 'COMPLETED', 'CANCELLED')",
            name="check_task_status"
        ),
    )

    def __repr__(self) -> str:
        return f"<RemediationTask(id={self.id}, title='{self.title}', status='{self.status}')>"
