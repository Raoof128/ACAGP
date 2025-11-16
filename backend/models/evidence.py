"""Evidence artifact model."""

from sqlalchemy import Column, String, Text, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class EvidenceArtifact(Base):
    """Evidence collected during compliance assessment."""

    __tablename__ = "evidence_artifacts"

    assessment_result_id = Column(
        UUID(as_uuid=True),
        ForeignKey("assessment_results.id", ondelete="CASCADE")
    )
    artifact_type = Column(String(100))  # LOG, SCREENSHOT, CONFIG, POLICY_DOC, etc.
    source_system = Column(String(100))  # AWS_CLOUDTRAIL, AZURE_MONITOR, SPLUNK, etc.
    artifact_url = Column(Text)
    artifact_hash = Column(String(64))  # SHA-256 hash for integrity
    collected_at = Column(DateTime(timezone=True))
    metadata = Column(JSONB, default={})

    # Relationships
    assessment_result = relationship("AssessmentResult", back_populates="evidence_artifacts")

    def __repr__(self) -> str:
        return f"<EvidenceArtifact(id={self.id}, type='{self.artifact_type}')>"
