#!/usr/bin/env python3
"""
Seed intern jobs from Pear VC portfolio companies into the Pathway database.

Pear VC (https://pear.vc) is a pre-seed and seed-focused VC firm founded by
Pejman Nozad and Mar Hershenson. Notable portfolio: DoorDash, Gusto, Guardant
Health, Vanta, Addepar, Viz.ai, Aurora Solar, WindBorne Systems, Capella Space.

Sources:
- https://pear.vc/portfolio
- https://jobs.ashbyhq.com/pear (Pear VC Ashby job board)
- https://job-boards.greenhouse.io/addepar1
- https://windbornesystems.com/open-roles
- https://capellaspace.com/company/careers
- https://job-boards.greenhouse.io/gusto/jobs/7238671

Companies already in DB (Gusto) have new jobs added via ADDITIONAL_JOBS.
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
FIRM_NAME = "Pear VC"
SCRIPT_ID = "pearvc"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Addepar ──
    {
        "company_name": "Addepar",
        "email": "careers@addepar.com",
        "name": "Eric Poirier",
        "industry": "FinTech / Wealth Management",
        "company_size": "startup",
        "website": "https://addepar.com",
        "slug": "addepar",
        "description": (
            "Addepar is a global technology and data company that builds software "
            "for investment professionals to manage and analyze over $8 trillion in "
            "assets across 50+ countries. Their platform unifies data, analytics, "
            "and reporting for wealth managers, RIAs, and family offices.\n\n"
            "Fund: Pear VC | HQ: Mountain View, CA"
        ),
        "founders": [
            {"name": "Joe Lonsdale", "title": "Founder & Chairman", "linkedin": "https://linkedin.com/in/joelonsdale"},
            {"name": "Eric Poirier", "title": "CEO", "linkedin": "https://linkedin.com/in/ericpoirier"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern - Research (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 7500,
                "salary_max": 9000,
                "requirements": [
                    "Currently enrolled in BS/MS in Computer Science or related field at a US/Canada university",
                    "Must be returning to school after internship",
                    "Strong programming skills and interest in data engineering",
                    "Experience with or interest in financial data systems",
                ],
                "description": (
                    "Software Engineer Intern on the Research Engineering Team at Addepar. "
                    "This is one of the most exciting areas at Addepar from a data, engineering, "
                    "and business perspective. You'll collaborate deeply with the Research Team "
                    "to enable research with quality at scale. 12-week remote internship with "
                    "dedicated mentor and team manager.\n\n"
                    "Compensation: $51/hr\n\n"
                    "Source: https://job-boards.greenhouse.io/addepar1/jobs/7830853002"
                ),
            },
            {
                "title": "Software Engineer Intern - Analysis Workflow (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 7500,
                "salary_max": 9000,
                "requirements": [
                    "Currently enrolled in BS/MS in Computer Science or related field at a US/Canada university",
                    "Must be returning to school after internship",
                    "Strong full-stack development skills",
                    "Interest in building financial analysis and dashboard tools",
                ],
                "description": (
                    "Software Engineer Intern on the Analysis, Widgets, and Dashboards (AWD) Team "
                    "at Addepar. The AWD team is actively building out new modules and functionality "
                    "for the next generation of Addepar's core product. 12-week remote internship "
                    "as part of the AddeU Internship Program with mentorship and onboarding.\n\n"
                    "Compensation: $51/hr\n\n"
                    "Source: https://jobs.ffvc.com/companies/addepar/jobs/45230343-software-engineer-intern-analysis-workflow"
                ),
            },
        ],
    },

    # ── WindBorne Systems ──
    {
        "company_name": "WindBorne Systems",
        "email": "careers@windbornesystems.com",
        "name": "John Dean",
        "industry": "Climate Tech / Weather Intelligence",
        "company_size": "startup",
        "website": "https://windbornesystems.com",
        "slug": "windborne-systems",
        "description": (
            "WindBorne Systems supercharges weather forecasts with a global constellation "
            "of next-generation smart weather balloons. The company designs, manufactures, "
            "and operates its own balloon fleet to generate weather intelligence, helping "
            "humanity adapt to climate change. Forbes 30 Under 30, Inc. 5000 honoree.\n\n"
            "Fund: Pear VC | HQ: Palo Alto, CA"
        ),
        "founders": [
            {"name": "John Dean", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/johndeanwb"},
            {"name": "Andrew Sushko", "title": "Co-Founder", "linkedin": ""},
            {"name": "Kai Marshland", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/kaimarshland"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern - Product (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 5000,
                "salary_max": 6000,
                "requirements": [
                    "Strong software engineering skills in frontend and/or backend development",
                    "High agency and willingness to work in a fast-paced startup",
                    "Ability to learn quickly and work on real customer-facing products",
                    "Interest in climate tech, weather forecasting, or geospatial data",
                ],
                "description": (
                    "Software Engineering Intern on the Product team at WindBorne Systems. "
                    "Build forecasting and insight products, working on the frontend and/or "
                    "backend to help customers gain actionable weather insights. Interns receive "
                    "the responsibility, respect, and trust of full-time engineers with high "
                    "potential to convert to full-time.\n\n"
                    "Compensation: ~$35/hr\n\n"
                    "Source: https://windbornesystems.com/careers/software-engineering-intern-product"
                ),
            },
            {
                "title": "Atlas Software Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 5000,
                "salary_max": 6000,
                "requirements": [
                    "Strong systems programming and infrastructure skills",
                    "Interest in data-driven automations and distributed systems",
                    "High agency and ability to learn quickly",
                    "Interest in satellite/balloon constellation management or IoT",
                ],
                "description": (
                    "Atlas Software Intern at WindBorne Systems. Help build the in situ global "
                    "nervous system 'Atlas' — working on data-driven automations, launch "
                    "infrastructure, flight software, and constellation management for "
                    "WindBorne's global balloon fleet.\n\n"
                    "Compensation: ~$35/hr\n\n"
                    "Source: https://windbornesystems.com/careers/atlas-software-intern"
                ),
            },
            {
                "title": "Software Engineering Intern - Finance (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 5000,
                "salary_max": 6000,
                "requirements": [
                    "Software engineering skills with interest in finance workflows",
                    "Experience with or interest in building internal tools",
                    "High agency and willingness to work in a fast-paced startup",
                    "Interest in procurement, reporting, or financial automation",
                ],
                "description": (
                    "Software Engineering Intern (Finance) at WindBorne Systems. Build tools "
                    "for finance workflows including procurement and reporting. Combine software "
                    "engineering with finance operations at a fast-growing climate tech startup.\n\n"
                    "Compensation: ~$35/hr\n\n"
                    "Source: https://windbornesystems.com/careers/software-engineering-intern-finance"
                ),
            },
        ],
    },

    # ── Capella Space ──
    {
        "company_name": "Capella Space",
        "email": "careers@capellaspace.com",
        "name": "Capella Space Team",
        "industry": "Space / Defense Tech",
        "company_size": "startup",
        "website": "https://capellaspace.com",
        "slug": "capella-space",
        "description": (
            "Capella Space builds and operates the largest constellation of commercial "
            "Synthetic Aperture Radar (SAR) satellites, providing persistent monitoring "
            "capabilities anywhere on the globe regardless of weather or time of day. "
            "PearX accelerator alumni.\n\n"
            "Fund: Pear VC (PearX) | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Payam Banazadeh", "title": "Founder", "linkedin": "https://linkedin.com/in/payamban"},
        ],
        "jobs": [
            {
                "title": "Flight Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Louisville, CO",
                "salary_min": 5500,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing degree in Computer Science, Aerospace Engineering, or related field",
                    "Experience with embedded systems or flight software",
                    "Must be a U.S. citizen, permanent resident, or lawfully admitted refugee (ITAR)",
                    "Available for 10-week in-person program June-August 2026",
                ],
                "description": (
                    "Flight Software Engineering Intern at Capella Space. Work on spacecraft "
                    "flight software development in a 10-week, in-person program. Gain hands-on "
                    "experience in satellite operations and geospatial technology. Includes "
                    "mentorship, team engagement, and social events. Housing allowance provided.\n\n"
                    "Compensation: $37/hr + living allowance\n\n"
                    "Source: https://capellaspace.com/company/careers"
                ),
            },
            {
                "title": "Security Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Louisville, CO",
                "salary_min": 5500,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing degree in Computer Science, Cybersecurity, or related field",
                    "Interest in security engineering and infrastructure hardening",
                    "Must be a U.S. citizen, permanent resident, or lawfully admitted refugee (ITAR)",
                    "Available for 10-week in-person program June-August 2026",
                ],
                "description": (
                    "Security Engineering Intern at Capella Space. Work on security systems "
                    "for satellite infrastructure during a 10-week in-person program. Paired "
                    "with a mentor, with opportunities for team engagement and presentations.\n\n"
                    "Compensation: $37/hr + living allowance\n\n"
                    "Source: https://capellaspace.com/company/careers"
                ),
            },
        ],
    },

    # ── Conduit Tech ──
    {
        "company_name": "Conduit Tech",
        "email": "careers@conduit.tech",
        "name": "Shelby Breger",
        "industry": "Climate Tech / HVAC",
        "company_size": "startup",
        "website": "https://www.conduit.tech",
        "slug": "conduit-tech",
        "description": (
            "Conduit Tech builds software to help HVAC professionals more quickly and "
            "profitably design, sell, and install high-efficiency heating and cooling "
            "systems. PearX accelerator alumni, backed by Breakthrough Energy Ventures "
            "and Pear VC. Spun out of Stanford Climate Ventures.\n\n"
            "Fund: Pear VC (PearX) | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Shelby Breger", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/shelbybreger"},
            {"name": "Marisa Reddy", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/marisareddy"},
        ],
        "jobs": [
            {
                "title": "Business Operations Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.BUSINESS_ANALYST,
                "location": "New York, NY",
                "salary_min": 4000,
                "salary_max": 6000,
                "requirements": [
                    "Strong analytical and organizational skills",
                    "Interest in climate tech, energy efficiency, or sustainability",
                    "Ability to work across teams in a fast-paced startup",
                    "Proficiency with spreadsheets and data analysis tools",
                ],
                "description": (
                    "Business Operations Intern at Conduit Tech. Work across the team on "
                    "operations, strategy, and growth initiatives at a climate tech startup "
                    "building tools for the HVAC industry. Conduit is tackling a 100,000+ "
                    "person labor shortage in HVAC with innovative software.\n\n"
                    "Source: https://jobs.ashbyhq.com/pear/3881774b-1869-4b30-b625-5ae01de63bf9"
                ),
            },
        ],
    },

    # ── Affinity ──
    {
        "company_name": "Affinity",
        "email": "careers@affinity.co",
        "name": "Ray Zhou",
        "industry": "Enterprise SaaS / CRM",
        "company_size": "startup",
        "website": "https://affinity.co",
        "slug": "affinity-crm",
        "description": (
            "Affinity is a relationship intelligence platform that uses AI to power "
            "dealmakers in venture capital, investment banking, private equity, and "
            "consulting. Founded by Stanford CS grads and Forbes 30 Under 30 honorees. "
            "PearX accelerator alumni with $120M+ in total funding.\n\n"
            "Fund: Pear VC (PearX) | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Ray Zhou", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/rayzhou"},
            {"name": "Shubham Goel", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/shubhamgoel"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Pursuing BS/MS in Computer Science or related field",
                    "Strong programming skills in Python, TypeScript, or similar",
                    "Interest in CRM, relationship intelligence, or enterprise SaaS",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Software Engineering Intern at Affinity. Work on the relationship "
                    "intelligence platform that empowers dealmakers across VC, PE, and "
                    "investment banking. Affinity's AI captures data from emails and "
                    "calendars to provide insights that drive better deals.\n\n"
                    "Source: https://affinity.co/company/careers"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    {
        "company_name": "Gusto",
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8000,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing BS/MS in Computer Science, Software Engineering, or related technical field",
                    "Expected graduation between December 2026 and June 2029",
                    "U.S. work authorization required (no visa sponsorship)",
                    "Available for 12-16 week hybrid summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Gusto (Pear VC portfolio). 12 or 16-week "
                    "hybrid summer experience embedded directly into engineering teams. Each "
                    "intern is paired with a dedicated mentor and team manager. Hybrid: in-office "
                    "2-3 days/week. Also available in NYC and Denver locations.\n\n"
                    "Compensation: $58.65/hr (SF/NYC undergrad), $46.63/hr (Denver undergrad)\n"
                    "Relocation assistance provided.\n\n"
                    "Source: https://job-boards.greenhouse.io/gusto/jobs/7238671"
                ),
            },
        ],
    },
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
