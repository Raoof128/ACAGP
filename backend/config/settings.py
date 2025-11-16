"""
Application configuration management using Pydantic Settings.
Loads configuration from environment variables and .env file.
"""

from typing import List, Optional
from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow"
    )

    # Application Settings
    app_name: str = Field(default="Australian Compliance Automation Platform")
    app_version: str = Field(default="1.0.0")
    environment: str = Field(default="development")
    debug: bool = Field(default=False)
    log_level: str = Field(default="INFO")

    # API Configuration
    api_host: str = Field(default="0.0.0.0")
    api_port: int = Field(default=8000)
    api_prefix: str = Field(default="/api/v1")
    cors_origins: str = Field(default="http://localhost:3000")

    @property
    def cors_origins_list(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    # Database Configuration
    database_url: str = Field(
        default="postgresql+asyncpg://postgres:postgres@localhost:5432/acagp"
    )
    database_pool_size: int = Field(default=20)
    database_max_overflow: int = Field(default=10)
    database_echo: bool = Field(default=False)
    timescale_enabled: bool = Field(default=True)

    # Authentication & Security
    secret_key: str = Field(default="change-this-secret-key-in-production")
    algorithm: str = Field(default="HS256")
    access_token_expire_minutes: int = Field(default=30)
    refresh_token_expire_days: int = Field(default=7)

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str, info) -> str:
        """Ensure secret key is changed in production."""
        if info.data.get("environment") == "production" and "change-this" in v:
            raise ValueError("Secret key must be changed in production environment")
        return v

    # AWS Configuration
    aws_region: str = Field(default="ap-southeast-2")
    aws_access_key_id: Optional[str] = Field(default=None)
    aws_secret_access_key: Optional[str] = Field(default=None)
    aws_cloudtrail_bucket: Optional[str] = Field(default=None)
    aws_config_bucket: Optional[str] = Field(default=None)
    aws_s3_reports_bucket: Optional[str] = Field(default=None)

    # Azure Configuration
    azure_tenant_id: Optional[str] = Field(default=None)
    azure_client_id: Optional[str] = Field(default=None)
    azure_client_secret: Optional[str] = Field(default=None)
    azure_subscription_id: Optional[str] = Field(default=None)
    azure_storage_account: Optional[str] = Field(default=None)
    azure_storage_key: Optional[str] = Field(default=None)

    # Redis Configuration
    redis_url: str = Field(default="redis://localhost:6379/0")
    celery_broker_url: str = Field(default="redis://localhost:6379/0")
    celery_result_backend: str = Field(default="redis://localhost:6379/0")

    # Compliance Engine Configuration
    compliance_check_interval_minutes: int = Field(default=15)
    max_concurrent_assessments: int = Field(default=5)
    enable_auto_remediation: bool = Field(default=False)

    # Report Generation
    reports_output_dir: str = Field(default="./reports/generated")
    reports_template_dir: str = Field(default="./reports/templates")
    reports_logo_path: str = Field(default="./assets/logo.png")

    # Monitoring & Observability
    prometheus_enabled: bool = Field(default=True)
    prometheus_port: int = Field(default=9090)
    sentry_dsn: Optional[str] = Field(default=None)
    sentry_traces_sample_rate: float = Field(default=0.1)

    # ML Model Configuration
    ml_models_dir: str = Field(default="./ml_models")
    ml_training_enabled: bool = Field(default=False)
    ml_risk_prediction_threshold: float = Field(default=0.75)

    # Feature Flags
    feature_apra_cps234: bool = Field(default=True)
    feature_essential_eight: bool = Field(default=True)
    feature_oaic_ndb: bool = Field(default=True)
    feature_pci_dss: bool = Field(default=True)
    feature_iso27001: bool = Field(default=False)
    feature_ml_risk_prediction: bool = Field(default=False)

    # Email Notifications
    smtp_host: str = Field(default="smtp.example.com")
    smtp_port: int = Field(default=587)
    smtp_user: Optional[str] = Field(default=None)
    smtp_password: Optional[str] = Field(default=None)
    smtp_from_email: str = Field(default="compliance@example.com")
    smtp_tls: bool = Field(default=True)

    # Logging
    log_format: str = Field(default="json")
    log_file_path: str = Field(default="./logs/acagp.log")
    log_rotation_size_mb: int = Field(default=100)
    log_retention_days: int = Field(default=90)

    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.environment.lower() == "production"

    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.environment.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """
    Get cached application settings.
    Using lru_cache ensures settings are loaded only once.
    """
    return Settings()


# Export settings instance
settings = get_settings()
