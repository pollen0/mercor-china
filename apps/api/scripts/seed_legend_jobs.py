#!/usr/bin/env python3
"""
Seed intern jobs from Legend Capital (君联资本) portfolio companies into Pathway.

Legend Capital is a China-headquartered VC firm (founded 2001, $10B+ AUM) with
a smaller US portfolio. This script covers their US-based portfolio companies
with confirmed or estimated internship positions.

NOTE: Legend Capital's portfolio is predominantly China-focused (~600 companies).
Only a handful have US operations with intern openings. This script covers:
  - Pony.ai (Fremont, CA) — confirmed intern listings
  - GrubMarket (San Francisco, CA) — estimated based on active SWE hiring
  - Bionano Genomics (San Diego, CA) — confirmed intern listing
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
FIRM_NAME = "Legend Capital"
SCRIPT_ID = "legend"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Pony.ai ──
    {
        "company_name": "Pony.ai",
        "email": "careers@pony.ai",
        "name": "James Peng",
        "industry": "AI / Autonomous Driving",
        "company_size": "startup",
        "website": "https://pony.ai",
        "slug": "pony-ai",
        "description": (
            "Pony.ai is a global autonomous mobility leader developing full-stack "
            "self-driving technology. Founded in 2016, the company builds a vehicle-agnostic "
            "'Virtual Driver' platform for perception, localization, planning, and control, "
            "and operates robotaxi services. Recently announced mass production of robotaxis "
            "with Toyota. Publicly traded on NASDAQ (PONY).\n\n"
            "Fund: Legend Capital (Series A co-lead) | HQ: Fremont, CA"
        ),
        "founders": [
            {"name": "James Peng", "title": "CEO & Chairman", "linkedin": ""},
            {"name": "Tiancheng Lou", "title": "CTO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "ML Engineer Intern, ML Runtime & Optimization (Spring 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Fremont, CA",
                "salary_min": 7000,
                "salary_max": 10000,
                "requirements": [
                    "Currently enrolled in a Master's or PhD program in CS, ML, Robotics, or related field",
                    "Strong programming skills in C/C++ or Python",
                    "Solid understanding of CPU/GPU execution models, memory hierarchies, and performance tradeoffs",
                    "Experience with benchmarking, profiling, and performance validation",
                    "Parallel programming experience (CUDA, ROCm, Triton, Cutlass) preferred",
                ],
                "description": (
                    "ML Engineer Intern at Pony.ai — ML Runtime & Optimization\n\n"
                    "Develop technologies that enhance the training and inference of AI models "
                    "used in autonomous driving systems. Work across the entire AI framework/compiler "
                    "stack (e.g. Torch, CUDA, TensorRT). Analyze performance, cost, and energy "
                    "tradeoffs in autonomous systems. Collaborate with hardware and software teams "
                    "on next-generation compute platforms.\n\n"
                    "Fully onsite in Fremont, CA. Minimum 3-month commitment.\n\n"
                    "Source: https://jobright.ai/jobs/info/69448aac94730b739877c3c8"
                ),
            },
            {
                "title": "Research Intern, Deep Learning (Spring 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Fremont, CA",
                "salary_min": 7000,
                "salary_max": 10000,
                "requirements": [
                    "Currently pursuing a Master's or PhD in Computer Science, Machine Learning, Robotics, or related field",
                    "Strong background in deep learning, including model design, training, and evaluation",
                    "Proficiency in Python and C++",
                    "Experience working with large-scale datasets and data pipeline management",
                    "Computer vision background preferred",
                ],
                "description": (
                    "Research Intern (Deep Learning) at Pony.ai\n\n"
                    "Conduct cutting-edge research in deep learning for autonomous driving. "
                    "Work on model design, training, and evaluation for perception and planning "
                    "systems. Collaborate with world-class researchers and engineers on next-generation "
                    "autonomous driving AI.\n\n"
                    "Fully onsite in Fremont, CA. Minimum 3-month commitment.\n\n"
                    "Source: https://apply.workable.com/pony-dot-ai/j/4C1F53EF5D/"
                ),
            },
        ],
    },

    # ── GrubMarket ──
    {
        "company_name": "GrubMarket",
        "email": "careers@grubmarket.com",
        "name": "Mike Xu",
        "industry": "AI / Food Tech / Supply Chain",
        "company_size": "startup",
        "website": "https://www.grubmarket.com",
        "slug": "grubmarket",
        "description": (
            "GrubMarket is an AI-powered technology enabler and digital transformer of the "
            "American food supply chain industry. Valued at $4.5B, it is one of the largest "
            "private food tech companies in the world, with 12,000 employees and customers in "
            "70+ countries. Named to CNBC Disruptor 50 (2025). CEO Mike Xu recognized by "
            "Goldman Sachs as one of the Most Exceptional Entrepreneurs of 2024.\n\n"
            "Fund: Legend Capital (Series A, 2015) | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Mike Xu", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/mikexu11"},
        ],
        "jobs": [
            {
                "title": "Full Stack Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Strong programming skills in Python, JavaScript/TypeScript, or similar",
                    "Experience with web frameworks (React, Node.js, Django, or similar)",
                    "Interest in food tech, supply chain, or e-commerce platforms",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Full Stack Software Engineering Intern at GrubMarket\n\n"
                    "Help build and enhance GrubMarket's AI-powered e-commerce platform and "
                    "next-generation supply chain management system. Work alongside experienced "
                    "engineers on real features that serve customers in 70+ countries.\n\n"
                    "GrubMarket is actively hiring Full Stack Software Engineers in SF. "
                    "Salary estimated based on comparable Bay Area startup internships.\n\n"
                    "Source: https://www.grubmarket.com/jobs/openings"
                ),
            },
        ],
    },

    # ── Bionano Genomics ──
    {
        "company_name": "Bionano Genomics",
        "email": "careers@bionano.com",
        "name": "Erik Holmlin",
        "industry": "Biotech / Genomics",
        "company_size": "startup",
        "website": "https://bionano.com",
        "slug": "bionano-genomics",
        "description": (
            "Bionano Genomics develops nanoscale imaging and analytics platforms to analyze DNA, "
            "specializing in genome mapping technology to reach the inaccessible genome. Their "
            "optical genome mapping (OGM) technology enables researchers and clinicians to see "
            "large structural variations in chromosomes that other technologies miss.\n\n"
            "Fund: Legend Capital (Series C co-lead, $53M) | HQ: San Diego, CA"
        ),
        "founders": [
            {"name": "Erik Holmlin", "title": "President & CEO", "linkedin": "https://linkedin.com/in/eholmlin"},
        ],
        "jobs": [
            {
                "title": "Software Quality Intern (2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.QA_ENGINEER,
                "location": "San Diego, CA",
                "salary_min": 4000,
                "salary_max": 6000,
                "requirements": [
                    "Currently enrolled in a bachelor's level or equivalent program",
                    "Written and spoken proficiency in English",
                    "Experience with Visual Studio, WebStorm, and MS Office",
                    "Knowledge of Windows, Linux, and Mac OS operating systems",
                    "Bioengineering background preferred but not required",
                ],
                "description": (
                    "Software Quality Intern at Bionano Genomics\n\n"
                    "Support quality assurance for a genome mapping instrument used in DNA analysis. "
                    "Scrutinize novel genomic analyses and visualizations, genomic variation data, "
                    "and the customer experience. Work with cutting-edge biotech software in a "
                    "fast-paced environment.\n\n"
                    "Internships conclude with project presentations. Salary estimated based on "
                    "comparable San Diego biotech internships.\n\n"
                    "Source: https://hired.com/job/software-quality-internship"
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
