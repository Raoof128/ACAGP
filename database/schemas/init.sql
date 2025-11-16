-- Australian Compliance Automation & Governance Platform (ACAGP)
-- PostgreSQL Database Schema Initialization
-- Requires: PostgreSQL 15+ with TimescaleDB extension

-- Create database (run as superuser)
-- CREATE DATABASE acagp OWNER postgres;

-- Connect to the database
\c acagp;

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- For text search
CREATE EXTENSION IF NOT EXISTS "btree_gin"; -- For index optimization

-- Set timezone
SET timezone = 'Australia/Sydney';

-- ============================================================================
-- ORGANIZATIONS & USERS
-- ============================================================================

CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) NOT NULL,
    industry VARCHAR(100),
    abn VARCHAR(11) UNIQUE,  -- Australian Business Number
    regulatory_body VARCHAR(100),  -- APRA, ASIC, OAIC, etc.
    risk_tier VARCHAR(20) CHECK (risk_tier IN ('LOW', 'MEDIUM', 'HIGH', 'CRITICAL')),
    contact_email VARCHAR(255),
    contact_phone VARCHAR(20),
    address_line1 VARCHAR(255),
    address_line2 VARCHAR(255),
    city VARCHAR(100),
    state VARCHAR(3),  -- NSW, VIC, QLD, etc.
    postcode VARCHAR(4),
    country VARCHAR(2) DEFAULT 'AU',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    deleted_at TIMESTAMP WITH TIME ZONE
);

CREATE INDEX idx_organizations_abn ON organizations(abn);
CREATE INDEX idx_organizations_regulatory_body ON organizations(regulatory_body);
CREATE INDEX idx_organizations_risk_tier ON organizations(risk_tier);
CREATE INDEX idx_organizations_metadata ON organizations USING GIN (metadata);


CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    role VARCHAR(50) CHECK (role IN ('ADMIN', 'COMPLIANCE_OFFICER', 'AUDITOR', 'VIEWER')),
    is_active BOOLEAN DEFAULT true,
    is_superuser BOOLEAN DEFAULT false,
    last_login TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_users_organization_id ON users(organization_id);
CREATE INDEX idx_users_role ON users(role);


-- ============================================================================
-- COMPLIANCE FRAMEWORKS
-- ============================================================================

CREATE TABLE compliance_frameworks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code VARCHAR(50) UNIQUE NOT NULL,  -- APRA_CPS_234, ESSENTIAL_EIGHT, etc.
    name VARCHAR(255) NOT NULL,
    description TEXT,
    version VARCHAR(20),
    issuing_authority VARCHAR(100),  -- APRA, ASD, OAIC, etc.
    effective_date DATE,
    jurisdiction VARCHAR(50) DEFAULT 'Australia',
    is_active BOOLEAN DEFAULT true,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_frameworks_code ON compliance_frameworks(code);
CREATE INDEX idx_frameworks_authority ON compliance_frameworks(issuing_authority);


CREATE TABLE compliance_controls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    framework_id UUID REFERENCES compliance_frameworks(id) ON DELETE CASCADE,
    control_id VARCHAR(100) NOT NULL,  -- e.g., CPS 234.1, E8-M1-APP-01
    parent_control_id UUID REFERENCES compliance_controls(id),
    name VARCHAR(255) NOT NULL,
    description TEXT,
    control_type VARCHAR(50) CHECK (control_type IN ('PREVENTIVE', 'DETECTIVE', 'CORRECTIVE', 'COMPENSATING')),
    severity VARCHAR(20) CHECK (severity IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO')),
    automated_check_available BOOLEAN DEFAULT false,
    maturity_level INTEGER CHECK (maturity_level BETWEEN 0 AND 3),  -- For Essential Eight
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(framework_id, control_id)
);

