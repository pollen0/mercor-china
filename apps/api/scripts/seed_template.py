#!/usr/bin/env python3
"""
TEMPLATE: Seed intern jobs from a VC firm's job board.

INSTRUCTIONS FOR CLAUDE CODE AGENTS:
1. Copy this file to: seed_[SCRIPT_ID]_jobs.py
2. Replace [SCRIPT_ID] with your assigned ID (e.g., "a16z", "sequoia")
3. Fill in COMPANIES list with scraped data
4. Fill in ADDITIONAL_JOBS list if adding jobs to companies already in DB
5. Update the FIRM_NAME constant
6. Run with: cd apps/api && python -m scripts.seed_[SCRIPT_ID]_jobs

ISOLATION: This script uses per-company transactions and dedup checks.
Multiple agents can run concurrently against the same DB without conflicts.

NAMING: seed_[SCRIPT_ID]_jobs.py — e.g., seed_a16z_jobs.py, seed_sequoia_jobs.py
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.employer import (
    Employer, Job, Organization, OrganizationMember,
    Vertical, RoleType, OrganizationRole,
)
from app.utils.auth import get_password_hash
from app.config import settings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# CONFIG — Update these for your VC firm
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRM_NAME = "TEMPLATE"  # e.g., "a16z", "Sequoia", "Greylock"
SCRIPT_ID = "template"  # e.g., "a16z", "sequoia", "greylock"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Each entry creates: Employer + Organization + OrganizationMember + Job(s)
#
# REQUIRED FIELDS per company:
#   company_name  — Unique display name (used for dedup)
#   email         — Unique email, typically careers@domain.com
#   name          — Contact name (founder name or "CompanyName Team")
#   industry      — e.g., "AI / Infrastructure", "Healthcare / AI"
#   company_size  — Always "startup" for VC portfolio companies
#   website       — Company homepage
#   slug          — URL-safe lowercase identifier (no spaces, no special chars)
#   description   — 2-4 sentence company description + "\n\nFund: X | HQ: City"
#   founders      — List of {name, title, linkedin} (linkedin can be "" if unknown)
#   jobs          — List of job entries (see below)
#
# REQUIRED FIELDS per job:
#   title         — Include timing, e.g., "SWE Intern (Summer 2026)"
#   vertical      — Vertical enum value
#   role_type     — RoleType enum value
#   location      — City, State format, e.g., "San Francisco, CA"
#   salary_min    — Monthly USD (integer), e.g., 5000
#   salary_max    — Monthly USD (integer), e.g., 8000
#   requirements  — List of 3-5 requirement strings
#   description   — Job description + "\n\nSource: [URL]"

COMPANIES = [
    # ── Example Company ──
    # {
    #     "company_name": "ExampleCo",
    #     "email": "careers@example.com",
    #     "name": "Jane Doe",
    #     "industry": "AI / Developer Tools",
    #     "company_size": "startup",
    #     "website": "https://example.com",
    #     "slug": "exampleco",
    #     "description": (
    #         "ExampleCo builds AI-powered developer tools.\n\n"
    #         "Fund: a16z | HQ: San Francisco"
    #     ),
    #     "founders": [
    #         {"name": "Jane Doe", "title": "CEO", "linkedin": "https://linkedin.com/in/janedoe"},
    #     ],
    #     "jobs": [
    #         {
    #             "title": "Software Engineering Intern (Summer 2026)",
    #             "vertical": Vertical.SOFTWARE_ENGINEERING,
    #             "role_type": RoleType.SOFTWARE_ENGINEER,
    #             "location": "San Francisco, CA",
    #             "salary_min": 5000,
    #             "salary_max": 8000,
    #             "requirements": [
    #                 "Strong programming skills in Python or TypeScript",
    #                 "Interest in developer tools",
    #                 "Available for summer 2026",
    #             ],
    #             "description": (
    #                 "SWE Intern at ExampleCo\n\n"
    #                 "Build AI-powered developer tools.\n\n"
    #                 "Source: https://jobs.example.com/12345"
    #             ),
    #         },
    #     ],
    # },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#
# Use this when a company was already seeded by another agent, but you
# found additional intern roles for it on your VC firm's board.
#
# Only the company_name and jobs[] fields are needed.

ADDITIONAL_JOBS = [
    # {
    #     "company_name": "ExistingCompany",
    #     "jobs": [
    #         {
    #             "title": "Data Science Intern (Summer 2026)",
    #             "vertical": Vertical.DATA,
    #             "role_type": RoleType.DATA_SCIENTIST,
    #             "location": "New York, NY",
    #             "salary_min": 6000,
    #             "salary_max": 9000,
    #             "requirements": ["Python", "SQL", "Statistics"],
    #             "description": "Data Science Intern at ExistingCompany\n\nSource: URL",
    #         },
    #     ],
    # },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DB OPERATIONS — Do not modify below this line
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def seed_new_company(session, company_data):
    """
    Create a new company with employer, organization, membership, and jobs.
    Skips entirely if company_name already exists.
    Returns number of jobs added.
    """
    company_name = company_data["company_name"]

    existing = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()
    if existing:
        print(f"  SKIP (already exists): {company_name}")
        return 0

    slug = company_data.get("slug", company_name.lower().replace(" ", "-"))
    employer_id = generate_cuid("e_")
    org_id = generate_cuid("o_")
    member_id = generate_cuid("tm_")

    # Create employer
    employer = Employer(
        id=employer_id,
        name=company_data["name"],
        company_name=company_name,
        email=company_data["email"],
        password=get_password_hash(f"{slug}Seed!2026"),
        industry=company_data.get("industry"),
        company_size=company_data.get("company_size", "startup"),
        is_verified=True,
    )
    session.add(employer)

    # Create organization
    organization = Organization(
        id=org_id,
        name=company_name,
        slug=slug,
        website=company_data.get("website"),
        industry=company_data.get("industry"),
        company_size=company_data.get("company_size", "startup"),
        description=company_data.get("description"),
        settings={"founders": company_data.get("founders", [])},
    )
    session.add(organization)

    # Link employer to organization
    membership = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(membership)

    # Create jobs
    job_count = 0
    for job_data in company_data.get("jobs", []):
        job = Job(
            id=generate_cuid("j_"),
            title=job_data["title"],
            description=job_data["description"],
            vertical=job_data.get("vertical"),
            role_type=job_data.get("role_type"),
            requirements=job_data.get("requirements", []),
            location=job_data.get("location"),
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            employer_id=employer_id,
            is_active=True,
        )
        session.add(job)
        job_count += 1
        sal = f"${job_data.get('salary_min', 0):,}-${job_data.get('salary_max', 0):,}/mo"
        print(f"    + {job.title} | {job.location} | {sal}")

    return job_count


def add_jobs_to_existing(session, entry):
    """
    Add new jobs to a company that already exists in the DB.
    Deduplicates by job title. Returns number of jobs added.
    """
    company_name = entry["company_name"]
    employer = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()

    if not employer:
        print(f"  SKIP (not found in DB): {company_name}")
        return 0

    existing_titles = {
        j.title
        for j in session.query(Job).filter(Job.employer_id == employer.id).all()
    }

    job_count = 0
    for job_data in entry.get("jobs", []):
        if job_data["title"] in existing_titles:
            print(f"    SKIP (duplicate): {job_data['title']}")
            continue

        job = Job(
            id=generate_cuid("j_"),
            title=job_data["title"],
            description=job_data["description"],
            vertical=job_data.get("vertical"),
            role_type=job_data.get("role_type"),
            requirements=job_data.get("requirements", []),
            location=job_data.get("location"),
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            employer_id=employer.id,
            is_active=True,
        )
        session.add(job)
        job_count += 1
        sal = f"${job_data.get('salary_min', 0):,}-${job_data.get('salary_max', 0):,}/mo"
        print(f"    + NEW {job.title} | {job.location} | {sal}")

    return job_count


def main():
    if not COMPANIES and not ADDITIONAL_JOBS:
        print("ERROR: No companies or jobs defined. Fill in the COMPANIES list.")
        sys.exit(1)

    print("=" * 60)
    print(f"Seeding Intern Jobs — {FIRM_NAME}")
    print("=" * 60)

    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)

    total_companies = 0
    total_jobs = 0
    errors = []

    # Phase 1: New companies (one transaction per company for isolation)
    if COMPANIES:
        print(f"\n--- Phase 1: {len(COMPANIES)} New Companies ---")
        for company_data in COMPANIES:
            company_name = company_data["company_name"]
            session = Session()
            try:
                print(f"\n[{company_name}]")
                jobs_added = seed_new_company(session, company_data)
                session.commit()
                if jobs_added > 0:
                    total_companies += 1
                    total_jobs += jobs_added
                    print(f"  OK: {jobs_added} job(s)")
            except Exception as e:
                session.rollback()
                error_msg = f"{company_name}: {e}"
                errors.append(error_msg)
                print(f"  ERROR: {e}")
            finally:
                session.close()

    # Phase 2: Additional jobs for existing companies
    if ADDITIONAL_JOBS:
        print(f"\n--- Phase 2: Additional Jobs for {len(ADDITIONAL_JOBS)} Existing Companies ---")
        for entry in ADDITIONAL_JOBS:
            company_name = entry["company_name"]
            session = Session()
            try:
                print(f"\n[{company_name}]")
                jobs_added = add_jobs_to_existing(session, entry)
                session.commit()
                total_jobs += jobs_added
                if jobs_added:
                    print(f"  OK: {jobs_added} new job(s)")
                else:
                    print(f"  No new jobs needed")
            except Exception as e:
                session.rollback()
                error_msg = f"{company_name} (additional): {e}"
                errors.append(error_msg)
                print(f"  ERROR: {e}")
            finally:
                session.close()

    # Summary
    session = Session()
    db_employers = session.query(Employer).count()
    db_jobs = session.query(Job).count()
    session.close()

    print(f"\n{'=' * 60}")
    print(f"{FIRM_NAME} seed complete:")
    print(f"  New companies: {total_companies}")
    print(f"  New jobs:      {total_jobs}")
    if errors:
        print(f"  Errors:        {len(errors)}")
        for e in errors:
            print(f"    - {e}")
    print(f"\nDB totals: {db_employers} employers, {db_jobs} jobs")
    print(f"{'=' * 60}")


if __name__ == "__main__":
    main()
