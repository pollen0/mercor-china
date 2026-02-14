#!/usr/bin/env python3
"""
Seed intern jobs from First Round Capital portfolio companies.

First Round Capital is a seed-stage VC firm founded in 2004, based in SF.
Notable portfolio includes Uber, Notion, Roblox, Square, Verkada, and 500+ others.

Run with: cd apps/api && python -m scripts.seed_firstround_jobs
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
FIRM_NAME = "First Round Capital"
SCRIPT_ID = "firstround"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
COMPANIES = [
    # ── Persona ──
    {
        "company_name": "Persona",
        "email": "careers@withpersona.com",
        "name": "Rick Song",
        "industry": "Identity / Security / SaaS",
        "company_size": "startup",
        "website": "https://withpersona.com",
        "slug": "persona",
        "description": (
            "Persona is the identity platform for businesses. Offers flexible "
            "building blocks that help companies fight fraud, stay compliant, and "
            "build trust among their customers. Series C, 250+ employees. "
            "Clients include Coursera, OpenAI, and Lime.\n\n"
            "Fund: First Round Capital | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Rick Song", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "Charles Yeh", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 9500,
                "requirements": [
                    "Pursuing Bachelor's or Master's in CS, Engineering, or Math",
                    "Must graduate Spring 2027",
                    "Full-stack development proficiency with data modeling expertise",
                    "Previous programming experience required",
                ],
                "description": (
                    "Software Engineer Intern at Persona (Summer 2026)\n\n"
                    "Ship code as early as your first week. Receive dedicated 1:1 "
                    "mentorship along with challenging technical assignments, novel "
                    "product feature work, and opportunities to stretch. Work on "
                    "identity platform design, customer partnerships, and scalable "
                    "systems. In-office Tue-Thu in San Francisco.\n\n"
                    "Source: https://www.builtinsf.com/job/software-engineer-intern-summer-2026/7254941"
                ),
            },
            {
                "title": "Product Design Intern (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.PRODUCT_DESIGNER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 9500,
                "requirements": [
                    "Pursuing degree in Design, HCI, or related field",
                    "Portfolio demonstrating strong visual and interaction design",
                    "Experience with Figma or similar design tools",
                    "Interest in identity verification and trust & safety",
                ],
                "description": (
                    "Product Design Intern at Persona (Summer 2026)\n\n"
                    "Join the design team building the identity platform used by "
                    "major companies. Work on UX/UI for fraud prevention and "
                    "compliance products. In-office Tue-Thu in San Francisco.\n\n"
                    "Source: https://www.builtinsf.com/job/product-design-intern-summer-2026/7254925"
                ),
            },
        ],
    },
    # ── K2 Space ──
    {
        "company_name": "K2 Space",
        "email": "careers@k2space.com",
        "name": "Karan Kunjur",
        "industry": "Aerospace / Space Tech",
        "company_size": "startup",
        "website": "https://www.k2space.com",
        "slug": "k2-space",
        "description": (
            "K2 Space builds the highest-powered satellite platforms ever built "
            "for missions across LEO to Deep Space. $450M in funding and $500M "
            "in signed contracts. Focused on mass production of advanced "
            "spacecraft including the 20kW+ Mega satellite.\n\n"
            "Fund: First Round Capital | HQ: Los Angeles"
        ),
        "founders": [
            {"name": "Karan Kunjur", "title": "Co-Founder & CEO", "linkedin": ""},
            {"name": "Jonathan Hofeller", "title": "Co-Founder & President", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Torrance, CA",
                "salary_min": 5200,
                "salary_max": 6900,
                "requirements": [
                    "Pursuing Bachelor's or Master's in CS, CE, EE, or related",
                    "6+ months technical engineering experience outside classroom",
                    "Development experience in Rust, C/C++, or Go",
                    "U.S. Person status required (ITAR compliance)",
                ],
                "description": (
                    "Software Engineering Intern at K2 Space (Summer 2026)\n\n"
                    "Own a software engineering project end-to-end and support "
                    "actual on-orbit operations of the Mega spacecraft. Develop "
                    "software for spacecraft subsystem control including propulsion, "
                    "GNC, thermal, power, and communications. Design real-time, "
                    "fault-tolerant software architecture. 12-week minimum.\n\n"
                    "Housing and travel stipends may be available.\n\n"
                    "Source: https://job-boards.greenhouse.io/k2spacecorporation/jobs/4885102008"
                ),
            },
        ],
    },
    # ── Flexport ──
    {
        "company_name": "Flexport",
        "email": "careers@flexport.com",
        "name": "Ryan Petersen",
        "industry": "Logistics / Supply Chain",
        "company_size": "startup",
        "website": "https://www.flexport.com",
        "slug": "flexport",
        "description": (
            "Flexport moves freight globally by air, ocean, rail, and truck for "
            "the world's leading brands. Technology-driven supply chain management "
            "platform that makes global trade easier for businesses of all sizes.\n\n"
            "Fund: First Round Capital | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Ryan Petersen", "title": "Founder & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 8000,
                "salary_max": 8000,
                "requirements": [
                    "Undergraduate pursuing degree in CS or software development",
                    "Expecting to graduate within 1 year of internship",
                    "Exposure to web application development",
                    "Functional knowledge of JavaScript and MVC frameworks (e.g., Rails)",
                ],
                "description": (
                    "Software Engineering Intern at Flexport (Summer 2026)\n\n"
                    "Join the freight forwarding operations engineering team in "
                    "Chicago. Automate complex processes in one of the last "
                    "industries to go untouched by technology. Assigned manager "
                    "and mentor dedicated to your success.\n\n"
                    "Source: https://www.flexport.com/careers/teams/engineering/"
                ),
            },
        ],
    },
    # ── Uber ──
    {
        "company_name": "Uber",
        "email": "careers@uber.com",
        "name": "Uber Team",
        "industry": "Transportation / Technology",
        "company_size": "startup",
        "website": "https://www.uber.com",
        "slug": "uber",
        "description": (
            "Uber is a global ride-hailing and delivery platform connecting "
            "riders with drivers and eaters with restaurants through Uber and "
            "Uber Eats apps. Also operates Uber Freight for logistics.\n\n"
            "Fund: First Round Capital | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Travis Kalanick", "title": "Co-Founder", "linkedin": ""},
            {"name": "Garrett Camp", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing Bachelor's or Master's in CS or related field",
                    "Expected graduation December 2026 - August 2027",
                    "Proficiency in Go, Python, Ruby, Java, or C/C++",
                    "Prior internship or work experience preferred",
                ],
                "description": (
                    "Software Engineering Intern at Uber (Summer 2026)\n\n"
                    "Work with your manager and mentor to drive exciting, "
                    "previously unsolved projects. Design software applications "
                    "using Uber's tech stack. Resolve technical issues and build "
                    "integrated components while demonstrating project ownership. "
                    "10-12 weeks. Eligible for health, dental, vision, 401(k), "
                    "and company equity.\n\n"
                    "Source: https://www.uber.com/us/en/careers/teams/university/"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies already in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
ADDITIONAL_JOBS = [
    # Notion, Clay, Roblox, Square, Upstart, Verkada already in DB
    # via other VC seed scripts. No additional unique intern positions found.
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
