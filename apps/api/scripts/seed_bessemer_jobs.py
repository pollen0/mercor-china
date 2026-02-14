#!/usr/bin/env python3
"""
Seed intern jobs from Bessemer Venture Partners portfolio companies into Pathway.

Bessemer Venture Partners is one of the oldest VC firms in the US (founded 1911),
with 900+ portfolio companies including 69 unicorns. This script covers US-based
portfolio companies with confirmed internship positions.

Portfolio companies already in DB (skipped): Abridge
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
FIRM_NAME = "Bessemer Venture Partners"
SCRIPT_ID = "bessemer"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Boom Supersonic ──
    {
        "company_name": "Boom Supersonic",
        "email": "careers@boomsupersonic.com",
        "name": "Blake Scholl",
        "industry": "Aerospace / Deep Tech",
        "company_size": "startup",
        "website": "https://boomsupersonic.com",
        "slug": "boom-supersonic",
        "description": (
            "Boom Supersonic is building the world's fastest airliner — Overture — "
            "designed to fly at Mach 1.7 over water. Founded in 2014, Boom has a team of "
            "240+ employees and has flight-tested the XB-1 demonstrator, which broke the "
            "sound barrier in January 2025. The company is also developing Symphony, the "
            "first purpose-built supersonic engine.\n\n"
            "Fund: Bessemer Venture Partners | HQ: Denver, CO"
        ),
        "founders": [
            {"name": "Blake Scholl", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/blakescholl"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Centennial, CO",
                "salary_min": 5200,
                "salary_max": 5200,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, or related field",
                    "Proficiency in Python, Golang, TypeScript, or systems languages (C++/Rust)",
                    "Interest in aerospace, CFD optimization, or embedded systems",
                    "US citizen or lawful permanent resident (ITAR requirement)",
                    "Available for full-time onsite work June to mid-August 2026",
                ],
                "description": (
                    "Software Engineering Intern at Boom Supersonic\n\n"
                    "Work on real aerospace challenges: shrinking week-long CFD runs, automating "
                    "control workflows, pulling data together from across disciplines, or developing "
                    "embedded systems that keep engines running safely. You'll learn and contribute "
                    "to projects using Python, Golang, TypeScript, and systems languages like C++ "
                    "or Rust.\n\n"
                    "100% onsite at Boom HQ in Centennial, CO. $30/hr + housing allowance.\n\n"
                    "Source: https://startup.jobs/software-engineering-intern-boom-supersonic-7212214"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Centennial, CO",
                "salary_min": 5200,
                "salary_max": 5200,
                "requirements": [
                    "Pursuing a degree in Data Science, Engineering, Mathematics, or Computer Science",
                    "One year from graduation (Bachelor's or Master's)",
                    "Experience with data analysis, visualization, and pipeline management",
                    "US citizen or lawful permanent resident (ITAR requirement)",
                    "Available for full-time onsite work June to mid-August 2026",
                ],
                "description": (
                    "Data Science Intern at Boom Supersonic\n\n"
                    "Work with the team developing tools and methods that power data acquisition "
                    "for Boom's engine development program. Dive into real-time telemetry and data "
                    "visualization, data wrangling and post-test data analysis, and get hands-on "
                    "hardware experience.\n\n"
                    "100% onsite at Boom HQ in Centennial, CO. $30/hr + housing allowance.\n\n"
                    "Source: https://builtin.com/job/data-science-intern/4657102"
                ),
            },
        ],
    },

    # ── GlossGenius ──
    {
        "company_name": "GlossGenius",
        "email": "careers@glossgenius.com",
        "name": "Danielle Cohen-Shohet",
        "industry": "SaaS / Beauty Tech",
        "company_size": "startup",
        "website": "https://glossgenius.com",
        "slug": "glossgenius",
        "description": (
            "GlossGenius is the operating system for appointment-based businesses. Over "
            "100,000 businesses — salons, spas, medspas, wellness practices — trust GlossGenius "
            "to run and scale their operations with integrated payments, booking, client & team "
            "management, and marketing. Founded by a Goldman Sachs alum who coded the first "
            "version herself.\n\n"
            "Fund: Bessemer Venture Partners | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Danielle Cohen-Shohet", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/dcohenshohet"},
        ],
        "jobs": [
            {
                "title": "Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 4300,
                "salary_max": 8700,
                "requirements": [
                    "Currently pursuing a B.S. in Computer Science or related technical field",
                    "Graduation date between 2027 and 2028",
                    "Ability to write clean, efficient code following industry best practices",
                    "Available to work from GlossGenius office in Union Square, NYC",
                ],
                "description": (
                    "Engineering Intern (Summer 2026) at GlossGenius\n\n"
                    "Collaborate with senior engineers to design, develop, and test new features "
                    "for web and mobile applications. Write clean and efficient code while adhering "
                    "to GlossGenius coding standards. Participate in debugging, troubleshooting, "
                    "and code reviews.\n\n"
                    "In-office at 579 Broadway 2C, New York, NY (Union Square). $25-$50/hr.\n\n"
                    "Source: https://job-boards.greenhouse.io/glossgenius/jobs/7413808003"
                ),
            },
        ],
    },

    # ── Betterment ──
    {
        "company_name": "Betterment",
        "email": "careers@betterment.com",
        "name": "Sarah Kirshbaum Levy",
        "industry": "Fintech / Wealth Management",
        "company_size": "startup",
        "website": "https://www.betterment.com",
        "slug": "betterment",
        "description": (
            "Betterment is the largest independent online financial advisor in the US, with "
            "over $50B in assets under management. The platform offers goal-based investing, "
            "retirement planning, and cash management tools. Founded in 2010, Betterment "
            "pioneered fractional shares, smart asset allocation, and tax-loss harvesting "
            "for everyday investors.\n\n"
            "Fund: Bessemer Venture Partners | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Jon Stein", "title": "Founder & Chairman", "linkedin": "https://linkedin.com/in/jonstein"},
            {"name": "Sarah Kirshbaum Levy", "title": "CEO", "linkedin": "https://linkedin.com/in/sarah-kirshbaum-levy-889881a1"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 6000,
                "salary_max": 7800,
                "requirements": [
                    "Pursuing a degree in Computer Science, Software Engineering, or related field",
                    "Strong programming fundamentals and problem-solving skills",
                    "Interest in fintech, personal finance, or investment platforms",
                    "Available for summer internship in Manhattan (in-office Tue-Thu)",
                ],
                "description": (
                    "Software Engineering Intern (Summer) at Betterment\n\n"
                    "Work alongside experienced engineers in focused squads, aligned to a mentor "
                    "with tools and support to grow professionally. Build applications that "
                    "directly impact customers through improved UI/UX and features to help users "
                    "make the most of their money. Hiring across full-stack, backend, and mobile "
                    "disciplines.\n\n"
                    "In-office Tue-Thu at Manhattan HQ.\n\n"
                    "Source: https://startup.jobs/software-engineer-summer-internship-betterment-267693"
                ),
            },
        ],
    },

    # ── BigID ──
    {
        "company_name": "BigID",
        "email": "careers@bigid.com",
        "name": "Dimitri Sirota",
        "industry": "Cybersecurity / Data Privacy",
        "company_size": "startup",
        "website": "https://bigid.com",
        "slug": "bigid",
        "description": (
            "BigID is an innovative tech startup that helps companies manage, protect, and get "
            "more value from their data. The platform provides solutions for data security, "
            "compliance, privacy, and AI data management. BigID helps enterprises satisfy "
            "regulations like GDPR, CCPA, and emerging AI governance requirements.\n\n"
            "Fund: Bessemer Venture Partners | HQ: New York, NY (Remote-first)"
        ),
        "founders": [
            {"name": "Dimitri Sirota", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/dimitrisirota"},
        ],
        "jobs": [
            {
                "title": "Software Integration Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 3500,
                "salary_max": 3500,
                "requirements": [
                    "Enrolled in a Bachelor's degree in Computer Science or related discipline",
                    "Hands-on experience with JavaScript/TypeScript, Python, or Java",
                    "Strong understanding of object-oriented programming, data structures, and algorithms",
                    "Interest in data security, privacy, or compliance tech",
                ],
                "description": (
                    "Software Integration Engineer Intern at BigID\n\n"
                    "Join the R&D group for a 10-week paid internship developing technical content "
                    "and apps to integrate third-party data technologies with the BigID platform. "
                    "Work on building integrations that help enterprises manage and protect their "
                    "data across cloud and on-premise environments.\n\n"
                    "Remote (US, MST/PST preferred). $20/hr, up to 35 hours/week.\n\n"
                    "Source: https://portfoliojobs.comcastventures.com/companies/bigid/jobs/48011209-software-integration-engineer-intern"
                ),
            },
        ],
    },

    # ── Bevi ──
    {
        "company_name": "Bevi",
        "email": "careers@bevi.co",
        "name": "Sean Grundy",
        "industry": "IoT / CleanTech / Beverages",
        "company_size": "startup",
        "website": "https://bevi.co",
        "slug": "bevi",
        "description": (
            "Bevi makes Smart Water Coolers that provide sparkling, flavored, and enhanced "
            "water on demand, eliminating single-use plastic bottles. 25% of Fortune 500 "
            "companies use Bevi machines, and the company has saved over 450 million bottles "
            "and cans since 2014. Raised $160M+ in venture capital.\n\n"
            "Fund: Bessemer Venture Partners | HQ: Boston, MA"
        ),
        "founders": [
            {"name": "Sean Grundy", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/seangrundy"},
            {"name": "Eliza Becton", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/elizabecton"},
            {"name": "Frank Lee", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/frankleepe"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Boston, MA",
                "salary_min": 4000,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Experience with React.js, Redux, Java, or Android development",
                    "Ability to write unit and integration tests",
                    "Interest in IoT, sustainability, or hardware-software integration",
                ],
                "description": (
                    "Software Engineering Intern at Bevi\n\n"
                    "Work on an interesting project with day-to-day help from Bevi's engineering "
                    "team — it's very likely your project will be deployed to production. Expand "
                    "Bevi's Java applications using open-source libraries (Dropwizard, Jersey, "
                    "Guava) or work on the React.js/Redux frontend. Tech stack includes Docker "
                    "and microservices architecture.\n\n"
                    "Salary estimated based on comparable Boston startup internships.\n\n"
                    "Source: https://venturefizz.com/jobs/boston/software-engineering-intern-at-bevi-boston-ma"
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
