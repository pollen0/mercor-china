#!/usr/bin/env python3
"""
Seed intern jobs from General Catalyst, Founders Fund, and Index Ventures portfolios.

These are hybrid-stage VC firms (seed through growth) whose portfolio companies
are large enough for formal internship programs.

SCRIPT ID: gcffindex
RUN: cd apps/api && python -m scripts.seed_gcffindex_jobs
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
FIRM_NAME = "General Catalyst + Founders Fund + Index Ventures"
SCRIPT_ID = "gcffindex"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Palantir Technologies (Founders Fund) ──
    {
        "company_name": "Palantir Technologies",
        "email": "careers@palantir.com",
        "name": "Alex Karp",
        "industry": "Enterprise Software / Defense Tech",
        "company_size": "startup",
        "website": "https://palantir.com",
        "slug": "palantir-technologies",
        "description": (
            "Palantir builds enterprise data analytics platforms for government and commercial "
            "clients. Products include Gotham (defense/intelligence), Foundry (commercial), and "
            "Apollo (deployment). Public on NYSE (PLTR) with ~4,400 employees. Founded by Peter "
            "Thiel and Alex Karp.\n\n"
            "Source: Founders Fund Portfolio | HQ: Denver, CO"
        ),
        "founders": [
            {"name": "Alex Karp", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/alexkarp"},
            {"name": "Peter Thiel", "title": "Co-Founder & Chairman", "linkedin": "https://linkedin.com/in/peterthiel"},
            {"name": "Stephen Cohen", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/stephencohen"},
            {"name": "Joe Lonsdale", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/joelonsdale"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 10500,
                "salary_max": 14000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Java, C++, Python, or Go",
                    "Interest in large-scale data systems and distributed computing",
                    "US citizenship or permanent residency may be required for some teams",
                ],
                "description": (
                    "Software Engineer Intern at Palantir — Summer 2026\n\n"
                    "Build data platforms used by governments and Fortune 500 companies. "
                    "Work on Gotham, Foundry, or Apollo products at one of defense tech's "
                    "most influential companies. $10,500/mo + $3,500/mo housing stipend.\n\n"
                    "Source: Founders Fund Portfolio / Palantir Careers"
                ),
            },
            {
                "title": "Forward Deployed Software Engineer Intern - Defense (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Washington, DC",
                "salary_min": 10000,
                "salary_max": 13500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong full-stack development skills",
                    "Interest in defense technology and national security applications",
                    "US citizenship required for defense clearance eligibility",
                ],
                "description": (
                    "Forward Deployed Software Engineer (FDSE) Intern, Defense at Palantir — Summer 2026\n\n"
                    "Work directly with defense and intelligence clients to build custom solutions "
                    "using Palantir's platform. Unique blend of software engineering and client-facing "
                    "work in Washington, DC.\n\n"
                    "Source: Founders Fund Portfolio / Palantir Careers"
                ),
            },
        ],
    },

    # ── 2. Aurora Innovation (Index Ventures) ──
    {
        "company_name": "Aurora Innovation",
        "email": "careers@aurora.tech",
        "name": "Chris Urmson",
        "industry": "Autonomous Vehicles / Robotics",
        "company_size": "startup",
        "website": "https://aurora.tech",
        "slug": "aurora-innovation",
        "description": (
            "Aurora develops the Aurora Driver, a self-driving platform for autonomous freight "
            "trucks and ride-hailing vehicles. Public on NASDAQ (AUR). Founded by leaders from "
            "Google's self-driving car project (Waymo), Tesla Autopilot, and Uber ATG. ~1,800 employees.\n\n"
            "Source: Index Ventures Portfolio | HQ: Pittsburgh, PA"
        ),
        "founders": [
            {"name": "Chris Urmson", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/chris-urmson-5392273"},
            {"name": "Drew Bagnell", "title": "Co-Founder & Chief Scientist", "linkedin": "https://linkedin.com/in/drew-bagnell"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Pittsburgh, PA",
                "salary_min": 7800,
                "salary_max": 8300,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Robotics, or related field",
                    "Strong programming skills in C++ or Python",
                    "Interest in autonomous vehicles, robotics, or computer vision",
                    "Experience with perception, planning, or simulation systems is a plus",
                ],
                "description": (
                    "Software Engineering Intern at Aurora — Summer 2026\n\n"
                    "Build the Aurora Driver, a self-driving platform for trucks and ride-hailing. "
                    "Work on perception, planning, simulation, or infrastructure. Founded by "
                    "Google/Waymo, Tesla, and Uber self-driving leaders. $49/hr.\n\n"
                    "Source: Index Ventures Portfolio / Aurora Careers"
                ),
            },
            {
                "title": "Hardware Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 7800,
                "salary_max": 8300,
                "requirements": [
                    "Currently pursuing a degree in Electrical Engineering, Computer Engineering, or related",
                    "Experience with embedded systems, PCB design, or sensor integration",
                    "Interest in autonomous vehicles, LiDAR, or robotics hardware",
                    "Familiarity with hardware testing and validation processes",
                ],
                "description": (
                    "Hardware Engineering Intern at Aurora — Summer 2026\n\n"
                    "Design and test hardware for autonomous vehicles including LiDAR, sensors, "
                    "and compute platforms. Work in Mountain View, Pittsburgh, or Bozeman. "
                    "NASDAQ-listed. $49/hr (undergrad), $52/hr (master's).\n\n"
                    "Source: Index Ventures Portfolio / Aurora Careers"
                ),
            },
        ],
    },

    # ── 3. Datadog (Index Ventures) ──
    {
        "company_name": "Datadog",
        "email": "careers@datadoghq.com",
        "name": "Olivier Pomel",
        "industry": "Cloud Infrastructure / DevOps / SaaS",
        "company_size": "startup",
        "website": "https://datadoghq.com",
        "slug": "datadog",
        "description": (
            "Datadog is a cloud-based monitoring and analytics platform for IT, operations, and "
            "development teams. Provides infrastructure monitoring, APM, log management, and "
            "security analytics at scale. Public on NASDAQ (DDOG) with ~2,400 employees.\n\n"
            "Source: Index Ventures Portfolio | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Olivier Pomel", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/olivierpomel"},
            {"name": "Alexis Le-Quoc", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/alexislequoc"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8500,
                "salary_max": 10500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Go, Python, Java, or similar",
                    "Interest in cloud infrastructure, observability, or distributed systems",
                    "Experience with monitoring, logging, or metrics systems is a plus",
                ],
                "description": (
                    "Software Engineering Intern at Datadog — Summer 2026\n\n"
                    "Build cloud monitoring and analytics products used by thousands of companies. "
                    "Work on infrastructure monitoring, APM, log management, or security analytics. "
                    "12-week program in NYC or Boston. ~$52.88/hr.\n\n"
                    "Source: Index Ventures Portfolio / Datadog Careers"
                ),
            },
        ],
    },

    # ── 4. Persona (Index Ventures + Founders Fund) ──
    {
        "company_name": "Persona",
        "email": "careers@withpersona.com",
        "name": "Rick Song",
        "industry": "Identity Verification / Cybersecurity",
        "company_size": "startup",
        "website": "https://withpersona.com",
        "slug": "persona",
        "description": (
            "Persona is an identity verification platform used by companies like OpenAI, Coursera, "
            "and Lime to fight fraud, stay compliant, and build trust. Series D at $2B valuation. "
            "~650 employees. Backed by Index Ventures and Founders Fund.\n\n"
            "Source: Index Ventures + Founders Fund Portfolio | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Rick Song", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/rick-song-25198b24"},
            {"name": "Charles Yeh", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/charlesyeh"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 10500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Ruby, Python, TypeScript, or Go",
                    "Interest in identity verification, fraud prevention, or security",
                    "Experience with web application development",
                ],
                "description": (
                    "Software Engineer Intern at Persona — Summer 2026\n\n"
                    "Build identity verification products used by OpenAI, Coursera, and "
                    "hundreds of other companies. Work on fraud detection, compliance, "
                    "and trust infrastructure at the $2B identity platform. ~$54.81/hr.\n\n"
                    "Source: Index Ventures + Founders Fund Portfolio / Persona Careers"
                ),
            },
            {
                "title": "Product Design Intern (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.PRODUCT_DESIGNER,
                "location": "San Francisco, CA",
                "salary_min": 7500,
                "salary_max": 9500,
                "requirements": [
                    "Currently pursuing a degree in Design, HCI, or related field",
                    "Strong portfolio demonstrating product design skills",
                    "Proficiency with Figma",
                    "Interest in identity, security, and trust products",
                ],
                "description": (
                    "Product Design Intern at Persona — Summer 2026\n\n"
                    "Design identity verification experiences used by millions of end users. "
                    "Work on flows for ID verification, fraud detection, and compliance "
                    "at the $2B identity platform in San Francisco.\n\n"
                    "Source: Index Ventures + Founders Fund Portfolio / Persona Careers"
                ),
            },
        ],
    },

    # ── 5. Gecko Robotics (Founders Fund) ──
    {
        "company_name": "Gecko Robotics",
        "email": "careers@geckorobotics.com",
        "name": "Jake Loosararian",
        "industry": "Robotics / Defense Tech / Industrial Inspection",
        "company_size": "startup",
        "website": "https://geckorobotics.com",
        "slug": "gecko-robotics",
        "description": (
            "Gecko Robotics uses wall-climbing inspection robots and AI analytics to help "
            "organizations inspect critical infrastructure like power plants, pipelines, and "
            "storage tanks. Serves US military and Fortune 500 industrials. Valued at $1.25B. "
            "~300 employees.\n\n"
            "Source: Founders Fund Portfolio | HQ: Pittsburgh, PA"
        ),
        "founders": [
            {"name": "Jake Loosararian", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/jake-loosararian-23981350"},
            {"name": "Troy Demmer", "title": "Co-Founder & Chief Product Officer", "linkedin": "https://linkedin.com/in/troy-demmer-27037526"},
        ],
        "jobs": [
            {
                "title": "Field Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Pittsburgh, PA",
                "salary_min": 9000,
                "salary_max": 11000,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Robotics, or related field",
                    "Strong programming skills in Python, C++, or Rust",
                    "Interest in robotics, industrial IoT, or infrastructure inspection",
                    "Ability to work on-site in Pittsburgh for 10-12 weeks",
                ],
                "description": (
                    "Field Software Engineer Intern at Gecko Robotics — Summer 2026\n\n"
                    "Build software for wall-climbing inspection robots used on power plants, "
                    "pipelines, and military infrastructure. Work at the intersection of "
                    "robotics, AI, and critical infrastructure. Unicorn valued at $1.25B. ~$60/hr.\n\n"
                    "Source: Founders Fund Portfolio / Gecko Robotics Careers"
                ),
            },
        ],
    },

    # ── 6. Loop (Index Ventures + Founders Fund) ──
    {
        "company_name": "Loop",
        "email": "careers@loop.us",
        "name": "Matt McKinney",
        "industry": "Supply Chain / Logistics / FinTech",
        "company_size": "startup",
        "website": "https://loop.us",
        "slug": "loop-logistics",
        "description": (
            "Loop is a logistics audit and payment platform using domain-driven AI to manage "
            "supply chain billing, freight invoicing, and transportation spend for enterprise "
            "shippers and 3PLs. Backed by Index Ventures and Founders Fund. ~100 employees.\n\n"
            "Source: Index Ventures + Founders Fund Portfolio | HQ: Chicago, IL"
        ),
        "founders": [
            {"name": "Matt McKinney", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/mattlmckinney"},
            {"name": "Shaosu Liu", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/shaosu"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern, Full-Stack (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Columbus, OH",
                "salary_min": 4500,
                "salary_max": 5500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Experience with full-stack development (React, Node.js, Python)",
                    "Interest in logistics, supply chain, or fintech",
                    "Columbus, OH preferred; remote option available",
                ],
                "description": (
                    "Software Engineer Intern, Full-Stack at Loop — Summer 2026\n\n"
                    "Build AI-powered logistics and payment tools that help enterprise shippers "
                    "manage supply chain billing. Full-stack role working on both frontend and "
                    "backend. Index Ventures + Founders Fund backed.\n\n"
                    "Source: Index Ventures + Founders Fund Portfolio / Loop Careers"
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

    membership = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(membership)

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
        print("ERROR: No companies or jobs defined.")
        sys.exit(1)

    print("=" * 60)
    print(f"Seeding Intern Jobs — {FIRM_NAME}")
    print("=" * 60)

    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)

    total_companies = 0
    total_jobs = 0
    errors = []

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
