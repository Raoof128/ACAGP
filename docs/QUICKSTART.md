# Quick Start Guide

## Prerequisites

- **Docker** and **Docker Compose** (recommended for quickest setup)
- **Python 3.11+** (for local development)
- **Node.js 18+** (for frontend development)
- **PostgreSQL 15+** with TimescaleDB (if not using Docker)

## Option 1: Docker Compose (Recommended)

This is the fastest way to get ACAGP running locally.

### 1. Clone the repository

```bash
git clone <repository-url>
cd ACAGP
```

### 2. Start all services

```bash
docker-compose up -d
```

This will start:
- PostgreSQL with TimescaleDB (port 5432)
- Redis (port 6379)
- FastAPI backend (port 8000)
- Celery worker
- React frontend (port 3000)
- Prometheus (port 9090)
- Grafana (port 3001)

### 3. Access the platform

- **Frontend**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **API**: http://localhost:8000/api/v1
- **Grafana Dashboards**: http://localhost:3001 (admin/admin)
- **Prometheus**: http://localhost:9090

### 4. Initialize database (first time only)

```bash
# Run from project root
docker-compose exec backend alembic upgrade head
```

### 5. View logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend
```

### 6. Stop services

```bash
docker-compose down

# To remove volumes as well
docker-compose down -v
```

---

## Option 2: Local Development Setup

### Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env

# Edit .env with your database credentials
nano .env

# Initialize database
psql -U postgres -c "CREATE DATABASE acagp;"
psql -U postgres -d acagp -f ../database/schemas/init.sql

# Run migrations
alembic upgrade head

# Start backend server
uvicorn main:app --reload --port 8000
```

Backend will be available at: http://localhost:8000

### Frontend Setup

```bash
cd frontend

# Install dependencies
npm install

# Start development server
npm start
```

Frontend will be available at: http://localhost:3000

---

## Testing the Platform

### 1. Create an organization

```bash
curl -X POST "http://localhost:8000/api/v1/organizations/" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Demo Bank Pty Ltd",
    "industry": "Financial Services",
    "abn": "12345678901",
    "regulatory_body": "APRA",
    "risk_tier": "HIGH",
    "contact_email": "compliance@demobank.com.au",
    "city": "Sydney",
    "state": "NSW",
    "postcode": "2000"
  }'
```

### 2. List compliance frameworks

```bash
curl "http://localhost:8000/api/v1/compliance/frameworks"
```

### 3. Run APRA CPS 234 assessment

```bash
curl -X POST "http://localhost:8000/api/v1/compliance/assess/APRA_CPS_234?organization_id=<org-id>"
```

Replace `<org-id>` with the ID from step 1.

### 4. View assessment results

The response will include:
- Overall compliance score
- Controls passed/failed
- Critical findings
- Detailed results for each check
- Remediation guidance

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_compliance_engine.py -v

# Run tests matching pattern
pytest -k "test_apra" -v
```

### Frontend Tests

```bash
cd frontend

# Run tests
npm test

# Run with coverage
npm test -- --coverage
```

---

## Database Management

### Using Alembic for Migrations

```bash
cd backend

# Create new migration
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# View migration history
alembic history
```

### Direct SQL Access

```bash
# Docker
docker-compose exec postgres psql -U postgres -d acagp

# Local
psql -U postgres -d acagp
```

Useful queries:
```sql
-- List organizations
SELECT id, name, regulatory_body, risk_tier FROM organizations;

-- List frameworks
SELECT code, name, version, issuing_authority FROM compliance_frameworks;

-- View recent assessments
SELECT id, status, overall_score, created_at
FROM compliance_assessments
ORDER BY created_at DESC
LIMIT 10;

-- Compliance event statistics
SELECT event_type, count(*)
FROM compliance_events
WHERE time > now() - interval '24 hours'
GROUP BY event_type;
```

---

## Troubleshooting

### Port already in use

If port 8000 or 3000 is already in use:

```bash
# Check what's using the port
lsof -i :8000  # macOS/Linux
netstat -ano | findstr :8000  # Windows

# Kill the process or change ports in docker-compose.yml
```

### Database connection errors

```bash
# Check if PostgreSQL is running
docker-compose ps postgres

# View PostgreSQL logs
docker-compose logs postgres

# Restart database
docker-compose restart postgres
```

### Backend import errors

```bash
# Ensure you're in the backend directory
cd backend

# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Frontend npm errors

```bash
# Clear npm cache
npm cache clean --force

# Remove node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

---

## Next Steps

1. **Explore API Documentation**: Visit http://localhost:8000/docs for interactive API docs
2. **Run Compliance Assessments**: Test APRA CPS 234 checks with your data
3. **Configure Cloud Integration**: Add AWS/Azure credentials for real data ingestion
4. **Customize Checks**: Extend compliance engine with organization-specific controls
5. **Build Dashboard**: Create React components for compliance visualization

---

## Development Workflow

### Adding New Compliance Checks

1. Create check class in `backend/compliance_engine/apra_cps234.py`
2. Add check to engine's `_initialize_checks()` method
3. Write tests in `backend/tests/test_compliance_engine.py`
4. Run tests: `pytest tests/test_compliance_engine.py -v`

### Adding New API Endpoints

1. Create route in `backend/api/v1/` directory
2. Add router to `backend/api/v1/__init__.py`
3. Test with interactive docs at `/docs`
4. Write integration tests

### Database Schema Changes

1. Modify models in `backend/models/`
2. Generate migration: `alembic revision --autogenerate -m "Description"`
3. Review migration in `database/migrations/versions/`
4. Apply: `alembic upgrade head`

---

## Support

- **Documentation**: See `/docs` directory
- **API Reference**: http://localhost:8000/docs
- **Issues**: GitHub Issues
- **Email**: support@example.com
