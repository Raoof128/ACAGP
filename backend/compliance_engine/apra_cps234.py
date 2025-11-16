"""
APRA CPS 234 Information Security Compliance Engine.

Implements automated checks for APRA Prudential Standard CPS 234,
which applies to APRA-regulated entities (banks, insurers, superannuation funds).

Reference: https://www.apra.gov.au/sites/default/files/cps_234_july_2019_for_public_release.pdf
"""

from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta

from .base import (
    ComplianceCheck,
    ComplianceRuleEngine,
    CheckResult,
    CheckStatus,
    Severity,
    Evidence,
)


# ============================================================================
# CPS 234.1: INFORMATION SECURITY GOVERNANCE
# ============================================================================

class CPS234_1_CISOAppointed(ComplianceCheck):
    """Check if Chief Information Security Officer is appointed."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-1-001",
            control_id="CPS_234.1",
            name="CISO Appointment Verification",
            description="Verify that a qualified CISO or equivalent is appointed",
            severity=Severity.CRITICAL,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        org_config = context.get("organization_config", {})
        ciso_appointed = org_config.get("ciso_appointed", False)
        ciso_name = org_config.get("ciso_name")
        appointment_date = org_config.get("ciso_appointment_date")

        if ciso_appointed and ciso_name:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"CISO appointed: {ciso_name} (since {appointment_date})",
                evidence=[
                    Evidence(
                        artifact_type="POLICY_DOC",
                        source_system="HR_SYSTEM",
                        artifact_data={"ciso_name": ciso_name, "date": appointment_date}
                    )
                ],
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings="No CISO or equivalent role appointed",
                remediation_required=True,
                remediation_guidance="Appoint a qualified CISO with appropriate authority and resources",
                remediation_priority="CRITICAL",
            )


class CPS234_1_PolicyDocumented(ComplianceCheck):
    """Check if information security policy is documented and board-approved."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-1-002",
            control_id="CPS_234.1",
            name="Information Security Policy Documentation",
            description="Verify documented and board-approved IS policy exists",
            severity=Severity.CRITICAL,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        policies = context.get("policies", {})
        is_policy = policies.get("information_security_policy", {})

        documented = is_policy.get("documented", False)
        board_approved = is_policy.get("board_approved", False)
        last_review_date = is_policy.get("last_review_date")

        if documented and board_approved:
            # Check if reviewed within last 12 months
            if last_review_date:
                last_review = datetime.fromisoformat(last_review_date)
                if (datetime.utcnow() - last_review).days <= 365:
                    return CheckResult(
                        check_id=self.check_id,
                        control_id=self.control_id,
                        status=CheckStatus.PASS,
                        severity=self.severity,
                        findings=f"IS policy documented, board-approved, last reviewed: {last_review_date}",
                    )

            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                findings="IS policy exists but not reviewed within 12 months",
                remediation_required=True,
                remediation_guidance="Review and update IS policy annually with board approval",
                remediation_priority="HIGH",
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings="IS policy not documented or not board-approved",
                remediation_required=True,
                remediation_guidance="Develop comprehensive IS policy and obtain board approval",
                remediation_priority="CRITICAL",
            )


class CPS234_1_RiskAssessment(ComplianceCheck):
    """Check if annual IS risk assessment is completed."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-1-003",
            control_id="CPS_234.1",
            name="Annual IS Risk Assessment",
            description="Verify annual information security risk assessment completed",
            severity=Severity.HIGH,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        risk_assessments = context.get("risk_assessments", [])

        # Check for risk assessment in last 12 months
        recent_assessment = None
        for assessment in risk_assessments:
            assessment_date = datetime.fromisoformat(assessment.get("date"))
            if (datetime.utcnow() - assessment_date).days <= 365:
                recent_assessment = assessment
                break

        if recent_assessment:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"IS risk assessment completed: {recent_assessment.get('date')}",
                evidence=[
                    Evidence(
                        artifact_type="ASSESSMENT_REPORT",
                        source_system="GRC_PLATFORM",
                        artifact_data=recent_assessment
                    )
                ],
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings="No IS risk assessment completed in last 12 months",
                remediation_required=True,
                remediation_guidance="Conduct comprehensive IS risk assessment covering all information assets",
                remediation_priority="HIGH",
            )


class CPS234_1_IncidentResponsePlan(ComplianceCheck):
    """Check if incident response plan exists and is tested."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-1-004",
            control_id="CPS_234.1",
            name="Incident Response Plan Testing",
            description="Verify IR plan exists and is tested at least quarterly",
            severity=Severity.HIGH,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        ir_plan = context.get("incident_response_plan", {})
        plan_exists = ir_plan.get("documented", False)
        last_test_date = ir_plan.get("last_test_date")

        if not plan_exists:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=Severity.CRITICAL,
                findings="No documented incident response plan",
                remediation_required=True,
                remediation_guidance="Develop and document comprehensive incident response plan",
                remediation_priority="CRITICAL",
            )

        if last_test_date:
            last_test = datetime.fromisoformat(last_test_date)
            days_since_test = (datetime.utcnow() - last_test).days

            if days_since_test <= 90:  # Quarterly
                return CheckResult(
                    check_id=self.check_id,
                    control_id=self.control_id,
                    status=CheckStatus.PASS,
                    severity=self.severity,
                    findings=f"IR plan tested {days_since_test} days ago (last: {last_test_date})",
                )
            else:
                return CheckResult(
                    check_id=self.check_id,
                    control_id=self.control_id,
                    status=CheckStatus.FAIL,
                    severity=Severity.HIGH,
                    findings=f"IR plan not tested in last 90 days (last test: {last_test_date})",
                    remediation_required=True,
                    remediation_guidance="Conduct quarterly IR plan tabletop exercises",
                    remediation_priority="HIGH",
                )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=Severity.HIGH,
                findings="IR plan exists but no evidence of testing",
                remediation_required=True,
                remediation_guidance="Implement quarterly IR plan testing program",
                remediation_priority="HIGH",
            )


