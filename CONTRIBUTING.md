# Contributing to ACAGP

First off, thank you for considering contributing to the Australian Compliance Automation & Governance Platform! It's people like you that make ACAGP such a great tool for the compliance community.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Workflow](#development-workflow)
- [Coding Standards](#coding-standards)
- [Testing Requirements](#testing-requirements)
- [Pull Request Process](#pull-request-process)
- [Reporting Bugs](#reporting-bugs)
- [Suggesting Enhancements](#suggesting-enhancements)
- [Community](#community)

## Code of Conduct

This project and everyone participating in it is governed by our [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git
- PostgreSQL 15+ (for local development without Docker)

### Fork and Clone

1. Fork the repository on GitHub
2. Clone your fork locally:
   ```bash
   git clone https://github.com/YOUR_USERNAME/ACAGP.git
   cd ACAGP
   ```

3. Add the upstream repository:
   ```bash
   git remote add upstream https://github.com/ORIGINAL_OWNER/ACAGP.git
   ```

### Local Development Setup

**Using Docker (Recommended):**
```bash
docker-compose up -d
```

**Manual Setup:**
```bash
# Backend
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt  # Development dependencies

# Frontend
cd frontend
npm install
```

## Development Workflow

### 1. Create a Feature Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/bug-description
```

Branch naming conventions:
- `feature/` - New features
- `fix/` - Bug fixes
- `docs/` - Documentation updates
- `refactor/` - Code refactoring
- `test/` - Test additions/improvements
- `chore/` - Maintenance tasks

### 2. Make Your Changes

- Write clear, concise commit messages
- Follow the coding standards (see below)
- Add tests for new functionality
- Update documentation as needed

### 3. Test Your Changes

```bash
# Backend tests
cd backend
pytest -v
pytest --cov=. --cov-report=html

# Frontend tests
cd frontend
npm test
npm run lint

# Integration tests
docker-compose up -d
# Run integration test suite
```

### 4. Commit Your Changes

We follow [Conventional Commits](https://www.conventionalcommits.org/):

```bash
git commit -m "feat: add OAIC breach notification automation"
git commit -m "fix: resolve database connection pool exhaustion"
git commit -m "docs: update API endpoint documentation"
```

Commit types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks
- `perf`: Performance improvements

### 5. Push to Your Fork

```bash
git push origin feature/your-feature-name
```

### 6. Submit a Pull Request

- Go to the original repository on GitHub
- Click "New Pull Request"
- Select your fork and branch
- Fill out the PR template completely
- Link any related issues

## Coding Standards

### Python (Backend)

**Style Guide:** PEP 8 (enforced by Black and flake8)

```bash
# Auto-format code
black .

# Check linting
flake8 .

# Type checking
mypy .

# Import sorting
isort .
```

**Key Standards:**
- Use type hints for all function parameters and return values
- Maximum line length: 100 characters
- Write docstrings for all public modules, functions, classes, and methods
- Use async/await for all I/O operations
- Follow dependency injection patterns

**Example:**
```python
from typing import List, Optional
from uuid import UUID

async def get_assessment_results(
    assessment_id: UUID,
    include_evidence: bool = False
) -> Optional[AssessmentResult]:
    """
    Retrieve assessment results by ID.

    Args:
        assessment_id: UUID of the assessment
        include_evidence: Whether to include evidence artifacts

    Returns:
        AssessmentResult if found, None otherwise

    Raises:
        DatabaseError: If database connection fails
    """
    # Implementation
    pass
```

### TypeScript/React (Frontend)

**Style Guide:** ESLint + Prettier configuration

```bash
# Auto-format
npm run format

# Lint
npm run lint

# Fix linting issues
npm run lint:fix
```

**Key Standards:**
- Use functional components with hooks
- Prefer `const` over `let`
- Use TypeScript interfaces for props
- Avoid `any` type - use proper typing
- Use async/await over promises

**Example:**
```typescript
interface AssessmentCardProps {
  assessment: Assessment;
  onSelect: (id: string) => void;
  isLoading?: boolean;
}

const AssessmentCard: React.FC<AssessmentCardProps> = ({
  assessment,
  onSelect,
  isLoading = false
}) => {
  // Component implementation
};
```

### SQL

- Use uppercase for SQL keywords
- Use snake_case for table and column names
- Always include proper indexes
- Add comments for complex queries

### Git Commit Messages

Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

Example:
```
feat(compliance): add Essential Eight L3 maturity checks

Implement automated checks for maturity level 3 across all 8
Essential Eight mitigation strategies. Includes evidence collection
from Azure Monitor and AWS Config.

Closes #123
```

## Testing Requirements

### Backend Testing

**Required Coverage:** Minimum 80% overall, 90% for core business logic

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html --cov-report=term

# Run specific test file
pytest tests/test_compliance_engine.py -v

# Run tests matching pattern
pytest -k "test_apra" -v
```

**Test Categories:**
- **Unit Tests:** Test individual functions/classes
- **Integration Tests:** Test API endpoints, database interactions
- **Compliance Tests:** Verify compliance check logic
- **Performance Tests:** Ensure <100ms latency for checks

**Writing Tests:**
```python
import pytest
from compliance_engine import APRACPS234Engine

@pytest.mark.asyncio
async def test_mfa_check_with_compliant_users():
    """Test MFA check passes when all users have MFA enabled."""
    engine = APRACPS234Engine()
    context = {
        "aws_iam_users": [
            {"username": "admin1", "is_privileged": True, "mfa_enabled": True},
            {"username": "admin2", "is_privileged": True, "mfa_enabled": True},
        ]
    }

    check = engine.get_check_by_id("CPS234-4-002")
    result = await check.execute(context)

    assert result.status == CheckStatus.PASS
    assert result.remediation_required is False
```

### Frontend Testing

```bash
# Run tests
npm test

# Run with coverage
npm test -- --coverage

# Run in watch mode
npm test -- --watch
```

## Pull Request Process

1. **Before Submitting:**
   - [ ] Code follows style guidelines (Black, flake8, ESLint)
   - [ ] All tests pass locally
   - [ ] New tests added for new functionality
   - [ ] Documentation updated
   - [ ] Changelog entry added (if applicable)
   - [ ] No merge conflicts with main branch

2. **PR Requirements:**
   - Clear, descriptive title
   - Complete description of changes
   - Link to related issues
   - Screenshots/GIFs for UI changes
   - Performance impact assessment (if applicable)

3. **Review Process:**
   - At least one approved review required
   - All CI checks must pass
   - Code owner approval for core modules
   - Squash merge preferred for feature branches

4. **After Merge:**
   - Delete your feature branch
   - Update your local main branch
   - Close related issues

## Reporting Bugs

**Before Submitting:**
- Check existing issues to avoid duplicates
- Verify bug exists in latest version
- Collect debug information

**Bug Report Template:**
```markdown
**Description:**
Clear description of the bug

**To Reproduce:**
1. Go to '...'
2. Click on '...'
3. See error

**Expected Behavior:**
What should happen

**Actual Behavior:**
What actually happens

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python Version: [e.g., 3.11.2]
- Docker Version: [e.g., 24.0.6]
- Browser: [e.g., Chrome 120]

**Logs:**
```
Paste relevant logs here
```

**Screenshots:**
If applicable
```

## Suggesting Enhancements

**Enhancement Proposal Template:**
```markdown
**Problem Statement:**
What problem does this solve?

**Proposed Solution:**
How should it work?

**Alternatives Considered:**
What other approaches were considered?

**Impact:**
- Performance impact?
- Breaking changes?
- Migration required?

**Implementation Plan:**
High-level steps to implement
```

## Development Tips

### Running Compliance Checks Locally

```bash
# Example: Test APRA CPS 234 check
python -c "
import asyncio
from compliance_engine import APRACPS234Engine

async def test():
    engine = APRACPS234Engine()
    context = {...}  # Your test context
    results = await engine.run_assessment(context)
    print(results)

asyncio.run(test())
"
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Add new compliance framework"

# Apply migrations
alembic upgrade head

# Rollback
alembic downgrade -1
```

### Debugging

```bash
# Backend debugging with pdb
import pdb; pdb.set_trace()

# View logs
docker-compose logs -f backend

# Database queries
docker-compose exec postgres psql -U postgres -d acagp
```

## Community

- **Discussions:** GitHub Discussions for questions and ideas
- **Issues:** GitHub Issues for bugs and feature requests
- **Security:** See [SECURITY.md](SECURITY.md) for security vulnerabilities

## Recognition

Contributors are recognized in:
- README.md Contributors section
- Release notes for significant contributions
- Annual contributor acknowledgments

## Questions?

Feel free to ask questions by:
- Opening a GitHub Discussion
- Commenting on relevant issues
- Reaching out to maintainers

Thank you for contributing to making compliance automation better for everyone! 🚀
