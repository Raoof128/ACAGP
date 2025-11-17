# ACAGP Architecture Documentation

## Table of Contents

- [System Overview](#system-overview)
- [Architecture Diagrams](#architecture-diagrams)
- [Component Details](#component-details)
- [Data Flow](#data-flow)
- [Security Architecture](#security-architecture)
- [Scalability Considerations](#scalability-considerations)
- [Technology Stack](#technology-stack)

## System Overview

The Australian Compliance Automation & Governance Platform (ACAGP) is designed as a microservices-based, event-driven system for automating compliance monitoring across Australian regulatory frameworks.

### Design Principles

1. **Separation of Concerns**: Clear boundaries between data ingestion, processing, storage, and presentation
2. **Async-First**: All I/O operations use async/await for maximum concurrency
3. **Event-Driven**: Compliance events trigger assessments and notifications
4. **Extensible**: Plugin architecture for new compliance frameworks
5. **Audit-Ready**: Immutable audit trails for all compliance activities
6. **Cloud-Native**: Designed for containerized deployment on Kubernetes

## Architecture Diagrams

### High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         EXTERNAL SYSTEMS                         │
│  AWS CloudTrail │ Azure Monitor │ Splunk │ K8s Audit │ AD/Entra │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                     DATA INGESTION LAYER                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ AWS Collector│  │Azure Collector│  │ SIEM Collector│          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         └──────────────────┼──────────────────┘                  │
│                            ▼                                      │
│                   ┌─────────────────┐                            │
│                   │  Kafka / Redis  │                            │
│                   │  Event Stream   │                            │
│                   └────────┬────────┘                            │
└────────────────────────────┼─────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                     PROCESSING LAYER                             │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │                 Compliance Rules Engine                    │  │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  │  │
│  │  │APRA CPS  │  │Essential │  │   OAIC   │  │ PCI DSS  │  │  │
│  │  │   234    │  │  Eight   │  │   NDB    │  │   4.0    │  │  │
│  │  └──────────┘  └──────────┘  └──────────┘  └──────────┘  │  │
│  └───────────────────────────────────────────────────────────┘  │
│                            │                                      │
│                            ▼                                      │
│              ┌──────────────────────────┐                        │
│              │  Assessment Orchestrator  │                        │
│              │    (Celery Workers)      │                        │
│              └────────────┬─────────────┘                        │
└───────────────────────────┼──────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                      DATA PERSISTENCE LAYER                      │
│  ┌─────────────────────┐         ┌──────────────────────┐       │
│  │   PostgreSQL 15     │         │    TimescaleDB       │       │
│  │  (Compliance Data)  │◄────────┤  (Time-Series Events)│       │
│  └─────────────────────┘         └──────────────────────┘       │
│  ┌─────────────────────┐         ┌──────────────────────┐       │
│  │  S3 / Azure Blob    │         │     Redis Cache      │       │
│  │ (Evidence Artifacts)│         │  (Session & Queue)   │       │
│  └─────────────────────┘         └──────────────────────┘       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                      APPLICATION LAYER                           │
│  ┌─────────────────────┐         ┌──────────────────────┐       │
│  │   FastAPI Backend   │◄────────┤   React Frontend     │       │
│  │   (REST API)        │         │   (TypeScript)       │       │
│  └─────────────────────┘         └──────────────────────┘       │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MONITORING & OBSERVABILITY                     │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐        │
│  │Prometheus│  │ Grafana  │  │  Sentry  │  │CloudWatch│        │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘        │
└─────────────────────────────────────────────────────────────────┘
```

### Data Flow Diagram

```
┌────────────┐
│ Cloud      │
│ Providers  │
└─────┬──────┘
      │ 1. Collect Events
      ▼
┌────────────┐
│ Ingestor   │
└─────┬──────┘
      │ 2. Normalize & Enrich
      ▼
┌────────────┐
│   Kafka    │
└─────┬──────┘
      │ 3. Stream Events
      ▼
┌────────────────────┐
│ Compliance Engine  │◄──── 4. Fetch Rules
└─────┬──────────────┘
      │ 5. Execute Checks
      ▼
┌────────────┐     ┌─────────────┐
│  Database  │◄────┤   Results   │
└────────────┘     └─────────────┘
      │                   │
      │ 6. Store          │ 7. Notify
      ▼                   ▼
┌────────────┐     ┌─────────────┐
│   Report   │     │   Alerts    │
│ Generator  │     │   System    │
└────────────┘     └─────────────┘
```

## Component Details

### 1. Data Ingestion Layer

**Purpose**: Collect security and compliance data from various sources

**Components**:
- **AWS Collector**: CloudTrail, Config, GuardDuty, Security Hub
- **Azure Collector**: Activity Log, Defender for Cloud, Monitor
- **SIEM Collector**: Splunk, Elastic, Azure Sentinel connectors
- **K8s Audit Collector**: Kubernetes audit logs
- **Identity Collector**: Active Directory, Entra ID logs

**Technology**:
- Python async clients (aioboto3, azure-sdk)
- Rate limiting and retry logic
- Error handling and dead-letter queues

**Performance**:
- Target: 10,000+ events/second
- Batch processing: 100-1000 events per batch
- Latency: <5 seconds from source to queue

### 2. Event Streaming

**Purpose**: Decouple data collection from processing

**Components**:
- **Kafka**: Primary event stream (production)
- **Redis Streams**: Alternative for smaller deployments
- **Message Schema**: Protobuf or JSON with versioning

**Topics**:
- `compliance.events.raw` - Raw events from sources
- `compliance.events.normalized` - Processed events
- `compliance.assessments.triggered` - Assessment requests
- `compliance.findings.critical` - High-priority findings

### 3. Compliance Rules Engine

**Purpose**: Execute compliance checks against normalized data

**Architecture**:
```python
class ComplianceCheck(ABC):
    @abstractmethod
    async def execute(context: Dict) -> CheckResult:
        pass

class APRACPS234Engine(ComplianceRuleEngine):
    def _initialize_checks(self):
        self.checks = [
            CPS234_1_CISOAppointed(),
            CPS234_1_PolicyDocumented(),
            # ... 50+ checks
        ]
```

**Check Execution Flow**:
1. Receive assessment request
2. Load organization context
3. Execute applicable checks in parallel
4. Collect evidence artifacts
5. Calculate compliance score
6. Generate findings
7. Store results
8. Trigger notifications if needed

**Performance Optimization**:
- Async/await for I/O operations
- Parallel check execution
- Caching of static data (policies, configs)
- Connection pooling

### 4. Assessment Orchestrator

**Purpose**: Manage long-running compliance assessments

**Technology**: Celery with Redis backend

**Task Types**:
- `run_full_assessment(org_id, framework_code)`
- `run_continuous_monitoring(org_id)`
- `generate_audit_report(assessment_id)`
- `auto_remediate(finding_id)`

**Task Priority Levels**:
1. Critical findings (P0) - Immediate
2. High-priority assessments (P1) - <5 min
3. Scheduled assessments (P2) - <15 min
4. Report generation (P3) - <30 min

### 5. Data Persistence

**PostgreSQL Schema Design**:

```sql
Organizations (1) ──┐
                    │
                    ├──< Users (N)
                    │
                    ├──< Compliance Assessments (N)
                    │    │
                    │    └──< Assessment Results (N)
                    │         │
                    │         └──< Evidence Artifacts (N)
                    │
                    ├──< Remediation Tasks (N)
                    │
                    ├──< Compliance Exceptions (N)
                    │
                    └──< Breach Notifications (N)

Compliance Frameworks (1) ──< Compliance Controls (N)
                              │
                              └──< Assessment Results (N)
```

**TimescaleDB for Time-Series**:
- Compliance events hypertable
- Automatic partitioning by time
- Compression for old data (>90 days)
- Retention policy (7 years for APRA)

### 6. API Layer (FastAPI)

**Endpoints Structure**:
```
/api/v1/
  ├── /compliance/
  │   ├── GET  /frameworks
  │   ├── GET  /frameworks/{code}/controls
  │   ├── POST /assess/{framework_code}
  │   └── GET  /score/{org_id}
  ├── /assessments/
  │   ├── GET  /
  │   ├── GET  /{id}
  │   ├── GET  /{id}/results
  │   └── POST /{id}/rerun
  ├── /organizations/
  │   ├── GET    /
  │   ├── POST   /
  │   ├── GET    /{id}
  │   ├── PATCH  /{id}
  │   └── DELETE /{id}
  ├── /reports/
  │   ├── GET  /
  │   ├── POST /generate
  │   └── GET  /{id}/download
  └── /remediation/
      ├── GET   /tasks
      ├── POST  /tasks
      ├── PATCH /tasks/{id}
      └── POST  /tasks/{id}/auto-remediate
```

**Authentication**: JWT tokens with role-based access control (RBAC)

**Rate Limiting**:
- Unauthenticated: 10 req/min
- Authenticated: 100 req/min
- Admin: 1000 req/min

### 7. Frontend (React)

**Component Architecture**:
```
App
├── DashboardPage
│   ├── ComplianceScoreCard
│   ├── FrameworksTable
│   └── RecentAssessments
├── AssessmentDetailPage
│   ├── AssessmentHeader
│   ├── ControlResults
│   └── EvidenceViewer
├── OrganizationsPage
│   ├── OrgList
│   └── OrgDetail
└── ReportsPage
    ├── ReportList
    └── ReportGenerator
```

**State Management**:
- React Context for global state
- React Query for server state
- Local state for UI-only concerns

## Security Architecture

### Authentication & Authorization

**Authentication Flow**:
1. User logs in with email/password
2. Backend validates credentials
3. JWT token issued (30 min expiry)
4. Refresh token issued (7 days expiry)
5. Client stores tokens securely
6. API requests include JWT in Authorization header

**Authorization Levels**:
- **ADMIN**: Full system access
- **COMPLIANCE_OFFICER**: Run assessments, view reports
- **AUDITOR**: Read-only access to assessments/reports
- **VIEWER**: Basic dashboard access

**Security Controls**:
- Password hashing: bcrypt with 12 rounds
- JWT signing: HS256 with rotated secrets
- API rate limiting: Per-user and per-IP
- Input validation: Pydantic models
- SQL injection prevention: Parameterized queries
- XSS prevention: CSP headers, input sanitization
- CSRF protection: SameSite cookies, CSRF tokens

### Network Security

```
Internet
   │
   ▼
┌─────────────────┐
│   CloudFlare    │ ◄── DDoS Protection, WAF
│   (CDN/WAF)     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Load Balancer  │ ◄── SSL Termination, Health Checks
│   (ALB/AGIC)    │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Kubernetes     │
│  Ingress        │
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌────────┐ ┌────────┐
│Backend │ │Frontend│ ◄── Private VPC, Security Groups
│ Pods   │ │  Pods  │
└───┬────┘ └────────┘
    │
    ▼
┌─────────────────┐
│   Database      │ ◄── Private Subnet, Encryption at Rest
│  (RDS/Postgres) │
└─────────────────┘
```

### Data Protection

**Encryption**:
- **At Rest**: AES-256 for database, S3 buckets
- **In Transit**: TLS 1.3 for all connections
- **Application**: Field-level encryption for sensitive data

**Data Classification**:
- **Public**: Framework descriptions, public docs
- **Internal**: Organization names, assessment scores
- **Confidential**: User credentials, compliance findings
- **Restricted**: Evidence artifacts, breach notifications

**Audit Logging**:
All actions logged with:
- User ID
- Action performed
- Resource accessed
- Timestamp (UTC)
- Source IP
- Result (success/failure)

Retention: 7 years (APRA requirement)

## Scalability Considerations

### Horizontal Scaling

**Stateless Services** (auto-scale based on CPU/memory):
- FastAPI backend: 2-20 pods
- Celery workers: 5-50 workers
- Frontend: 2-10 pods

**Stateful Services** (manual scaling):
- PostgreSQL: Read replicas for reporting
- Redis: Cluster mode with sharding
- TimescaleDB: Partitioning by time

### Performance Optimization

**Database**:
- Connection pooling (20-100 connections)
- Read replicas for reporting queries
- Materialized views for dashboards
- Indexes on foreign keys and query columns
- Partitioning for large tables

**Caching Strategy**:
- Redis for session data (TTL: 30 min)
- API response caching (TTL: 1-5 min)
- Static framework data (TTL: 24 hours)
- CDN caching for frontend assets

**Async Processing**:
- Celery for long-running tasks
- Kafka for event streaming
- Async I/O for all database queries
- Parallel execution of compliance checks

### Capacity Planning

**Expected Load** (per 1000 organizations):
- API requests: 10,000 req/min
- Database queries: 50,000 queries/min
- Events ingested: 100,000 events/min
- Assessments/day: 10,000
- Reports/day: 1,000

**Resource Estimates**:
- Backend pods: 10-20 (2 CPU, 4GB RAM each)
- Workers: 20-50 (1 CPU, 2GB RAM each)
- Database: r6g.2xlarge (8 vCPU, 64GB RAM)
- Redis: r6g.large (2 vCPU, 16GB RAM)
- Storage: 500GB - 5TB (depending on retention)

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Framework**: FastAPI 0.104+
- **ORM**: SQLAlchemy 2.0 (async)
- **Migration**: Alembic
- **Task Queue**: Celery
- **Validation**: Pydantic v2

### Frontend
- **Language**: TypeScript 5.3+
- **Framework**: React 18
- **Build Tool**: Webpack / Vite
- **State**: React Query + Context
- **UI Library**: Material-UI / Tailwind

### Database
- **Primary**: PostgreSQL 15
- **Time-Series**: TimescaleDB
- **Cache**: Redis 7
- **Object Storage**: S3 / Azure Blob

### Infrastructure
- **Containers**: Docker
- **Orchestration**: Kubernetes
- **IaC**: Terraform
- **CI/CD**: GitHub Actions
- **Monitoring**: Prometheus + Grafana

### Cloud Providers
- **AWS**: EKS, RDS, S3, CloudWatch
- **Azure**: AKS, PostgreSQL, Blob, Monitor
- **Multi-Cloud**: Cloud-agnostic design

---

**Last Updated**: 2025-01-16
**Version**: 1.0.0
**Authors**: ACAGP Team
