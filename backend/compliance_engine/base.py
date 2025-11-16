"""
Base classes for compliance rules engine.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import uuid4


class CheckStatus(str, Enum):
    """Compliance check result status."""
    PASS = "PASS"
    FAIL = "FAIL"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    MANUAL_REVIEW = "MANUAL_REVIEW"
    COMPENSATING_CONTROL = "COMPENSATING_CONTROL"
    ERROR = "ERROR"


class Severity(str, Enum):
    """Finding severity levels."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


@dataclass
class Evidence:
    """Evidence artifact from compliance check."""
    artifact_type: str  # LOG, CONFIG, SCREENSHOT, POLICY_DOC
    source_system: str  # AWS_CLOUDTRAIL, AZURE_MONITOR, etc.
    artifact_url: Optional[str] = None
    artifact_data: Optional[Dict[str, Any]] = None
    collected_at: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CheckResult:
    """Result of a compliance check."""
    check_id: str
    control_id: str
    status: CheckStatus
    severity: Severity
    findings: str
    evidence: List[Evidence] = field(default_factory=list)
    remediation_required: bool = False
    remediation_guidance: Optional[str] = None
    remediation_priority: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    checked_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "check_id": self.check_id,
            "control_id": self.control_id,
            "status": self.status.value,
            "severity": self.severity.value,
            "findings": self.findings,
            "evidence": [
                {
                    "type": e.artifact_type,
                    "source": e.source_system,
                    "url": e.artifact_url,
                    "collected_at": e.collected_at.isoformat(),
                }
                for e in self.evidence
            ],
            "remediation_required": self.remediation_required,
            "remediation_guidance": self.remediation_guidance,
            "remediation_priority": self.remediation_priority,
            "metadata": self.metadata,
            "checked_at": self.checked_at.isoformat(),
        }


@dataclass
class ComplianceCheck(ABC):
    """Base class for a compliance check."""

    check_id: str
    control_id: str
    name: str
    description: str
    severity: Severity
    automated: bool = True

    @abstractmethod
    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        """
        Execute the compliance check.

        Args:
            context: Execution context containing organization data, config, etc.

        Returns:
            CheckResult with status and evidence
        """
        pass


class ComplianceRuleEngine(ABC):
    """Base class for compliance framework rule engines."""

    def __init__(self):
        self.checks: List[ComplianceCheck] = []
        self._initialize_checks()

    @abstractmethod
    def _initialize_checks(self) -> None:
        """Initialize framework-specific compliance checks."""
        pass

    @property
    @abstractmethod
    def framework_code(self) -> str:
        """Framework identifier code."""
        pass

    @property
    @abstractmethod
    def framework_name(self) -> str:
        """Framework full name."""
        pass

    async def run_assessment(
        self,
        context: Dict[str, Any],
        control_ids: Optional[List[str]] = None
    ) -> List[CheckResult]:
        """
        Run compliance assessment.

        Args:
            context: Assessment context (org config, cloud credentials, etc.)
            control_ids: Optional list of specific control IDs to check

        Returns:
            List of check results
        """
        results = []

        # Filter checks if specific control IDs provided
        checks_to_run = self.checks
        if control_ids:
            checks_to_run = [
                check for check in self.checks
                if check.control_id in control_ids
            ]

        # Execute all checks
        for check in checks_to_run:
            try:
                result = await check.execute(context)
                results.append(result)
            except Exception as e:
                # Handle check execution errors
                error_result = CheckResult(
                    check_id=check.check_id,
                    control_id=check.control_id,
                    status=CheckStatus.ERROR,
                    severity=check.severity,
                    findings=f"Check execution failed: {str(e)}",
                    metadata={"error": str(e), "error_type": type(e).__name__}
                )
                results.append(error_result)

        return results

    def get_check_by_id(self, check_id: str) -> Optional[ComplianceCheck]:
        """Get a specific check by ID."""
        for check in self.checks:
            if check.check_id == check_id:
                return check
        return None

    def get_checks_by_control(self, control_id: str) -> List[ComplianceCheck]:
        """Get all checks for a specific control."""
        return [check for check in self.checks if check.control_id == control_id]

    def calculate_compliance_score(self, results: List[CheckResult]) -> Dict[str, Any]:
        """
        Calculate overall compliance score from results.

        Returns:
            Dictionary with score, pass/fail counts, and findings breakdown
        """
        total_checks = len(results)
        passed = sum(1 for r in results if r.status == CheckStatus.PASS)
        failed = sum(1 for r in results if r.status == CheckStatus.FAIL)
        not_applicable = sum(1 for r in results if r.status == CheckStatus.NOT_APPLICABLE)
        manual_review = sum(1 for r in results if r.status == CheckStatus.MANUAL_REVIEW)

        # Calculate score (excluding N/A and manual review)
        applicable_checks = total_checks - not_applicable - manual_review
        score = (passed / applicable_checks * 100) if applicable_checks > 0 else 0

        # Count findings by severity
        findings = {
            "critical": sum(1 for r in results if r.severity == Severity.CRITICAL and r.status == CheckStatus.FAIL),
            "high": sum(1 for r in results if r.severity == Severity.HIGH and r.status == CheckStatus.FAIL),
            "medium": sum(1 for r in results if r.severity == Severity.MEDIUM and r.status == CheckStatus.FAIL),
            "low": sum(1 for r in results if r.severity == Severity.LOW and r.status == CheckStatus.FAIL),
        }

        return {
            "overall_score": round(score, 2),
            "total_checks": total_checks,
            "passed": passed,
            "failed": failed,
            "not_applicable": not_applicable,
            "manual_review": manual_review,
            "findings": findings,
            "framework": self.framework_code,
        }
