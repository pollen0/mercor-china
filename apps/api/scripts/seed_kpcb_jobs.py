#!/usr/bin/env python3
"""
Seed intern jobs from Kleiner Perkins portfolio companies.

Kleiner Perkins is a legendary Silicon Valley VC firm founded in 1972, investing
in technology companies from seed to growth. Portfolio includes Figma, Handshake,
Applied Intuition, Flock Safety, Cartesia, Qumulo, Labelbox, Rippling, and more.

Sources:
- https://www.kleinerperkins.com/portfolio
- https://jobs.kleinerperkins.com/ (scraped via Playwright — apps/web/scripts/scrape-consider.ts)
- Individual company career pages

SCRIPT ID: kpcb
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
FIRM_NAME = "Kleiner Perkins"
SCRIPT_ID = "kpcb"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Handshake ──
    {
        "company_name": "Handshake",
        "email": "careers@joinhandshake.com",
        "name": "Garrett Lord",
        "industry": "HR / Recruiting",
        "company_size": "enterprise",
        "website": "https://joinhandshake.com",
        "slug": "handshake",
        "description": (
            "Handshake is the #1 career platform for college students and recent graduates. "
            "Connecting students with employers for internships and entry-level jobs, Handshake "
            "serves 15M+ students across 1,500+ universities and partners with 900K+ employers. "
            "Their AI-powered platform matches students with personalized career opportunities.\n\n"
            "Fund: Kleiner Perkins | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Garrett Lord", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/garrettlord"},
            {"name": "Scott Ringwelski", "title": "CTO & Co-Founder", "linkedin": "https://linkedin.com/in/scott-ringwelski"},
            {"name": "Ben Christensen", "title": "CPO & Co-Founder", "linkedin": "https://linkedin.com/in/bchristensen"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Software Engineering, or related field",
                    "Experience with React.js, JavaScript, and TypeScript",
                    "Familiarity with Ruby on Rails or similar backend frameworks",
                    "Interest in full stack development and AI applications",
                ],
                "description": (
                    "Software Engineer Intern at Handshake. Build features across the career platform "
                    "connecting millions of college students with employers. Work on full stack development "
                    "with React, TypeScript, and Ruby on Rails.\n\n"
                    "Source: https://jobs.ashbyhq.com/handshake/25b3e69c-0a49-40db-9184-832a1e6fcf1a"
                ),
            },
            {
                "title": "AI Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing a graduate degree in Computer Science, ML, NLP, or related field",
                    "Experience with PyTorch or TensorFlow and modern AI/ML techniques",
                    "Strong research skills with ability to present findings",
                    "Interest in applying AI to career platform and matching algorithms",
                ],
                "description": (
                    "AI Research Intern at Handshake. Conduct research on AI-powered matching, "
                    "recommendation systems, and NLP applications for the career platform. "
                    "Work alongside the HAI Research team on cutting-edge AI problems.\n\n"
                    "Source: https://jobs.ashbyhq.com/handshake/f01f09ac-4b94-4de0-bbef-e1892df4e0cb"
                ),
            },
        ],
    },

    # ── 2. Cartesia ──
    {
        "company_name": "Cartesia",
        "email": "careers@cartesia.ai",
        "name": "Albert Gu",
        "industry": "AI / Enterprise Software",
        "company_size": "startup",
        "website": "https://cartesia.ai",
        "slug": "cartesia",
        "description": (
            "Cartesia is building real-time multimodal intelligence with state space models. "
            "Their foundation model technology enables fast, efficient inference for AI applications. "
            "Founded by the creators of the Mamba architecture, Cartesia is at the frontier of "
            "efficient sequence modeling and real-time AI.\n\n"
            "Fund: Kleiner Perkins | HQ: San Francisco, CA | Stage: Series A"
        ),
        "founders": [
            {"name": "Albert Gu", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/albert-gu"},
            {"name": "Tri Dao", "title": "Chief Scientist & Co-Founder", "linkedin": "https://linkedin.com/in/tridao"},
        ],
        "jobs": [
            {
                "title": "Product Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Experience with React.js, TypeScript, and Python",
                    "Interest in building developer tools and AI-powered products",
                    "Familiarity with systems engineering and open source software",
                ],
                "description": (
                    "Product Engineer Intern at Cartesia. Build user-facing products and developer tools "
                    "for Cartesia's real-time AI platform. Work with React, TypeScript, and Python on "
                    "web applications powering AI model deployment and inference.\n\n"
                    "Source: https://jobs.ashbyhq.com/cartesia/ebae3ceb-a6a7-4af0-ae3e-c197af14a67a"
                ),
            },
            {
                "title": "Platform Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Systems Engineering, or related field",
                    "Experience with distributed systems and infrastructure",
                    "Proficiency in Python and familiarity with ML systems",
                    "Interest in building scalable AI infrastructure and observability",
                ],
                "description": (
                    "Platform Engineer Intern at Cartesia. Build and optimize the infrastructure "
                    "powering real-time AI inference at scale. Work on distributed systems, "
                    "ML infrastructure, and platform observability.\n\n"
                    "Source: https://jobs.ashbyhq.com/cartesia/57126466-2554-4ae5-baa6-ea56e18db942"
                ),
            },
            {
                "title": "Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing a graduate degree in CS, ML, or related field",
                    "Strong experience with PyTorch and CUDA",
                    "Research background in ML systems, efficient architectures, or state space models",
                    "Ability to work independently on open-ended research problems",
                ],
                "description": (
                    "Research Intern at Cartesia. Conduct research on efficient sequence modeling, "
                    "state space models, and real-time AI architectures. Work with the team that "
                    "created the Mamba architecture on next-generation AI foundation models.\n\n"
                    "Source: https://jobs.ashbyhq.com/cartesia/0dc46cae-e837-4e78-8ea7-8f555de51d24"
                ),
            },
        ],
    },

    # ── 3. Qumulo ──
    {
        "company_name": "Qumulo",
        "email": "careers@qumulo.com",
        "name": "Bill Richter",
        "industry": "Cloud Services / Data Infrastructure",
        "company_size": "mid_market",
        "website": "https://qumulo.com",
        "slug": "qumulo",
        "description": (
            "Qumulo is the leader in hybrid cloud file storage, providing a single, scalable "
            "file data platform for unstructured data management. Qumulo's software-defined "
            "architecture runs wherever data is needed — on-premises, in the public cloud, or "
            "at the edge — enabling enterprises to manage file data at scale.\n\n"
            "Fund: Kleiner Perkins | HQ: Seattle, WA"
        ),
        "founders": [
            {"name": "Bill Richter", "title": "CEO", "linkedin": "https://linkedin.com/in/billrichter"},
            {"name": "Peter Godman", "title": "Co-Founder & CTO", "linkedin": "https://linkedin.com/in/petergodman"},
        ],
        "jobs": [
            {
                "title": "Software Development Engineer Internship (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Seattle, WA",
                "salary_min": 8500,
                "salary_max": 9500,
                "requirements": [
                    "Pursuing a degree in Computer Science, Computer Engineering, or related field",
                    "Experience with operating systems, data structures, and concurrency",
                    "Interest in distributed systems, cloud services, and storage",
                    "Available for winter, spring, or summer internship",
                ],
                "description": (
                    "Software Development Engineer Intern at Qumulo. Work on hybrid cloud file storage "
                    "infrastructure, including distributed systems, operating systems, and cloud services. "
                    "Help build the next generation of scalable data management solutions.\n\n"
                    "Source: https://qumulo.hrmdirect.com/employment/job-opening.php?req=3513374"
                ),
            },
        ],
    },

    # ── 4. Labelbox ──
    {
        "company_name": "Labelbox",
        "email": "careers@labelbox.com",
        "name": "Manu Sharma",
        "industry": "Developer Tools / AI",
        "company_size": "mid_market",
        "website": "https://labelbox.com",
        "slug": "labelbox",
        "description": (
            "Labelbox is the leading data-centric AI platform for building, managing, and "
            "iterating on training data for AI models. Their platform enables teams to create "
            "high-quality labeled datasets, manage annotation workflows, and improve model "
            "performance through better data.\n\n"
            "Fund: Kleiner Perkins | HQ: San Francisco, CA | Stage: Growth"
        ),
        "founders": [
            {"name": "Manu Sharma", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/manusharma1"},
            {"name": "Brian Rieger", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/brian-rieger"},
            {"name": "Ibrahim Ulukaya", "title": "CTO & Co-Founder", "linkedin": "https://linkedin.com/in/ibrahim-ulukaya"},
        ],
        "jobs": [
            {
                "title": "Applied Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a graduate degree in CS, ML, NLP, or related field",
                    "Experience with TensorFlow, PyTorch, and deep learning frameworks",
                    "Research background in ML, NLP, or computer vision",
                    "Interest in data-centric AI and training data quality",
                ],
                "description": (
                    "Applied Research Intern at Labelbox. Work on ML research problems related to "
                    "data-centric AI, including active learning, data quality assessment, and automated "
                    "labeling. Research and build solutions that improve AI model performance through "
                    "better training data.\n\n"
                    "Source: https://job-boards.greenhouse.io/labelbox/jobs/4820677007"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New roles for companies already in the DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # ── Applied Intuition ── (already has "Software Engineer Intern (Summer 2026)")
    {
        "company_name": "Applied Intuition",
        "jobs": [
            {
                "title": "Research Intern - Reinforcement Learning, Robotics (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Sunnyvale, CA",
                "salary_min": 10000,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing a graduate degree in CS, Robotics, ML, or related field",
                    "Experience with reinforcement learning, robotics, and computer vision",
                    "Proficiency in Python and deep learning frameworks (PyTorch, TensorFlow)",
                    "Published research in RL, robotics, or related areas preferred",
                ],
                "description": (
                    "Research Intern at Applied Intuition - Reinforcement Learning & Robotics. "
                    "Work on RL algorithms for autonomous systems, robot perception, and control. "
                    "Apply cutting-edge ML research to autonomous vehicle simulation.\n\n"
                    "Source: https://boards.greenhouse.io/appliedintuition/jobs/4661665005"
                ),
            },
            {
                "title": "Research Intern - 3D Vision and Generation, Self-Driving (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Sunnyvale, CA",
                "salary_min": 10000,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing a graduate degree in CS, Computer Vision, or related field",
                    "Experience with 3D vision, generative models, and autonomous driving",
                    "Strong background in computer vision and graphics",
                    "Proficiency in Python, PyTorch, and CUDA",
                ],
                "description": (
                    "Research Intern at Applied Intuition - 3D Vision & Generation for Self-Driving. "
                    "Work on 3D scene generation, perception, and simulation for autonomous vehicles. "
                    "Research and develop state-of-the-art computer vision models.\n\n"
                    "Source: https://boards.greenhouse.io/appliedintuition/jobs/4661663005"
                ),
            },
            {
                "title": "Research Intern - World-Action Foundation Model, Robotics (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Sunnyvale, CA",
                "salary_min": 10000,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing a graduate degree in CS, ML, Robotics, or related field",
                    "Experience with foundation models, large-scale ML, and robotics",
                    "Research background in world models, action prediction, or embodied AI",
                    "Strong proficiency in Python and deep learning frameworks",
                ],
                "description": (
                    "Research Intern at Applied Intuition - World-Action Foundation Models for Robotics. "
                    "Work on large-scale foundation models for autonomous systems including world models "
                    "and action prediction for robotics applications.\n\n"
                    "Source: https://boards.greenhouse.io/appliedintuition/jobs/4661666005"
                ),
            },
            {
                "title": "Research Intern - Robotic Hardware, Simulation and Data (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Sunnyvale, CA",
                "salary_min": 10000,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing a graduate degree in Robotics, ME, CS, or related field",
                    "Experience with robotic hardware, simulation, and data pipelines",
                    "Background in computer vision, ML, and robotics systems",
                    "Proficiency in Python and simulation frameworks",
                ],
                "description": (
                    "Research Intern at Applied Intuition - Robotic Hardware, Simulation & Data. "
                    "Work on simulation environments, data collection, and hardware integration "
                    "for autonomous systems and robotics.\n\n"
                    "Source: https://boards.greenhouse.io/appliedintuition/jobs/4661664005"
                ),
            },
        ],
    },

    # ── Flock Safety ── (already has "Software Engineering Intern (Summer 2026)")
    {
        "company_name": "Flock Safety",
        "jobs": [
            {
                "title": "Device Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Atlanta, GA",
                "salary_min": 8000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Computer Engineering, or related field",
                    "Experience with Kotlin, Java, or Android development",
                    "Interest in embedded systems, IoT, and network protocols",
                    "Familiarity with infrastructure and automation",
                ],
                "description": (
                    "Device Software Engineering Intern at Flock Safety. Work on software for "
                    "IoT camera devices including Android development, network protocols, and "
                    "embedded systems. Help build public safety technology.\n\n"
                    "Source: https://jobs.ashbyhq.com/Flock%20Safety/88a80dbf-1627-420a-a087-1bc8edc894e0"
                ),
            },
            {
                "title": "Wireless Software Systems Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Atlanta, GA",
                "salary_min": 8000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a degree in Computer Science, EE, or related field",
                    "Interest in wireless systems, IoT, and application software",
                    "Familiarity with embedded systems and communication protocols",
                    "Strong problem-solving and analytical skills",
                ],
                "description": (
                    "Wireless Software Systems Intern at Flock Safety. Work on wireless communication "
                    "systems for IoT public safety devices. Develop and optimize wireless protocols "
                    "and application software for camera and sensor systems.\n\n"
                    "Source: https://jobs.ashbyhq.com/Flock%20Safety/6917efab-3505-4810-b4c0-115287711653"
                ),
            },
            {
                "title": "Technical Project Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "Atlanta, GA",
                "salary_min": 7500,
                "salary_max": 8500,
                "requirements": [
                    "Pursuing a degree in Engineering, Business, or related field",
                    "Interest in IoT, embedded systems, and program management",
                    "Strong organizational and prioritization skills",
                    "Technical aptitude with ability to coordinate cross-functional teams",
                ],
                "description": (
                    "Technical Project Management Intern at Flock Safety. Coordinate engineering "
                    "projects across hardware and software teams. Manage timelines, dependencies, "
                    "and stakeholder communication for IoT product development.\n\n"
                    "Source: https://jobs.ashbyhq.com/Flock%20Safety/39f5a056-3e08-4d58-974c-fab9c9a29ae1"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# SEED FUNCTIONS
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
        print(f"  SKIP: {company_name} already exists (id={existing.id})")
        return 0

    employer_id = generate_cuid("e_")
    org_id = generate_cuid("o_")
    member_id = generate_cuid("tm_")

    hashed_pw = get_password_hash(f"{company_data['slug']}Intern2026!")

    employer = Employer(
        id=employer_id,
        email=company_data["email"],
        password=hashed_pw,
        name=company_data["name"],
        company_name=company_name,
        industry=company_data["industry"],
        company_size=company_data["company_size"],
    )
    session.add(employer)

    org = Organization(
        id=org_id,
        name=company_name,
        slug=company_data["slug"],
        description=company_data.get("description", ""),
        website=company_data.get("website", ""),
        industry=company_data["industry"],
        company_size=company_data["company_size"],
    )
    session.add(org)

    member = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(member)

    jobs_added = 0
    for job_data in company_data.get("jobs", []):
        job_id = generate_cuid("j_")
        job = Job(
            id=job_id,
            employer_id=employer_id,
            title=job_data["title"],
            vertical=job_data["vertical"],
            role_type=job_data["role_type"],
            location=job_data["location"],
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            requirements=job_data.get("requirements", []),
            description=job_data.get("description", ""),
            is_active=True,
        )
        session.add(job)
        jobs_added += 1

    return jobs_added


def add_jobs_to_existing(session, entry):
    """
    Add new jobs to an existing company.
    Skips jobs whose title already exists for that employer.
    """
    company_name = entry["company_name"]

    employer = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()
    if not employer:
        print(f"  SKIP: {company_name} not found in DB")
        return 0

    existing_titles = {
        j.title
        for j in session.query(Job).filter(Job.employer_id == employer.id).all()
    }

    jobs_added = 0
    for job_data in entry["jobs"]:
        if job_data["title"] in existing_titles:
            print(f"  SKIP job: \"{job_data['title']}\" already exists")
            continue

        job_id = generate_cuid("j_")
        job = Job(
            id=job_id,
            employer_id=employer.id,
            title=job_data["title"],
            vertical=job_data["vertical"],
            role_type=job_data["role_type"],
            location=job_data["location"],
            salary_min=job_data.get("salary_min"),
            salary_max=job_data.get("salary_max"),
            requirements=job_data.get("requirements", []),
            description=job_data.get("description", ""),
            is_active=True,
        )
        session.add(job)
        jobs_added += 1

    return jobs_added


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# MAIN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

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
        for err in errors:
            print(f"    - {err}")
    print(f"\n  DB totals: {db_employers} employers, {db_jobs} jobs")
    print("=" * 60)


if __name__ == "__main__":
    main()
