#!/usr/bin/env python3
"""
Seed intern jobs from Precursor Ventures portfolio companies.

FIRM: Precursor Ventures
JOB BOARD: https://precursorvc.com/portfolio/ (careers.precursorvc.com is offline)
SCRIPT ID: precursor

NOTE: Precursor Ventures is a pre-seed/seed fund (~321 companies).
Most portfolio companies are very early stage (5-20 employees) and do not
have formal internship programs. Only 3 companies had confirmed US-based
tech intern positions.

Companies: Superhuman, Juniper Square, Rad AI
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
FIRM_NAME = "Precursor Ventures"
SCRIPT_ID = "precursor"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Superhuman ──
    {
        "company_name": "Superhuman",
        "email": "careers@superhuman.com",
        "name": "Rahul Vohra",
        "industry": "Productivity / Email / AI",
        "company_size": "startup",
        "website": "https://superhuman.com",
        "slug": "superhuman",
        "description": (
            "Superhuman builds the fastest, most beautiful email experience ever made. "
            "The company uses AI to help professionals get through email twice as fast, "
            "with features like AI triage, instant reply, and scheduled send. Acquired "
            "by Grammarly in 2025.\n\n"
            "Fund: Precursor Ventures | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Rahul Vohra", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/rahulvohra"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8147,
                "salary_max": 8147,
                "requirements": [
                    "Currently enrolled in a Bachelor's degree program in CS or related field",
                    "Strong CS fundamentals (data structures, algorithms)",
                    "Proficiency in Java, JavaScript, C#, Python, or Go",
                    "Able to work in-person at SF office minimum 2 days/week",
                ],
                "description": (
                    "Software Engineering Intern at Superhuman (Summer 2026)\n\n"
                    "12-week internship working on front-end, back-end, full-stack, or mobile "
                    "engineering projects for the fastest email experience in the world. "
                    "Hybrid (minimum 2 days/week in San Francisco office). Demonstrates "
                    "independence, task management, and cross-functional collaboration.\n\n"
                    "$47/hr | San Francisco, CA (Hybrid)\n\n"
                    "Source: https://www.builtinsf.com/job/software-engineering-intern/7151311"
                ),
            },
        ],
    },

    # ── 2. Juniper Square ──
    {
        "company_name": "Juniper Square",
        "email": "careers@junipersquare.com",
        "name": "Alex Robinson",
        "industry": "FinTech / Real Estate / Investment Management",
        "company_size": "startup",
        "website": "https://www.junipersquare.com",
        "slug": "juniper-square",
        "description": (
            "Juniper Square is the leading investment management platform for the private "
            "capital markets. The company streamlines fundraising, investor reporting, and "
            "partnership accounting for commercial real estate firms, serving over $1 trillion "
            "in managed assets.\n\n"
            "Fund: Precursor Ventures | HQ: San Francisco (cloud-first)"
        ),
        "founders": [
            {"name": "Alex Robinson", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "Adam Ginsburg", "title": "Co-Founder", "linkedin": ""},
            {"name": "Yonas Fisseha", "title": "Co-Founder, Engineering", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "AI Engineer Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Remote, US",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Pursuing Bachelor's or Master's in Computer Science, Data Science, or related field",
                    "Experience with Python and machine learning frameworks",
                    "Interest in AI applications for financial services",
                    "Available for 10-week full-time internship (June 16 - August 22)",
                ],
                "description": (
                    "AI Engineer Intern at Juniper Square (Summer 2026)\n\n"
                    "10-week full-time internship (40 hrs/week) working on AI and automation "
                    "solutions for the private capital markets. Build AI-powered tools that help "
                    "real estate investment firms manage over $1 trillion in assets. Remote "
                    "(US or Canada).\n\n"
                    "Remote (US) | June 16 - August 22, 2026\n\n"
                    "Source: https://careers.redpoint.com/companies/juniper-square/jobs/49470002-ai-engineer-intern"
                ),
            },
        ],
    },

    # ── 3. Rad AI ──
    {
        "company_name": "Rad AI",
        "email": "careers@radai.com",
        "name": "Doktor Gurson",
        "industry": "Healthcare / AI / Radiology",
        "company_size": "startup",
        "website": "https://www.radai.com",
        "slug": "rad-ai",
        "description": (
            "Rad AI is a healthcare AI company that automates radiology report generation, "
            "helping radiologists work more efficiently. The platform uses AI to transform "
            "patient-radiologist workflows across healthcare systems. Valued at ~$525M with "
            "$140M+ raised.\n\n"
            "Fund: Precursor Ventures | HQ: San Francisco (Remote-first)"
        ),
        "founders": [
            {"name": "Doktor Gurson", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "Dr. Jeff Chang", "title": "Co-Founder & CPO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Currently enrolled full-time in Bachelor's or Master's in CS or related field",
                    "Prior software engineering experience (internship, projects, or publications)",
                    "Proficiency in Python, JavaScript/TypeScript, FastAPI, or equivalent",
                    "Knowledge of relational and document-based databases",
                    "Must have US work authorization and intent to return to degree program",
                ],
                "description": (
                    "Software Engineer Intern at Rad AI (Summer 2026)\n\n"
                    "12-week internship working on AI-powered radiology tools that improve "
                    "diagnostic efficiency across healthcare systems. Fully remote (US/Canada) "
                    "with optional San Francisco office. Benefits include medical/dental/vision, "
                    "HSA, 401(k), and housing stipend. Opportunity for full-time offer.\n\n"
                    "Remote (US) or San Francisco, CA\n\n"
                    "Source: https://www.radai.com/careers"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
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
