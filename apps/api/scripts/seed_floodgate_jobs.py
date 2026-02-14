#!/usr/bin/env python3
"""
Seed intern jobs from Floodgate portfolio companies' job boards.

Floodgate is a seed-stage venture fund based in Palo Alto, CA.
Notable portfolio: Lyft, Chegg, Okta, Applied Intuition, Superhuman, etc.

Companies seeded: 3 new companies, 4 jobs
- Lyft (2 SWE interns)
- Eudia (1 AI engineer intern)
- Chegg (1 SWE intern)
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
# CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
FIRM_NAME = "Floodgate"
SCRIPT_ID = "floodgate"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Lyft ──
    {
        "company_name": "Lyft",
        "email": "careers@lyft.com",
        "name": "Lyft Recruiting",
        "industry": "Transportation / Technology",
        "company_size": "startup",
        "website": "https://www.lyft.com",
        "slug": "lyft",
        "description": (
            "Lyft is a ridesharing and transportation platform connecting "
            "riders with drivers across the US and Canada. The company also "
            "operates bike-share and scooter programs in select cities.\n\n"
            "Fund: Floodgate | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Logan Green", "title": "Co-founder", "linkedin": "https://linkedin.com/in/logangreen"},
            {"name": "John Zimmer", "title": "Co-founder", "linkedin": "https://linkedin.com/in/johnzimmer"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern, Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8300,
                "salary_max": 9300,
                "requirements": [
                    "Pursuing BS or MS in Computer Science, graduating Dec 2026 - Summer 2027",
                    "Strong CS fundamentals including data structures and algorithms",
                    "Experience with unit testing, integration testing, and end-to-end testing",
                    "Database experience and familiarity with backend systems",
                    "Available for Summer 2026 internship in San Francisco (hybrid, 3 days/week)",
                ],
                "description": (
                    "Software Engineer Intern, Backend at Lyft\n\n"
                    "Join Lyft's engineering team to build and scale backend services "
                    "powering one of the largest ridesharing platforms. Work on real-time "
                    "systems, APIs, and infrastructure serving millions of users.\n\n"
                    "Hybrid role: 3 days/week in SF office (Mon/Wed/Thu).\n"
                    "Pay: $52-$58/hour.\n\n"
                    "Source: https://app.careerpuck.com/job-board/lyft/job/8130804002"
                ),
            },
            {
                "title": "Software Engineer Intern, Mobile iOS (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8300,
                "salary_max": 9300,
                "requirements": [
                    "Pursuing BS or MS in Computer Science, graduating Dec 2026 - Summer 2027",
                    "Strong CS fundamentals including data structures and algorithms",
                    "Experience or interest in Swift and iOS mobile development",
                    "Familiarity with real-time technology and open source contributions a plus",
                    "Available for Summer 2026 internship in San Francisco (hybrid, 3 days/week)",
                ],
                "description": (
                    "Software Engineer Intern, Mobile iOS at Lyft\n\n"
                    "Develop user-facing mobile applications in Swift for Lyft's "
                    "transportation platform. Work on features used by millions of "
                    "riders and drivers daily.\n\n"
                    "Hybrid role: 3 days/week in SF office (Mon/Wed/Thu).\n"
                    "Pay: $52-$58/hour.\n\n"
                    "Source: https://app.careerpuck.com/job-board/lyft/job/8215921002"
                ),
            },
        ],
    },

    # ── Eudia ──
    {
        "company_name": "Eudia",
        "email": "careers@eudia.com",
        "name": "Omar Haroun",
        "industry": "AI / Legal Tech",
        "company_size": "startup",
        "website": "https://www.eudia.com",
        "slug": "eudia",
        "description": (
            "Eudia builds AI-powered tools for legal and professional services, "
            "helping law firms and enterprises automate complex document analysis "
            "and research workflows.\n\n"
            "Fund: General Catalyst, Floodgate | HQ: Palo Alto, CA"
        ),
        "founders": [
            {"name": "Omar Haroun", "title": "CEO", "linkedin": ""},
            {"name": "Ashish Agrawal", "title": "Co-founder", "linkedin": ""},
            {"name": "David Van Reyk", "title": "Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "AI Engineer Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Strong programming skills in Python",
                    "Familiarity with ML frameworks (PyTorch, TensorFlow) and LLM APIs",
                    "Interest in NLP, document understanding, or legal tech",
                    "Currently pursuing BS or MS in Computer Science, AI, or related field",
                ],
                "description": (
                    "AI Engineer Intern at Eudia\n\n"
                    "Work on cutting-edge AI models for legal document analysis and "
                    "research automation. Build and fine-tune LLM-powered workflows "
                    "that help law firms process complex cases faster.\n\n"
                    "Source: https://www.eudia.com"
                ),
            },
        ],
    },

    # ── Chegg ──
    {
        "company_name": "Chegg",
        "email": "careers@chegg.com",
        "name": "Chegg Recruiting",
        "industry": "Education / Technology",
        "company_size": "startup",
        "website": "https://www.chegg.com",
        "slug": "chegg",
        "description": (
            "Chegg is an education technology company providing homework help, "
            "textbook solutions, online tutoring, and internship matching for "
            "college students.\n\n"
            "Fund: Floodgate | HQ: Santa Clara, CA"
        ),
        "founders": [
            {"name": "Osman Rashid", "title": "Co-founder", "linkedin": ""},
            {"name": "Aayush Phumbhra", "title": "Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Santa Clara, CA",
                "salary_min": 5500,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing BS or MS in Computer Science or related discipline",
                    "Legally authorized to work in the US (citizen, green card, or F1 visa)",
                    "Solid foundation in data structures, algorithms, and software design",
                    "Ability to work 40 hours/week in Santa Clara office",
                    "Available for summer 2026 internship starting in June",
                ],
                "description": (
                    "Software Engineer Intern at Chegg\n\n"
                    "Create and support highly scalable, fault-tolerant programs that "
                    "interface with core transactional systems. Work within an AWS "
                    "ECS/EC2/S3 environment alongside Business Analysts, Operations "
                    "team members, and other engineers.\n\n"
                    "Pay: ~$37/hour.\n\n"
                    "Source: https://jobs.chegg.com/job/CHEGA0056OKBIBFWY/Software-Engineer-Intern"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — for companies already in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = []


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
