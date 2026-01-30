# Running Tests

## Requirements

The tests use PostgreSQL-specific features (ARRAY, JSONB columns) and require a PostgreSQL database to run.

### Setting Up Test Database

1. Create a test database:
   ```bash
   createdb zhipin_test
   ```

2. Set the test database URL:
   ```bash
   export TEST_DATABASE_URL="postgresql://localhost/zhipin_test"
   ```

3. Run tests:
   ```bash
   cd apps/api
   source venv/bin/activate
   pytest tests/ -v
   ```

### Test Categories

- `test_health.py` - Basic health check endpoints (works with SQLite)
- `test_employers.py` - Employer registration, login, jobs, interviews
- `test_candidates.py` - Candidate registration
- `test_interviews.py` - Interview start, submit, complete
- `test_invites.py` - Invite token management
- `test_questions.py` - Question management
- `test_practice.py` - Practice mode interviews
- `test_bulk_actions.py` - Bulk interview actions, CSV export
- `test_followups.py` - Follow-up question endpoints
- `test_matching.py` - Top candidates, contact candidates
- `test_cache.py` - Redis cache service (unit tests)

### Running with Docker

```bash
# Start test PostgreSQL
docker run --name zhipin-test-db -e POSTGRES_DB=zhipin_test -e POSTGRES_PASSWORD=test -p 5433:5432 -d postgres:15

# Set database URL
export TEST_DATABASE_URL="postgresql://postgres:test@localhost:5433/zhipin_test"

# Run tests
pytest tests/ -v

# Cleanup
docker stop zhipin-test-db && docker rm zhipin-test-db
```

### Test Coverage

Run with coverage report:
```bash
pytest tests/ --cov=app --cov-report=html
```
