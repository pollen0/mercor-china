#!/usr/bin/env python3
"""
Seed intern jobs from Technology Crossover Ventures (TCV) portfolio companies.

TCV portfolio: https://tcv.com/companies/
Job board: https://portfoliojobs.tcv.com/

Companies added:
  NEW: Spotify, CCC Intelligent Solutions, Hinge Health, Attentive, OneTrust
  ADDITIONAL_JOBS: (none — existing DB companies had no new unique intern roles found)

Run with: cd apps/api && python -m scripts.seed_tcv_jobs
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
FIRM_NAME = "Technology Crossover Ventures (TCV)"
SCRIPT_ID = "tcv"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Spotify ──
    {
        "company_name": "Spotify",
        "email": "careers@spotify.com",
        "name": "Daniel Ek",
        "industry": "Music / Streaming / Technology",
        "company_size": "enterprise",
        "website": "https://spotify.com",
        "slug": "spotify",
        "description": (
            "Spotify is the world's largest audio streaming platform with over 600 million users. "
            "The company provides access to millions of songs, podcasts, and audiobooks from creators around the world.\n\n"
            "Fund: TCV | HQ: New York, NY (US HQ)"
        ),
        "founders": [
            {"name": "Daniel Ek", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/danielek"},
            {"name": "Martin Lorentzon", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8000,
                "salary_max": 8500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Strong programming skills in Java, Python, or similar",
                    "Familiarity with distributed systems or backend development",
                    "Available for 10-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Spotify.\n\n"
                    "Work on the platform that powers music streaming for 600M+ users. "
                    "Intern projects span backend services, data infrastructure, mobile apps, "
                    "and machine learning systems.\n\n"
                    "Source: https://www.lifeatspotify.com/students"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "New York, NY",
                "salary_min": 8000,
                "salary_max": 8500,
                "requirements": [
                    "Pursuing a degree in Data Science, Statistics, CS, or related field",
                    "Experience with Python, SQL, and statistical analysis",
                    "Familiarity with machine learning frameworks (TensorFlow, PyTorch)",
                    "Interest in recommendation systems or audio ML",
                ],
                "description": (
                    "Data Science Intern at Spotify.\n\n"
                    "Work on data-driven projects including recommendation algorithms, "
                    "user behavior analysis, and audio content understanding. "
                    "Spotify's data team powers personalization for hundreds of millions of users.\n\n"
                    "Source: https://www.lifeatspotify.com/students"
                ),
            },
        ],
    },

    # ── CCC Intelligent Solutions ──
    {
        "company_name": "CCC Intelligent Solutions",
        "email": "careers@cccis.com",
        "name": "Githesh Ramamurthy",
        "industry": "Insurance / AI / SaaS",
        "company_size": "enterprise",
        "website": "https://cccis.com",
        "slug": "ccc-intelligent-solutions",
        "description": (
            "CCC Intelligent Solutions is a SaaS platform connecting the insurance and automotive industries. "
            "The company uses AI and IoT to digitize and automate insurance claims, repair workflows, "
            "and vehicle data analytics. Publicly traded (CCCS) with 35,000+ customers.\n\n"
            "Fund: TCV | HQ: Chicago, IL"
        ),
        "founders": [
            {"name": "Githesh Ramamurthy", "title": "Chairman & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern - Workflow (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 4000,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Java, C#, or Python",
                    "Interest in enterprise SaaS or workflow automation",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Software Engineering Intern (Workflow) at CCC Intelligent Solutions.\n\n"
                    "Build and enhance workflow automation tools that power insurance claims processing "
                    "for thousands of customers.\n\n"
                    "Source: https://cccis.wd1.myworkdayjobs.com/CCCIntelligentSolutions"
                ),
            },
            {
                "title": "Software Engineering Intern - Parts (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 4000,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with backend development (Java, Python, or Go)",
                    "Interest in data platforms or e-commerce systems",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Software Engineering Intern (Parts) at CCC Intelligent Solutions.\n\n"
                    "Work on the parts marketplace and supply chain platform that connects "
                    "auto repair shops with parts suppliers.\n\n"
                    "Source: https://cccis.wd1.myworkdayjobs.com/CCCIntelligentSolutions"
                ),
            },
            {
                "title": "Site Reliability Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 4000,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science, IT, or related field",
                    "Familiarity with Linux, cloud platforms (AWS/GCP), and CI/CD",
                    "Interest in site reliability, DevOps, or infrastructure",
                    "Scripting experience in Python or Bash",
                ],
                "description": (
                    "Site Reliability Engineering Intern at CCC Intelligent Solutions.\n\n"
                    "Help maintain and improve the reliability of CCC's SaaS platform "
                    "serving 35,000+ customers across the insurance ecosystem.\n\n"
                    "Source: https://cccis.wd1.myworkdayjobs.com/CCCIntelligentSolutions"
                ),
            },
            {
                "title": "Platform Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 4000,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with cloud services (AWS, GCP, or Azure)",
                    "Interest in platform engineering and developer tooling",
                    "Familiarity with containerization (Docker, Kubernetes) is a plus",
                ],
                "description": (
                    "Platform Engineering Intern at CCC Intelligent Solutions.\n\n"
                    "Work on the core platform infrastructure that powers CCC's AI-driven "
                    "insurance technology solutions.\n\n"
                    "Source: https://cccis.wd1.myworkdayjobs.com/CCCIntelligentSolutions"
                ),
            },
        ],
    },

    # ── Hinge Health ──
    {
        "company_name": "Hinge Health",
        "email": "careers@hingehealth.com",
        "name": "Daniel Perez",
        "industry": "Healthcare / Digital Therapeutics",
        "company_size": "startup",
        "website": "https://hingehealth.com",
        "slug": "hinge-health",
        "description": (
            "Hinge Health is the leading digital musculoskeletal (MSK) clinic, providing "
            "personalized exercise therapy and behavioral health coaching through a mobile app "
            "and wearable sensors. Serves 1,500+ employer and health plan customers.\n\n"
            "Fund: TCV | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Daniel Perez", "title": "CEO & Co-Founder", "linkedin": ""},
            {"name": "Gabriel Mecklenburg", "title": "Executive Chairman & Co-Founder", "linkedin": ""},
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
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Proficiency in Python, TypeScript, or similar languages",
                    "Interest in healthcare technology or digital health",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Software Engineering Intern at Hinge Health.\n\n"
                    "Build digital health solutions that help millions of people manage "
                    "chronic pain and musculoskeletal conditions. Work on mobile apps, "
                    "backend services, or data infrastructure.\n\n"
                    "Source: https://www.hingehealth.com/careers/"
                ),
            },
        ],
    },

    # ── Attentive ──
    {
        "company_name": "Attentive",
        "email": "careers@attentivemobile.com",
        "name": "Brian Long",
        "industry": "Marketing / SMS / E-commerce",
        "company_size": "startup",
        "website": "https://attentive.com",
        "slug": "attentive",
        "description": (
            "Attentive is the leading AI-powered SMS and email marketing platform for e-commerce brands. "
            "The platform helps 8,000+ brands drive revenue through personalized text message marketing "
            "and intelligent audience targeting.\n\n"
            "Fund: TCV | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Brian Long", "title": "Co-Founder & Chairman", "linkedin": ""},
            {"name": "Andrew Jones", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Java, Python, or TypeScript",
                    "Interest in marketing technology or distributed systems",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Software Engineering Intern at Attentive.\n\n"
                    "Help build the AI-powered messaging platform used by 8,000+ e-commerce brands. "
                    "Work on real-time messaging infrastructure, personalization engines, "
                    "or audience targeting systems.\n\n"
                    "Source: https://www.attentive.com/careers"
                ),
            },
        ],
    },

    # ── OneTrust ──
    {
        "company_name": "OneTrust",
        "email": "careers@onetrust.com",
        "name": "Kabir Barday",
        "industry": "Privacy / Compliance / SaaS",
        "company_size": "startup",
        "website": "https://onetrust.com",
        "slug": "onetrust",
        "description": (
            "OneTrust is the trust intelligence platform that helps organizations implement "
            "privacy, security, and AI governance programs. Used by 14,000+ customers globally "
            "to manage compliance with GDPR, CCPA, and other regulations.\n\n"
            "Fund: TCV | HQ: Atlanta, GA"
        ),
        "founders": [
            {"name": "Kabir Barday", "title": "Founder & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Atlanta, GA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing a BS/MS in Computer Science or related field",
                    "Experience with Java, Python, or JavaScript/TypeScript",
                    "Interest in privacy, security, or compliance technology",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Software Engineering Intern at OneTrust.\n\n"
                    "Build trust intelligence solutions that help 14,000+ organizations "
                    "manage privacy, security, and AI governance compliance. "
                    "Work on platform features, APIs, or data processing pipelines.\n\n"
                    "Source: https://www.onetrust.com/careers/"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# TCV portfolio overlaps with Tiger Global (Toast, Brex, GitLab) and others
# (Strava, Instacart) but no new unique intern roles were found for those.

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