CREATE INDEX idx_controls_framework ON compliance_controls(framework_id);
CREATE INDEX idx_controls_control_id ON compliance_controls(control_id);
CREATE INDEX idx_controls_severity ON compliance_controls(severity);
CREATE INDEX idx_controls_automated ON compliance_controls(automated_check_available);


-- ============================================================================
-- COMPLIANCE ASSESSMENTS
-- ============================================================================

CREATE TABLE compliance_assessments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    framework_id UUID REFERENCES compliance_frameworks(id) ON DELETE CASCADE,
    assessment_type VARCHAR(50) CHECK (assessment_type IN ('FULL', 'PARTIAL', 'CONTINUOUS', 'AUDIT')),
    status VARCHAR(50) CHECK (status IN ('PENDING', 'IN_PROGRESS', 'COMPLETED', 'FAILED', 'CANCELLED')),
    overall_score DECIMAL(5, 2),  -- Percentage 0-100
    controls_passed INTEGER DEFAULT 0,
    controls_failed INTEGER DEFAULT 0,
    controls_not_applicable INTEGER DEFAULT 0,
    critical_findings INTEGER DEFAULT 0,
    high_findings INTEGER DEFAULT 0,
    medium_findings INTEGER DEFAULT 0,
    low_findings INTEGER DEFAULT 0,
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    conducted_by UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_assessments_org ON compliance_assessments(organization_id);
CREATE INDEX idx_assessments_framework ON compliance_assessments(framework_id);
CREATE INDEX idx_assessments_status ON compliance_assessments(status);
CREATE INDEX idx_assessments_score ON compliance_assessments(overall_score);
CREATE INDEX idx_assessments_created ON compliance_assessments(created_at DESC);