# ============================================================================
# CPS 234.2: INFORMATION SECURITY CAPABILITY
# ============================================================================

class CPS234_2_SecurityAwareness(ComplianceCheck):
    """Check if security awareness training is provided."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-2-001",
            control_id="CPS_234.2",
            name="Security Awareness Training",
            description="Verify employees receive regular security awareness training",
            severity=Severity.MEDIUM,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        training_data = context.get("security_training", {})
        completion_rate = training_data.get("completion_rate", 0)
        last_training_date = training_data.get("last_training_date")

        if completion_rate >= 95 and last_training_date:
            last_training = datetime.fromisoformat(last_training_date)
            if (datetime.utcnow() - last_training).days <= 365:
                return CheckResult(
                    check_id=self.check_id,
                    control_id=self.control_id,
                    status=CheckStatus.PASS,
                    severity=self.severity,
                    findings=f"Security awareness training: {completion_rate}% completion rate",
                )

        return CheckResult(
            check_id=self.check_id,
            control_id=self.control_id,
            status=CheckStatus.FAIL,
            severity=self.severity,
            findings=f"Inadequate security training coverage: {completion_rate}%",
            remediation_required=True,
            remediation_guidance="Implement mandatory annual security awareness training for all staff",
            remediation_priority="MEDIUM",
        )


# ============================================================================
# CPS 234.4: IMPLEMENTATION OF CONTROLS
# ============================================================================

class CPS234_4_EncryptionAtRest(ComplianceCheck):
    """Check if encryption at rest is implemented for sensitive data."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-4-001",
            control_id="CPS_234.4",
            name="Encryption at Rest",
            description="Verify encryption at rest for databases and storage",
            severity=Severity.CRITICAL,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        aws_config = context.get("aws_config", {})
        databases = aws_config.get("rds_instances", [])
        s3_buckets = aws_config.get("s3_buckets", [])

        unencrypted_resources = []

        # Check RDS encryption
        for db in databases:
            if not db.get("encrypted", False):
                unencrypted_resources.append(f"RDS: {db.get('identifier')}")

        # Check S3 bucket encryption
        for bucket in s3_buckets:
            if not bucket.get("encryption_enabled", False):
                unencrypted_resources.append(f"S3: {bucket.get('name')}")

        if not unencrypted_resources:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings="All databases and storage encrypted at rest",
                evidence=[
                    Evidence(
                        artifact_type="CONFIG",
                        source_system="AWS_CONFIG",
                        artifact_data={"databases": len(databases), "buckets": len(s3_buckets)}
                    )
                ],
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"Unencrypted resources found: {', '.join(unencrypted_resources)}",
                remediation_required=True,
                remediation_guidance="Enable encryption at rest for all databases and storage",
                remediation_priority="CRITICAL",
            )


