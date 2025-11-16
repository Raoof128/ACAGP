"""
Tests for compliance engine.
"""

import pytest
from compliance_engine import APRACPS234Engine
from compliance_engine.base import CheckStatus


@pytest.mark.asyncio
async def test_apra_cps234_engine_initialization():
    """Test APRA CPS 234 engine initializes correctly."""
    engine = APRACPS234Engine()
    assert engine.framework_code == "APRA_CPS_234"
    assert engine.framework_name == "APRA Prudential Standard CPS 234 - Information Security"
    assert len(engine.checks) > 0


@pytest.mark.asyncio
async def test_apra_cps234_ciso_check_pass():
    """Test CISO appointment check passes with valid data."""
    engine = APRACPS234Engine()
    context = {
        "organization_config": {
            "ciso_appointed": True,
            "ciso_name": "John Doe",
            "ciso_appointment_date": "2023-01-01",
        }
    }

    check = engine.get_check_by_id("CPS234-1-001")
    assert check is not None

    result = await check.execute(context)
    assert result.status == CheckStatus.PASS
    assert result.control_id == "CPS_234.1"


@pytest.mark.asyncio
async def test_apra_cps234_ciso_check_fail():
    """Test CISO appointment check fails without CISO."""
    engine = APRACPS234Engine()
    context = {
        "organization_config": {
            "ciso_appointed": False,
        }
    }

    check = engine.get_check_by_id("CPS234-1-001")
    result = await check.execute(context)

    assert result.status == CheckStatus.FAIL
    assert result.remediation_required is True
    assert result.remediation_priority == "CRITICAL"


@pytest.mark.asyncio
async def test_compliance_score_calculation():
    """Test compliance score calculation."""
    engine = APRACPS234Engine()
    context = {
        "organization_config": {
            "ciso_appointed": True,
            "ciso_name": "Test",
            "ciso_appointment_date": "2023-01-01",
        },
        "policies": {
            "information_security_policy": {
                "documented": True,
                "board_approved": True,
                "last_review_date": "2024-06-01",
            }
        },
        "risk_assessments": [{"date": "2024-03-15"}],
        "incident_response_plan": {
            "documented": True,
            "last_test_date": "2024-10-01",
        },
        "security_training": {"completion_rate": 96, "last_training_date": "2024-08-01"},
        "aws_config": {
            "guardduty_enabled": True,
            "cloudtrail_enabled": True,
            "rds_instances": [{"identifier": "db", "encrypted": True}],
            "s3_buckets": [{"name": "bucket", "encryption_enabled": True}],
        },
        "aws_iam_users": [
            {"username": "admin", "is_privileged": True, "mfa_enabled": True}
        ],
        "patch_management": {"critical_patches_outstanding": []},
        "aws_security_groups": [{"id": "sg-1", "ingress_rules": []}],
        "log_retention": {
            "cloudtrail_retention_days": 2555,
            "s3_log_retention_days": 2555,
        },
        "third_party_vendors": [
            {
                "name": "Vendor",
                "criticality": "CRITICAL",
                "last_security_assessment": "2024-05-01",
            }
        ],
    }

    results = await engine.run_assessment(context)
    score_data = engine.calculate_compliance_score(results)

    assert "overall_score" in score_data
    assert "total_checks" in score_data
    assert "passed" in score_data
    assert "failed" in score_data
    assert score_data["framework"] == "APRA_CPS_234"
    assert 0 <= score_data["overall_score"] <= 100