CREATE TABLE assessment_results (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES compliance_assessments(id) ON DELETE CASCADE,
    control_id UUID REFERENCES compliance_controls(id) ON DELETE CASCADE,
    status VARCHAR(50) CHECK (status IN ('PASS', 'FAIL', 'NOT_APPLICABLE', 'MANUAL_REVIEW', 'COMPENSATING_CONTROL')),
    evidence_collected JSONB DEFAULT '[]',  -- Array of evidence artifacts
    findings TEXT,
    remediation_required BOOLEAN DEFAULT false,
    remediation_priority VARCHAR(20) CHECK (remediation_priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    remediation_deadline DATE,
    tested_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    tested_by UUID REFERENCES users(id),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_results_assessment ON assessment_results(assessment_id);
CREATE INDEX idx_results_control ON assessment_results(control_id);
CREATE INDEX idx_results_status ON assessment_results(status);
CREATE INDEX idx_results_remediation ON assessment_results(remediation_required);


-- ============================================================================
-- EVIDENCE & AUDIT TRAILS
-- ============================================================================

CREATE TABLE evidence_artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_result_id UUID REFERENCES assessment_results(id) ON DELETE CASCADE,
    artifact_type VARCHAR(100),  -- LOG, SCREENSHOT, CONFIG, POLICY_DOC, etc.
    source_system VARCHAR(100),  -- AWS_CLOUDTRAIL, AZURE_MONITOR, SPLUNK, etc.
    artifact_url TEXT,
    artifact_hash VARCHAR(64),  -- SHA-256 hash for integrity
    collected_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_evidence_assessment ON evidence_artifacts(assessment_result_id);
CREATE INDEX idx_evidence_type ON evidence_artifacts(artifact_type);
CREATE INDEX idx_evidence_source ON evidence_artifacts(source_system);


-- ============================================================================
-- COMPLIANCE EVENTS (TimescaleDB Hypertable)
-- ============================================================================

CREATE TABLE compliance_events (
    time TIMESTAMP WITH TIME ZONE NOT NULL,
    event_id UUID DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id),
    framework_code VARCHAR(50),
    control_id VARCHAR(100),
    event_type VARCHAR(100),  -- CHECK_EXECUTED, COMPLIANCE_DRIFT, BREACH_DETECTED, etc.
    severity VARCHAR(20),
    source_system VARCHAR(100),
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Convert to TimescaleDB hypertable for time-series optimization
SELECT create_hypertable('compliance_events', 'time');

-- Create indexes on hypertable
CREATE INDEX idx_events_org ON compliance_events(organization_id, time DESC);
CREATE INDEX idx_events_framework ON compliance_events(framework_code, time DESC);
CREATE INDEX idx_events_type ON compliance_events(event_type, time DESC);
CREATE INDEX idx_events_severity ON compliance_events(severity, time DESC);


-- ============================================================================
-- REMEDIATION TRACKING
-- ============================================================================

CREATE TABLE remediation_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_result_id UUID REFERENCES assessment_results(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    priority VARCHAR(20) CHECK (priority IN ('CRITICAL', 'HIGH', 'MEDIUM', 'LOW')),
    status VARCHAR(50) CHECK (status IN ('OPEN', 'IN_PROGRESS', 'BLOCKED', 'COMPLETED', 'CANCELLED')),
    assigned_to UUID REFERENCES users(id),
    due_date DATE,
    estimated_effort_hours INTEGER,
    actual_effort_hours INTEGER,
    auto_remediation_available BOOLEAN DEFAULT false,
    auto_remediation_script TEXT,
    completed_at TIMESTAMP WITH TIME ZONE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_remediation_assessment ON remediation_tasks(assessment_result_id);
CREATE INDEX idx_remediation_org ON remediation_tasks(organization_id);
CREATE INDEX idx_remediation_status ON remediation_tasks(status);
CREATE INDEX idx_remediation_priority ON remediation_tasks(priority);
CREATE INDEX idx_remediation_due_date ON remediation_tasks(due_date);


-- ============================================================================
-- EXCEPTION MANAGEMENT
-- ============================================================================

CREATE TABLE compliance_exceptions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    control_id UUID REFERENCES compliance_controls(id) ON DELETE CASCADE,
    exception_type VARCHAR(50) CHECK (exception_type IN ('TEMPORARY', 'PERMANENT', 'RISK_ACCEPTED')),
    justification TEXT NOT NULL,
    compensating_controls TEXT,
    approved_by UUID REFERENCES users(id),
    approved_at TIMESTAMP WITH TIME ZONE,
    valid_from DATE NOT NULL,
    valid_until DATE,
    review_frequency_days INTEGER DEFAULT 90,
    next_review_date DATE,
    status VARCHAR(50) CHECK (status IN ('PENDING', 'APPROVED', 'REJECTED', 'EXPIRED', 'REVOKED')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_exceptions_org ON compliance_exceptions(organization_id);
CREATE INDEX idx_exceptions_control ON compliance_exceptions(control_id);
CREATE INDEX idx_exceptions_status ON compliance_exceptions(status);
CREATE INDEX idx_exceptions_review_date ON compliance_exceptions(next_review_date);


-- ============================================================================
-- AUDIT REPORTS
-- ============================================================================

CREATE TABLE audit_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    assessment_id UUID REFERENCES compliance_assessments(id) ON DELETE CASCADE,
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    report_type VARCHAR(50) CHECK (report_type IN ('COMPLIANCE', 'AUDIT', 'BOARD', 'REGULATORY')),
    framework_code VARCHAR(50),
    title VARCHAR(255) NOT NULL,
    report_period_start DATE,
    report_period_end DATE,
    file_path TEXT,
    file_format VARCHAR(10) DEFAULT 'PDF',
    file_size_bytes BIGINT,
    generated_by UUID REFERENCES users(id),
    generated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_reports_assessment ON audit_reports(assessment_id);
CREATE INDEX idx_reports_org ON audit_reports(organization_id);
CREATE INDEX idx_reports_type ON audit_reports(report_type);
CREATE INDEX idx_reports_framework ON audit_reports(framework_code);


-- ============================================================================
-- BREACH NOTIFICATIONS (OAIC)
-- ============================================================================

CREATE TABLE breach_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,
    incident_id VARCHAR(100) UNIQUE,
    breach_type VARCHAR(100),
    affected_individuals_count INTEGER,
    data_types_compromised TEXT[],
    breach_date DATE NOT NULL,
    discovered_date DATE NOT NULL,
    notification_required BOOLEAN DEFAULT false,
    oaic_notified BOOLEAN DEFAULT false,
    oaic_notification_date TIMESTAMP WITH TIME ZONE,
    individuals_notified BOOLEAN DEFAULT false,
    notification_method VARCHAR(100),
    remediation_actions TEXT,
    status VARCHAR(50) CHECK (status IN ('DETECTED', 'ASSESSING', 'NOTIFIED', 'REMEDIATED', 'CLOSED')),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_breaches_org ON breach_notifications(organization_id);
CREATE INDEX idx_breaches_status ON breach_notifications(status);
CREATE INDEX idx_breaches_notification_required ON breach_notifications(notification_required);
CREATE INDEX idx_breaches_oaic_notified ON breach_notifications(oaic_notified);


-- ============================================================================
-- TRIGGERS FOR UPDATED_AT
-- ============================================================================

CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON users
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_frameworks_updated_at BEFORE UPDATE ON compliance_frameworks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_controls_updated_at BEFORE UPDATE ON compliance_controls
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_assessments_updated_at BEFORE UPDATE ON compliance_assessments
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_remediation_updated_at BEFORE UPDATE ON remediation_tasks
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_exceptions_updated_at BEFORE UPDATE ON compliance_exceptions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_breaches_updated_at BEFORE UPDATE ON breach_notifications
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();


-- ============================================================================
-- VIEWS FOR REPORTING
-- ============================================================================

CREATE OR REPLACE VIEW v_compliance_dashboard AS
SELECT
    o.id AS organization_id,
    o.name AS organization_name,
    cf.code AS framework_code,
    cf.name AS framework_name,
    COUNT(DISTINCT ca.id) AS total_assessments,
    AVG(ca.overall_score) AS average_score,
    SUM(ca.controls_passed) AS total_controls_passed,
    SUM(ca.controls_failed) AS total_controls_failed,
    SUM(ca.critical_findings) AS total_critical_findings,
    MAX(ca.completed_at) AS last_assessment_date
FROM organizations o
LEFT JOIN compliance_assessments ca ON o.id = ca.organization_id
LEFT JOIN compliance_frameworks cf ON ca.framework_id = cf.id
WHERE ca.status = 'COMPLETED'
GROUP BY o.id, o.name, cf.code, cf.name;


-- ============================================================================
-- INITIAL DATA (Frameworks & Controls)
-- ============================================================================

-- Insert compliance frameworks
INSERT INTO compliance_frameworks (code, name, description, version, issuing_authority, effective_date) VALUES
('APRA_CPS_234', 'APRA Prudential Standard CPS 234', 'Information Security for APRA-regulated entities', '2019', 'APRA', '2019-07-01'),
('ESSENTIAL_EIGHT', 'ASD Essential Eight Maturity Model', 'Strategies to mitigate cyber security incidents', '2023', 'Australian Signals Directorate', '2023-01-01'),
('OAIC_NDB', 'OAIC Notifiable Data Breaches Scheme', 'Privacy Act 1988 breach notification requirements', '2018', 'OAIC', '2018-02-22'),
('PCI_DSS', 'Payment Card Industry Data Security Standard', 'Security standards for card payment processing', '4.0', 'PCI SSC', '2024-03-31'),
('ISO_27001', 'ISO/IEC 27001:2022', 'Information security management systems', '2022', 'ISO/IEC', '2022-10-25');

-- Commit changes
COMMIT;

-- Success message
\echo 'Database schema initialized successfully!'
\echo 'TimescaleDB extension enabled for compliance_events table'
\echo 'Run seed data scripts to populate with sample compliance controls'