class CPS234_4_MFAEnabled(ComplianceCheck):
    """Check if MFA is enabled for privileged accounts."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-4-002",
            control_id="CPS_234.4",
            name="Multi-Factor Authentication",
            description="Verify MFA enabled for all privileged accounts",
            severity=Severity.CRITICAL,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        iam_users = context.get("aws_iam_users", [])
        privileged_users = [u for u in iam_users if u.get("is_privileged", False)]

        users_without_mfa = [
            u.get("username") for u in privileged_users
            if not u.get("mfa_enabled", False)
        ]

        if not users_without_mfa:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"MFA enabled for all {len(privileged_users)} privileged accounts",
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"{len(users_without_mfa)} privileged accounts without MFA: {', '.join(users_without_mfa[:5])}",
                remediation_required=True,
                remediation_guidance="Enforce MFA for all privileged accounts immediately",
                remediation_priority="CRITICAL",
            )


class CPS234_4_PatchManagement(ComplianceCheck):
    """Check if critical patches are applied within acceptable timeframe."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-4-003",
            control_id="CPS_234.4",
            name="Patch Management",
            description="Verify critical patches applied within 30 days",
            severity=Severity.HIGH,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        patch_data = context.get("patch_management", {})
        outstanding_critical = patch_data.get("critical_patches_outstanding", [])

        overdue_patches = []
        for patch in outstanding_critical:
            release_date = datetime.fromisoformat(patch.get("release_date"))
            days_outstanding = (datetime.utcnow() - release_date).days
            if days_outstanding > 30:
                overdue_patches.append({
                    "patch": patch.get("name"),
                    "days_overdue": days_outstanding
                })

        if not overdue_patches:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"All critical patches applied within 30 days ({len(outstanding_critical)} patches reviewed)",
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"{len(overdue_patches)} critical patches overdue beyond 30 days",
                remediation_required=True,
                remediation_guidance="Apply all critical patches within 30 days of release",
                remediation_priority="HIGH",
                metadata={"overdue_patches": overdue_patches[:10]},
            )


class CPS234_4_AccessControl(ComplianceCheck):
    """Check if least privilege access control is implemented."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-4-004",
            control_id="CPS_234.4",
            name="Least Privilege Access Control",
            description="Verify least privilege principle in IAM policies",
            severity=Severity.HIGH,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        iam_users = context.get("aws_iam_users", [])
        admin_users = [u for u in iam_users if "AdministratorAccess" in u.get("policies", [])]

        total_users = len(iam_users)
        admin_percentage = (len(admin_users) / total_users * 100) if total_users > 0 else 0

        # Acceptable threshold: <10% of users should have admin access
        if admin_percentage < 10:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"Least privilege maintained: {admin_percentage:.1f}% users with admin access",
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"Excessive admin access: {admin_percentage:.1f}% users with AdministratorAccess",
                remediation_required=True,
                remediation_guidance="Review and remove unnecessary admin privileges, implement least privilege",
                remediation_priority="HIGH",
            )


class CPS234_4_NetworkSegmentation(ComplianceCheck):
    """Check if network segmentation is implemented."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-4-005",
            control_id="CPS_234.4",
            name="Network Segmentation",
            description="Verify network segmentation with security groups",
            severity=Severity.HIGH,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        security_groups = context.get("aws_security_groups", [])

        # Check for overly permissive rules (0.0.0.0/0 on sensitive ports)
        sensitive_ports = [22, 3389, 1433, 3306, 5432]
        permissive_rules = []

        for sg in security_groups:
            for rule in sg.get("ingress_rules", []):
                if rule.get("cidr") == "0.0.0.0/0" and rule.get("port") in sensitive_ports:
                    permissive_rules.append({
                        "sg_id": sg.get("id"),
                        "port": rule.get("port"),
                    })

        if not permissive_rules:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"Network segmentation properly configured ({len(security_groups)} security groups reviewed)",
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"{len(permissive_rules)} overly permissive security group rules found",
                remediation_required=True,
                remediation_guidance="Restrict access to sensitive ports, remove 0.0.0.0/0 rules",
                remediation_priority="HIGH",
                metadata={"permissive_rules": permissive_rules},
            )


# ============================================================================
# CPS 234.5: INCIDENT MANAGEMENT
# ============================================================================

