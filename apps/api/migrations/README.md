# Database Migrations

This directory contains Alembic database migrations for Pathway.

## Quick Commands

```bash
# Create a new migration (after changing models)
alembic revision --autogenerate -m "Description of changes"

# Apply all pending migrations
alembic upgrade head

# Rollback one migration
alembic downgrade -1

# Rollback all migrations
alembic downgrade base

# Show current migration version
alembic current

# Show migration history
alembic history
```

## Initial Setup (New Database)

If starting with a fresh database:

```bash
cd apps/api
alembic upgrade head
```

## Existing Database (Already has tables)

If your database already has tables from SQLAlchemy auto-create:

```bash
# Mark the initial migration as already applied
alembic stamp 001
```

## Creating New Migrations

After modifying models in `app/models/`:

```bash
# Generate migration automatically
alembic revision --autogenerate -m "Add new_field to candidates"

# Review the generated migration in migrations/versions/
# Then apply it
alembic upgrade head
```

## Best Practices

1. Always review auto-generated migrations before applying
2. Test migrations on a copy of production data first
3. Keep migrations small and focused
4. Never edit migrations that have been applied to production
5. Use descriptive migration messages
