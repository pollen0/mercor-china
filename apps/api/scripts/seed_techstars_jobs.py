#!/usr/bin/env python3
"""
Seed intern jobs from Techstars portfolio companies.

FIRM: Techstars
JOB BOARD: https://jobs.techstars.com
SCRIPT ID: techstars

Techstars is one of the largest startup accelerators (~4000+ companies).
Their job board lists 813+ jobs. Most portfolio companies with intern
programs are larger alumni (public companies, unicorns).

New companies: DigitalOcean, Chainalysis, Remitly, Socure, Laminar, Vermeer
Already in DB (skipped): Zipline (3 intern jobs), GlossGenius (2 intern jobs)
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
FIRM_NAME = "Techstars"
SCRIPT_ID = "techstars"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. DigitalOcean ──
    {
        "company_name": "DigitalOcean",
        "email": "careers@digitalocean.com",
        "name": "Paddy Srinivasan",
        "industry": "Cloud Infrastructure / Developer Tools",
        "company_size": "enterprise",
        "website": "https://www.digitalocean.com",
        "slug": "digitalocean",
        "description": (
            "DigitalOcean is a cloud infrastructure provider that simplifies "
            "cloud computing for developers and businesses. The platform offers "
            "scalable compute, managed databases, Kubernetes, and app deployment "
            "tools used by millions of developers worldwide.\n\n"
            "Fund: Techstars (Boulder 2012) | HQ: New York (Remote-first)"
        ),
        "founders": [
            {"name": "Ben Uretsky", "title": "Co-Founder", "linkedin": ""},
            {"name": "Moisey Uretsky", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 7800,
                "salary_max": 9360,
                "requirements": [
                    "3rd/4th year CS or Engineering student graduating 2025-2026",
                    "Experience with REST or gRPC API development",
                    "Familiarity with Docker and Kubernetes",
                    "Go experience or willingness to learn",
                    "Knowledge of cloud infrastructure and MySQL",
                ],
                "description": (
                    "Software Engineer Intern at DigitalOcean (Summer 2026)\n\n"
                    "Design and develop production-level code, draft engineering design "
                    "documents, build backend services primarily in Go using REST/gRPC APIs. "
                    "Project areas include database enhancement, infrastructure building, "
                    "UX/UI, deployment automation, and data engineering. 12-week program, "
                    "June-August. Remote-eligible from hub cities: Austin, Boston, Denver, "
                    "SF Bay, Seattle.\n\n"
                    "$45-$54/hr | Remote from hub cities (NYSE: DOCN)\n\n"
                    "Source: https://builtin.com/job/software-engineer-intern/4214492"
                ),
            },
        ],
    },

    # ── 2. Chainalysis ──
    {
        "company_name": "Chainalysis",
        "email": "careers@chainalysis.com",
        "name": "Jonathan Levin",
        "industry": "Blockchain Analytics / Cybersecurity",
        "company_size": "startup",
        "website": "https://www.chainalysis.com",
        "slug": "chainalysis",
        "description": (
            "Chainalysis is the blockchain analytics company. The platform provides "
            "data, software, services, and research to government agencies, exchanges, "
            "financial institutions, and insurance/cybersecurity companies across 70+ "
            "countries. Chainalysis data powers investigation, compliance, and market "
            "intelligence tools.\n\n"
            "Fund: Techstars | HQ: New York"
        ),
        "founders": [
            {"name": "Michael Gronager", "title": "Co-Founder", "linkedin": ""},
            {"name": "Jonathan Levin", "title": "Co-Founder & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8667,
                "salary_max": 8667,
                "requirements": [
                    "Pursuing degree in Computer Science, Engineering, or related field",
                    "Analytic mindset with strong problem-solving skills",
                    "Proficiency in at least one programming language",
                    "Interest in blockchain technology and cryptocurrency",
                    "Collaborative nature and rigorous work ethic",
                ],
                "description": (
                    "Software Engineering Intern at Chainalysis (Summer 2026)\n\n"
                    "Work alongside the R&D team building investigation and compliance "
                    "products that help track cryptocurrency fraud, money laundering, "
                    "and human trafficking. Contribute to databases, analysis tools, "
                    "and blockchain analytics products used by law enforcement worldwide.\n\n"
                    "~$50/hr | New York, NY\n\n"
                    "Source: https://www.chainalysis.com/careers/job-openings/"
                ),
            },
            {
                "title": "Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "New York, NY",
                "salary_min": 8667,
                "salary_max": 8667,
                "requirements": [
                    "Pursuing degree in Data Science, Economics, CS, or related field",
                    "Data analytics and research experience",
                    "Creative problem-solving approach",
                    "Ability to navigate blockchain analytic tools",
                    "Interest in cryptocurrency and financial crime research",
                ],
                "description": (
                    "Research Intern at Chainalysis (Summer 2026)\n\n"
                    "Join the R&D team conducting research on blockchain data, "
                    "cryptocurrency trends, and financial crime patterns. Participate "
                    "in real-life responsibilities alongside full-time research teams, "
                    "with potential for publication credit.\n\n"
                    "~$50/hr | New York, NY\n\n"
                    "Source: https://startup.jobs/research-intern-chainalysis-1752807"
                ),
            },
        ],
    },

    # ── 3. Remitly ──
    {
        "company_name": "Remitly",
        "email": "careers@remitly.com",
        "name": "Matt Oppenheimer",
        "industry": "FinTech / Digital Remittances",
        "company_size": "enterprise",
        "website": "https://www.remitly.com",
        "slug": "remitly",
        "description": (
            "Remitly is a digital financial services provider that transforms the "
            "lives of immigrants and their families by providing the most trusted "
            "financial products and services on the planet. The largest independent "
            "international money transmitter in the US.\n\n"
            "Fund: Techstars (Seattle 2011) | HQ: Seattle (NASDAQ: RELY)"
        ),
        "founders": [
            {"name": "Matt Oppenheimer", "title": "CEO & Co-Founder", "linkedin": ""},
            {"name": "Josh Hug", "title": "Co-Founder", "linkedin": ""},
            {"name": "Shivaas Gulati", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Development Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Seattle, WA",
                "salary_min": 8147,
                "salary_max": 8147,
                "requirements": [
                    "Pursuing BS or MS in Computer Science or related field",
                    "Knowledge of data structures, algorithms, and complexity analysis",
                    "Some knowledge of databases and back-end development",
                    "Strong problem-solving skills",
                    "Ability to take ownership of projects under mentor guidance",
                ],
                "description": (
                    "Software Development Engineer Intern at Remitly (Summer 2026)\n\n"
                    "Report to a senior engineer and contribute to a collaborative product "
                    "development team. Work on meaningful and impactful projects over ~3 months. "
                    "Take ownership of projects, solve complex technical problems, and learn "
                    "from experienced engineers at a company processing billions in remittances.\n\n"
                    "$47/hr | Seattle, WA (in-office)\n\n"
                    "Source: https://remitly.wd5.myworkdayjobs.com/en-US/Remitly_Careers/job/Software-Development-Engineer-Intern_R_101195"
                ),
            },
        ],
    },

    # ── 4. Socure ──
    {
        "company_name": "Socure",
        "email": "careers@socure.com",
        "name": "Johnny Ayers",
        "industry": "Identity Verification / AI / Cybersecurity",
        "company_size": "startup",
        "website": "https://www.socure.com",
        "slug": "socure",
        "description": (
            "Socure is the leading platform for digital identity verification, "
            "using AI and machine learning to verify identities in real-time for "
            "fraud prevention. Trusted by top banks, fintechs, and government "
            "agencies to verify over 2 billion identities.\n\n"
            "Fund: Techstars | HQ: New York (Remote-first)"
        ),
        "founders": [
            {"name": "Johnny Ayers", "title": "Founder & CEO", "linkedin": ""},
            {"name": "Sunil Madhu", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Data Science Intern - Fraud Prevention (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Remote, US",
                "salary_min": 7000,
                "salary_max": 8667,
                "requirements": [
                    "Pursuing BS, MS, or PhD in Data Science, CS, Statistics, or related field",
                    "Proficiency in Python (Pandas, NumPy)",
                    "Familiarity with ML frameworks (scikit-learn, TensorFlow, PyTorch)",
                    "Experience handling large datasets and feature engineering",
                    "Interest in fraud detection or anomaly detection preferred",
                ],
                "description": (
                    "Data Science Intern (Fraud Prevention) at Socure (Summer 2026)\n\n"
                    "Work alongside data scientists and engineers to develop and optimize "
                    "methods for fraud detection and device recognition. Analyze large datasets, "
                    "extract insights, detect patterns. Develop and evaluate features derived "
                    "from browser, app, and IP-based activity. Assist in research and "
                    "implementation of new ML algorithms. Potential for full-time offer.\n\n"
                    "Remote (US)\n\n"
                    "Source: https://socure.wd1.myworkdayjobs.com/en-US/SocureCareers/job/Data-Science-Intern---DI_JR512"
                ),
            },
            {
                "title": "Data Science Intern - Document Verification (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Remote, US",
                "salary_min": 7000,
                "salary_max": 8667,
                "requirements": [
                    "Pursuing BS, MS, or PhD in Data Science, CS, or related field",
                    "Proficiency in Python and ML frameworks",
                    "Experience with computer vision or NLP preferred",
                    "Strong analytical and communication skills",
                    "Interest in identity verification and document analysis",
                ],
                "description": (
                    "Data Science Intern (Document Verification) at Socure (Summer 2026)\n\n"
                    "Work on ML models for document verification, using computer vision "
                    "and NLP to detect fraudulent identity documents. Contribute to "
                    "Socure's DocV product that verifies government-issued IDs.\n\n"
                    "Remote (US)\n\n"
                    "Source: https://remotive.com/remote/jobs/data/data-science-intern-docv-1397629"
                ),
            },
        ],
    },

    # ── 5. Laminar ──
    {
        "company_name": "Laminar",
        "email": "careers@runlaminar.com",
        "name": "Annie Lu",
        "industry": "CleanTech / Industrial IoT / AI",
        "company_size": "startup",
        "website": "https://runlaminar.com",
        "slug": "laminar",
        "description": (
            "Laminar (formerly H2Ok Innovations) uses proprietary spectral sensing "
            "and agentic AI to automate CPG manufacturing, reducing downtime and "
            "improving sustainability. Named Unilever's 2023 Startup of the Year "
            "supplier. Based at Greentown Labs.\n\n"
            "Fund: Techstars | HQ: Somerville, MA"
        ),
        "founders": [
            {"name": "Annie Lu", "title": "CEO & Co-Founder", "linkedin": ""},
            {"name": "David Lu", "title": "CTO & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Somerville, MA",
                "salary_min": 4000,
                "salary_max": 4680,
                "requirements": [
                    "Pursuing degree in Software Engineering, CS, or related field",
                    "Ability to thrive in fast-paced team environments",
                    "Startup mindset with motivation to drive positive change",
                    "Interest in cleantech and manufacturing innovation",
                ],
                "description": (
                    "Software Engineering Intern at Laminar (Summer 2026)\n\n"
                    "Work on software enabling sensor and gateway products to generate "
                    "customer insights for CPG manufacturing. Collaborate with hardware "
                    "and software engineers on R&D. Implement data sharing, analysis, and "
                    "visualization solutions. Based at Greentown Labs in Somerville, MA. "
                    "Application deadline: March 6. Potential for full-time conversion.\n\n"
                    "$25-$27/hr | Somerville, MA (at Greentown Labs)\n\n"
                    "Source: https://runlaminar.com/careers/bf35fd58-611e-4ecc-83f6-fb8bd7c3d8af"
                ),
            },
        ],
    },

    # ── 6. Vermeer ──
    {
        "company_name": "Vermeer",
        "email": "careers@getvermeer.com",
        "name": "Brian Streem",
        "industry": "Defense Technology / Robotics",
        "company_size": "startup",
        "website": "https://www.getvermeer.com",
        "slug": "vermeer-defense",
        "description": (
            "Vermeer is an American-Ukrainian defense tech startup building autonomous "
            "robotic systems for military applications. The company develops multi-axis "
            "robotic arms, computer vision systems, and autonomous drone integrations. "
            "Recently raised $10M Series A led by Draper Associates.\n\n"
            "Fund: Techstars | HQ: Brooklyn, NY"
        ),
        "founders": [
            {"name": "Brian Streem", "title": "Founder & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Robotics Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Brooklyn, NY",
                "salary_min": 3467,
                "salary_max": 6933,
                "requirements": [
                    "Pursuing BS or MS in Robotics, ME, EE, or CS (3rd/4th year min)",
                    "Proficiency in Python or C++",
                    "Strong understanding of linear algebra, kinematics, and coordinate transforms",
                    "Experience with single-board computers (Jetson Orin, Raspberry Pi)",
                    "US Citizenship required",
                ],
                "description": (
                    "Robotics Engineering Intern at Vermeer (Summer 2026)\n\n"
                    "8-12 week in-person internship in Brooklyn, NY. Two tracks: "
                    "Track A (Mechatronics) — CAD, electromechanical integration, rapid "
                    "prototyping. Track B (Software & Perception) — ROS/ROS2, OpenCV, "
                    "Robot Arm SDKs. Work on multi-axis robotic arms, computer vision, "
                    "and autonomous drone integrations. Full access to Brooklyn lab. "
                    "Designs go from prototype to flight-testing by summer's end. "
                    "Includes NYC metro card.\n\n"
                    "$20-$40/hr + NYC metro card | Brooklyn, NY (in-person)\n\n"
                    "Source: https://jobs.techstars.com/companies/vermeer/jobs/66636363-robotics-engineering-intern"
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