class CPS234_5_IncidentDetection(ComplianceCheck):
    """Check if security monitoring and incident detection is enabled."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-5-001",
            control_id="CPS_234.5",
            name="Security Monitoring",
            description="Verify GuardDuty/Defender and CloudTrail/Activity Log enabled",
            severity=Severity.CRITICAL,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        aws_config = context.get("aws_config", {})
        guardduty_enabled = aws_config.get("guardduty_enabled", False)
        cloudtrail_enabled = aws_config.get("cloudtrail_enabled", False)

        if guardduty_enabled and cloudtrail_enabled:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings="Security monitoring enabled: GuardDuty and CloudTrail active",
            )
        else:
            missing = []
            if not guardduty_enabled:
                missing.append("GuardDuty")
            if not cloudtrail_enabled:
                missing.append("CloudTrail")

            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"Security monitoring gaps: {', '.join(missing)} not enabled",
                remediation_required=True,
                remediation_guidance="Enable GuardDuty and CloudTrail for all regions",
                remediation_priority="CRITICAL",
            )


class CPS234_5_IncidentLogging(ComplianceCheck):
    """Check if incident logs are retained for appropriate duration."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-5-002",
            control_id="CPS_234.5",
            name="Incident Log Retention",
            description="Verify security logs retained for minimum 7 years (APRA requirement)",
            severity=Severity.HIGH,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        log_retention = context.get("log_retention", {})
        cloudtrail_retention_days = log_retention.get("cloudtrail_retention_days", 0)
        s3_log_retention_days = log_retention.get("s3_log_retention_days", 0)

        required_days = 7 * 365  # 7 years

        if cloudtrail_retention_days >= required_days and s3_log_retention_days >= required_days:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"Log retention compliant: {cloudtrail_retention_days} days configured",
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"Insufficient log retention: {cloudtrail_retention_days} days (required: {required_days})",
                remediation_required=True,
                remediation_guidance="Configure log retention to 7 years minimum for APRA compliance",
                remediation_priority="HIGH",
            )


# ============================================================================
# CPS 234.6: THIRD PARTY ARRANGEMENTS
# ============================================================================

class CPS234_6_VendorRiskAssessment(ComplianceCheck):
    """Check if third-party vendor security assessments are conducted."""

    def __init__(self):
        super().__init__(
            check_id="CPS234-6-001",
            control_id="CPS_234.6",
            name="Third-Party Security Assessment",
            description="Verify security assessments completed for critical vendors",
            severity=Severity.HIGH,
            automated=True,
        )

    async def execute(self, context: Dict[str, Any]) -> CheckResult:
        vendors = context.get("third_party_vendors", [])
        critical_vendors = [v for v in vendors if v.get("criticality") == "CRITICAL"]

        vendors_without_assessment = []
        for vendor in critical_vendors:
            last_assessment = vendor.get("last_security_assessment")
            if not last_assessment:
                vendors_without_assessment.append(vendor.get("name"))
            else:
                assessment_date = datetime.fromisoformat(last_assessment)
                if (datetime.utcnow() - assessment_date).days > 365:
                    vendors_without_assessment.append(f"{vendor.get('name')} (assessment >1yr old)")

        if not vendors_without_assessment:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.PASS,
                severity=self.severity,
                findings=f"All {len(critical_vendors)} critical vendors have current security assessments",
            )
        else:
            return CheckResult(
                check_id=self.check_id,
                control_id=self.control_id,
                status=CheckStatus.FAIL,
                severity=self.severity,
                findings=f"{len(vendors_without_assessment)} critical vendors lacking current security assessment",
                remediation_required=True,
                remediation_guidance="Conduct annual security assessments for all critical third-party vendors",
                remediation_priority="HIGH",
                metadata={"vendors": vendors_without_assessment},
            )


# ============================================================================
# APRA CPS 234 ENGINE
# ============================================================================

class APRACPS234Engine(ComplianceRuleEngine):
    """APRA CPS 234 compliance rules engine."""

    @property
    def framework_code(self) -> str:
        return "APRA_CPS_234"

    @property
    def framework_name(self) -> str:
        return "APRA Prudential Standard CPS 234 - Information Security"

    def _initialize_checks(self) -> None:
        """Initialize all APRA CPS 234 compliance checks."""

        # CPS 234.1: Information Security Governance
        self.checks.extend([
            CPS234_1_CISOAppointed(),
            CPS234_1_PolicyDocumented(),
            CPS234_1_RiskAssessment(),
            CPS234_1_IncidentResponsePlan(),
        ])

        # CPS 234.2: Information Security Capability
        self.checks.extend([
            CPS234_2_SecurityAwareness(),
        ])

        # CPS 234.4: Implementation of Controls
        self.checks.extend([
            CPS234_4_EncryptionAtRest(),
            CPS234_4_MFAEnabled(),
            CPS234_4_PatchManagement(),
            CPS234_4_AccessControl(),
            CPS234_4_NetworkSegmentation(),
        ])

        # CPS 234.5: Incident Management
        self.checks.extend([
            CPS234_5_IncidentDetection(),
            CPS234_5_IncidentLogging(),
        ])

        # CPS 234.6: Third Party Arrangements
        self.checks.extend([
            CPS234_6_VendorRiskAssessment(),
        ])

        # Total: 13 critical checks implemented
        # Note: In production, this would contain 50+ checks covering all CPS 234 requirements
