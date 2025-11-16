"""User model."""

from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from .base import Base


class User(Base):
    """User model for authentication and authorization."""

    __tablename__ = "users"

    organization_id = Column(UUID(as_uuid=True), ForeignKey("organizations.id", ondelete="CASCADE"))
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(String(50))

    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)
    last_login = Column(DateTime(timezone=True))

    metadata = Column(JSONB, default={})

    # Relationships
    organization = relationship("Organization", back_populates="users")

    __table_args__ = (
        CheckConstraint(
            "role IN ('ADMIN', 'COMPLIANCE_OFFICER', 'AUDITOR', 'VIEWER')",
            name="check_role"
        ),
    )

    def __repr__(self) -> str:
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
