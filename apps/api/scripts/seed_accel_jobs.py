#!/usr/bin/env python3
"""
Seed intern jobs from Accel portfolio companies.

Accel is one of the leading global VC firms, founded in 1983, with 1,100+ investments
including Dropbox, CrowdStrike, Atlassian, Spotify, Scale AI, Squarespace, DocuSign,
Qualtrics, and many more.

SCRIPT ID: accel
RUN: cd apps/api && python -m scripts.seed_accel_jobs
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
FIRM_NAME = "Accel"
SCRIPT_ID = "accel"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Dropbox ──
    {
        "company_name": "Dropbox",
        "email": "careers@dropbox.com",
        "name": "Drew Houston",
        "industry": "Cloud Storage / Productivity",
        "company_size": "startup",
        "website": "https://www.dropbox.com",
        "slug": "dropbox",
        "description": (
            "Dropbox is a smart workspace that brings content, tools, and teams together. "
            "Over 700 million users in 180+ countries use Dropbox for file storage, sharing, "
            "and collaboration. Virtual First work model. Public on Nasdaq.\n\n"
            "Fund: Accel | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Drew Houston", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/drewhouston"},
            {"name": "Arash Ferdowsi", "title": "Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8000,
                "salary_max": 9500,
                "requirements": [
                    "Current underclassman with anticipated graduation Fall/Winter 2027 - Spring 2028",
                    "Studying Computer Science or related field",
                    "Strong programming skills and problem-solving ability",
                    "Available for a 12-week full-time summer internship (40 hrs/week)",
                ],
                "description": (
                    "Software Engineer Intern at Dropbox — Summer 2026\n\n"
                    "Join Dropbox's Virtual First work environment. Work on real projects that "
                    "impact 700M+ users. Benefits include flexible PTO, paid holidays, and perks "
                    "allowance for wellness and development. Compensation: ~$55/hr.\n\n"
                    "Source: https://jobs.accel.com/companies/dropbox/jobs/57286220-software-engineer-intern-summer-2026"
                ),
            },
        ],
    },
    # ── 2. CrowdStrike ──
    {
        "company_name": "CrowdStrike",
        "email": "careers@crowdstrike.com",
        "name": "George Kurtz",
        "industry": "Cybersecurity / AI",
        "company_size": "startup",
        "website": "https://www.crowdstrike.com",
        "slug": "crowdstrike",
        "description": (
            "CrowdStrike is a global cybersecurity leader providing cloud-delivered endpoint "
            "and workload protection. The Falcon platform uses AI to stop breaches in real time "
            "across endpoints, cloud workloads, identity, and data. Public on Nasdaq.\n\n"
            "Fund: Accel | HQ: Austin, TX"
        ),
        "founders": [
            {"name": "George Kurtz", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/georgekurtz"},
            {"name": "Dmitri Alperovitch", "title": "Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Sunnyvale, CA",
                "salary_min": 6600,
                "salary_max": 7800,
                "requirements": [
                    "Currently enrolled in a Bachelor's or Master's program in CS, Engineering, or related field",
                    "Strong programming skills in Python, Go, C/C++, or Java",
                    "Interest in cybersecurity and cloud-native architectures",
                    "Available for a 12-week onsite internship at Sunnyvale, CA or Redmond, WA",
                ],
                "description": (
                    "Software Engineer Intern at CrowdStrike — Summer 2026\n\n"
                    "Work on the Falcon platform, protecting millions of endpoints worldwide. "
                    "All engineering internships are onsite at Sunnyvale, CA or Redmond, WA. "
                    "12-week program, 40 hours/week. Compensation: $38-45/hr.\n\n"
                    "Source: https://crowdstrike.wd5.myworkdayjobs.com/crowdstrikecareers/job/USA---Redmond-WA/Software-Engineer-Intern---Summer-2026_R26636"
                ),
            },
        ],
    },
    # ── 3. Scale AI ──
    {
        "company_name": "Scale AI",
        "email": "careers@scale.com",
        "name": "Alexandr Wang",
        "industry": "AI / Data Infrastructure",
        "company_size": "startup",
        "website": "https://scale.com",
        "slug": "scale-ai",
        "description": (
            "Scale AI is an AI infrastructure company providing data labeling, model evaluation, "
            "and AI application development. Trusted by the US military, OpenAI, Meta, and "
            "leading enterprises. Valued at $14B+.\n\n"
            "Fund: Accel | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Alexandr Wang", "title": "Founder", "linkedin": "https://linkedin.com/in/alexandrwang"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 10400,
                "requirements": [
                    "Graduation date in Fall 2026 or Spring 2027 with a Bachelor's in CS, EECS, CE, or Statistics",
                    "Strong programming skills and systems thinking",
                    "Interest in AI, data infrastructure, and large-scale systems",
                    "Available for a Summer 2026 internship (May/June start)",
                ],
                "description": (
                    "Software Engineering Intern at Scale AI — Summer 2026\n\n"
                    "Build the infrastructure powering the AI revolution. Work on data labeling "
                    "platforms, model evaluation tools, and AI applications used by the world's "
                    "leading AI companies. Compensation: ~$60/hr.\n\n"
                    "Source: https://scale.com/careers/4606014005"
                ),
            },
        ],
    },
    # ── 4. Squarespace ──
    {
        "company_name": "Squarespace",
        "email": "careers@squarespace.com",
        "name": "Anthony Casalena",
        "industry": "Website Builder / SaaS",
        "company_size": "startup",
        "website": "https://www.squarespace.com",
        "slug": "squarespace",
        "description": (
            "Squarespace is the all-in-one website building and e-commerce platform enabling "
            "millions of people to build an online presence, run their businesses, and sell "
            "products and services. Founded in a dorm room, now serving millions globally.\n\n"
            "Fund: Accel | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Anthony Casalena", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/acasalena"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 9000,
                "salary_max": 9400,
                "requirements": [
                    "Currently enrolled, graduating December 2026 or Spring 2027",
                    "Pursuing a BS or MS in CS, CE, or related technical discipline",
                    "Foundation in data structures, algorithms, and software design",
                    "Available for a 12-week paid internship (June-August) in NYC",
                ],
                "description": (
                    "Software Engineering Intern at Squarespace — Summer 2026\n\n"
                    "Join the engineering team in NYC building products used by millions. "
                    "12-week paid program, 40 hours/week, between June and August. "
                    "100% paid internship across all teams. Compensation: ~$54/hr.\n\n"
                    "Source: https://www.squarespace.com/careers/early-career"
                ),
            },
        ],
    },
    # ── 5. Atlassian ──
    {
        "company_name": "Atlassian",
        "email": "careers@atlassian.com",
        "name": "Mike Cannon-Brookes",
        "industry": "Developer Tools / Collaboration",
        "company_size": "startup",
        "website": "https://www.atlassian.com",
        "slug": "atlassian",
        "description": (
            "Atlassian builds software for software teams. Products include Jira, Confluence, "
            "Trello, and Bitbucket — used by millions of teams worldwide to plan, track, and "
            "ship great software. Public on Nasdaq.\n\n"
            "Fund: Accel | HQ: Sydney, AU (US: San Francisco, CA)"
        ),
        "founders": [
            {"name": "Mike Cannon-Brookes", "title": "CEO & Co-founder", "linkedin": "https://au.linkedin.com/in/mcannonbrookes"},
            {"name": "Scott Farquhar", "title": "Co-founder", "linkedin": "https://au.linkedin.com/in/scottfarquhar"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 13000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Software Engineering, or related field",
                    "Strong programming skills in Java, Python, JavaScript/TypeScript, or similar",
                    "Interest in developer tools, collaboration software, or enterprise SaaS",
                    "Available for a summer internship at the San Francisco office",
                ],
                "description": (
                    "Software Engineer Intern at Atlassian — Summer 2026 (U.S.)\n\n"
                    "Hands-on technical training, professional growth, dedicated mentorship, and "
                    "strong social connections. Work on products like Jira and Confluence used by "
                    "millions. Pay: $49-75/hr depending on zone. Benefits + equity eligible.\n\n"
                    "Source: https://www.atlassian.com/company/careers/details/14983"
                ),
            },
        ],
    },
    # ── 6. DocuSign ──
    {
        "company_name": "DocuSign",
        "email": "careers@docusign.com",
        "name": "Allan Thygesen",
        "industry": "E-Signature / Agreement Cloud",
        "company_size": "startup",
        "website": "https://www.docusign.com",
        "slug": "docusign",
        "description": (
            "DocuSign is the global standard for electronic signatures and agreement management. "
            "Over 1.5 million customers and a billion users in 180+ countries use DocuSign to "
            "prepare, sign, act on, and manage agreements. Public on Nasdaq.\n\n"
            "Fund: Accel | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Tom Gonser", "title": "Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7000,
                "salary_max": 7600,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Strong programming skills and interest in enterprise software",
                    "Experience with web technologies, APIs, or cloud platforms",
                    "Available for a summer internship starting late May or early June",
                ],
                "description": (
                    "Software Engineer Intern at DocuSign — Summer 2026\n\n"
                    "Add value to vital projects, develop career-ready skills, make an impact "
                    "and build community. Work on the Agreement Cloud powering digital "
                    "transactions for 1.5M+ customers. Compensation: ~$44/hr.\n\n"
                    "Source: https://careers.docusign.com/students"
                ),
            },
        ],
    },
    # ── 7. Qualtrics ──
    {
        "company_name": "Qualtrics",
        "email": "careers@qualtrics.com",
        "name": "Zig Serafin",
        "industry": "Experience Management / SaaS",
        "company_size": "startup",
        "website": "https://www.qualtrics.com",
        "slug": "qualtrics",
        "description": (
            "Qualtrics is the leader in experience management (XM), helping organizations "
            "measure and optimize customer, employee, product, and brand experiences. "
            "85% of interns receive return offers. Now part of Silver Lake.\n\n"
            "Fund: Accel | HQ: Provo, UT / Seattle, WA"
        ),
        "founders": [
            {"name": "Ryan Smith", "title": "Founder & Executive Chairman", "linkedin": ""},
            {"name": "Jared Smith", "title": "Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Provo, UT",
                "salary_min": 9500,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Strong programming skills in Java, Python, JavaScript/TypeScript, or similar",
                    "Interest in experience management, analytics, or enterprise SaaS",
                    "Available for a summer internship",
                ],
                "description": (
                    "Software Engineer Intern at Qualtrics — Summer 2026\n\n"
                    "Meaningful work with core deliverables tied to metrics. Assigned a manager "
                    "and mentor with regular coaching sessions. 85% of interns receive return "
                    "offers for full-time. Compensation: ~$57/hr.\n\n"
                    "Source: https://www.qualtrics.com/careers/us/en/internships"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # ── Spotify (already in DB from another seed) ──
    {
        "company_name": "Spotify",
        "jobs": [
            {
                "title": "Engineering & Data Science Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 7000,
                "salary_max": 8500,
                "requirements": [
                    "Pursuing a Bachelor's, Master's, or bootcamp certification in CS, CE, or related field",
                    "Previous coding experience in Java, Python, C++, TypeScript, Scala, Swift, or Kotlin",
                    "Passionate about music, audio, and personalization technology",
                    "Available from June 15 to August 21, 2026 in NYC",
                ],
                "description": (
                    "Engineering & Data Science Intern at Spotify — Summer 2026\n\n"
                    "Join the world's largest audio platform. 10-week paid internship in NYC. "
                    "Work on features that reach 600M+ users. Applications closed Feb 5 but "
                    "roles open annually for the next cycle.\n\n"
                    "Source: https://www.lifeatspotify.com/jobs/2026-summer-internship-engineering-data-science-new-york-city"
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
