#!/usr/bin/env python3
"""
Seed script for YC startup jobs scraped from Work at a Startup.

Usage:
    cd apps/api
    python -m scripts.seed_yc_jobs

This script populates the database with real YC startup job listings,
including employer profiles, organizations, and all open roles.
"""
import sys
import os

# Add parent directory to path for imports
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


def generate_cuid(prefix: str = "") -> str:
    """Generate a CUID-like ID."""
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ─────────────────────────────────────────────
# Company Data: Reacher (YC S25)
# Source: https://www.workatastartup.com/companies/reacher
# ─────────────────────────────────────────────

REACHER = {
    "company_name": "Reacher",
    "email": "careers@reacherapp.com",
    "name": "Jerry Qian",  # CEO
    "industry": "AI / E-commerce / Creator Economy",
    "company_size": "startup",
    "website": "https://reacherapp.com/",
    "description": (
        "Reacher is the #1 TikTok Shop partner helping brands like Under Armour, Hanes, "
        "HeyDude, and Logitech scale their affiliate marketing. We automate creator marketing "
        "workflows including discovery, outreach, campaign management, and content strategy "
        "across TikTok Shop, YouTube Shopping, Instagram, and Amazon.\n\n"
        "YC Batch: S25 | Team Size: 15 | HQ: San Francisco, CA\n"
        "7-figure ARR, raising seed round."
    ),
    "founders": [
        {
            "name": "Jerry Qian",
            "title": "Co-Founder & CEO",
            "linkedin": "https://www.linkedin.com/in/j-qian",
            "background": "Meta, UC Berkeley, NASA",
        },
        {
            "name": "Bora Mutluoglu",
            "title": "Co-Founder",
            "linkedin": "https://www.linkedin.com/in/bora-mutluoglu",
            "background": "UC Berkeley, Palo Alto Networks",
        },
    ],
}

REACHER_JOBS = [
    {
        "title": "Software Engineer Intern (Fall 2025 / Summer 2026)",
        "vertical": Vertical.SOFTWARE_ENGINEERING,
        "role_type": RoleType.SOFTWARE_ENGINEER,
        "location": "San Francisco, CA / Los Angeles, CA (In-person)",
        "salary_min": 6000,
        "salary_max": 10000,
        "requirements": [
            "Computer Science major with completed foundational coursework",
            "Full-stack project experience (personal projects, hackathons, or coursework)",
            "Available for 10-12 weeks (Fall: Sept/Oct-Dec 2025 or Summer: May/June-Aug 2026)",
            "Resourceful and comfortable navigating ambiguity",
            "US citizen or valid work visa",
        ],
        "description": (
            "Software Engineer Intern at Reacher (YC S25)\n\n"
            "Compensation: $6,000 - $10,000/month for 10-12 weeks\n\n"
            "About the Role:\n"
            "Build full-stack features that ship to production within days - not throwaway intern projects. "
            "You'll work on AI agents, LLM-powered tools and ML pipelines processing millions of "
            "creator/brand interactions, plus direct customer-facing features with real impact.\n\n"
            "Tech Stack:\n"
            "- Backend: Python, FastAPI, PostgreSQL, GCP\n"
            "- Frontend: React, Tailwind, shadcn/ui\n\n"
            "What We Look For:\n"
            "- CS major with completed foundational coursework\n"
            "- Full-stack project experience from personal projects, hackathons, or coursework\n"
            "- Available 10-12 weeks (Fall 2025 or Summer 2026)\n"
            "- Resourceful and comfortable with ambiguity\n\n"
            "Bonus:\n"
            "- Previous startup or tech internship experience\n"
            "- ML/AI coursework or projects\n"
            "- Deployed apps with real users\n"
            "- Side projects or open-source contributions\n"
            "- Interest in AI, e-commerce, or creator economy\n\n"
            "Culture:\n"
            "Collaborative by default. No politics. Regular customer interaction. "
            "High trust, high output. Team activities and social cohesion.\n\n"
            "Source: https://www.workatastartup.com/jobs/80430"
        ),
    },
    {
        "title": "Software Engineer (Full Stack)",
        "vertical": Vertical.SOFTWARE_ENGINEERING,
        "role_type": RoleType.SOFTWARE_ENGINEER,
        "location": "San Francisco, CA / Los Angeles, CA / New York, NY / Remote (US)",
        "salary_min": 90000,
        "salary_max": 130000,
        "requirements": [
            "1+ years professional experience",
            "Full-stack capability from schema design to frontend polish",
            "Product-oriented mindset - you think beyond just code",
            "Demonstrated end-to-end ownership of projects",
            "Resourceful and comfortable navigating ambiguity",
            "US citizen or valid work visa",
        ],
        "description": (
            "Software Engineer (Full Stack) at Reacher (YC S25)\n\n"
            "Compensation: $90K - $130K + 0.10% - 1.00% equity\n\n"
            "About the Role:\n"
            "Own product features end-to-end - from research and design through implementation, "
            "testing, and shipping. Engage directly with customers to translate requirements "
            "into polished experiences. Design scalable backends and build responsive frontends.\n\n"
            "Tech Stack:\n"
            "- Backend: Python, FastAPI, PostgreSQL, GCP\n"
            "- Frontend: React, Tailwind, shadcn/ui\n\n"
            "What We Look For:\n"
            "- 1+ years professional experience\n"
            "- Full-stack capability from schema design to frontend polish\n"
            "- Product-oriented mindset\n"
            "- Proven end-to-end ownership\n\n"
            "Bonus:\n"
            "- Early-stage startup or first-hire experience\n"
            "- Internal tooling or dashboards scaled to thousands of users\n"
            "- Interest in AI, e-commerce, or automation\n"
            "- Side projects or open-source contributions\n\n"
            "Source: https://www.ycombinator.com/companies/reacher/jobs/D4dVC9e"
        ),
    },
    {
        "title": "Senior Software Engineer (Full Stack)",
        "vertical": Vertical.SOFTWARE_ENGINEERING,
        "role_type": RoleType.SOFTWARE_ENGINEER,
        "location": "San Francisco, CA / Los Angeles, CA / New York, NY / Remote (US)",
        "salary_min": 115000,
        "salary_max": 200000,
        "requirements": [
            "5-8 years professional experience at product-first companies or FAANG",
            "Full-stack capability from schema design to frontend polish",
            "Product-oriented mindset - you think beyond just code",
            "Demonstrated end-to-end ownership of meaningful projects",
            "Resourceful and comfortable navigating ambiguity",
            "US citizen or valid work visa",
        ],
        "description": (
            "Senior Software Engineer (Full Stack) at Reacher (YC S25)\n\n"
            "Compensation: $115K - $200K + 0.50% - 2.50% equity\n\n"
            "About the Role:\n"
            "Own product features end-to-end, from research through shipping. Engage directly "
            "with customers to translate requirements into polished experiences. Design scalable "
            "backend systems and build responsive user interfaces. Write clean, maintainable, "
            "and testable code with minimal oversight. Contribute to architectural and process "
            "decisions. Operate with high urgency - we ship fast and learn fast.\n\n"
            "Tech Stack:\n"
            "- Backend: Python, FastAPI, PostgreSQL, GCP\n"
            "- Frontend: React, Tailwind, shadcn/ui\n\n"
            "What We Look For:\n"
            "- 5-8 years professional experience, ideally at product-focused firms or FAANG\n"
            "- SDE-2 level ownership expected\n"
            "- Full-stack capability from schema design to frontend polish\n"
            "- Product-oriented mindset\n\n"
            "Bonus:\n"
            "- Early-stage startup or first-hire experience\n"
            "- Internal tooling, dashboards, or systems scaled to thousands of users\n"
            "- Interest in AI, e-commerce, or automation\n"
            "- Side projects or open-source contributions\n\n"
            "Application: Send a short note about something you've built and why this role "
            "excites you. GitHub, LinkedIn, or resume optional.\n\n"
            "Source: https://www.workatastartup.com/jobs/77926"
        ),
    },
    {
        "title": "Head of Customer Success",
        "vertical": None,
        "role_type": None,
        "location": "San Francisco, CA",
        "salary_min": 110000,
        "salary_max": 180000,
        "requirements": [
            "5+ years Customer Success experience, 2+ years in leadership at SaaS",
            "Proven track record scaling CS teams while improving retention and expansion",
            "Data proficiency with SaaS metrics and KPIs",
            "Strong communication and cross-functional collaboration",
            "Ability to thrive in fast-paced, ambiguous startup environments",
            "US citizen or valid work visa",
        ],
        "description": (
            "Head of Customer Success at Reacher (YC S25)\n\n"
            "Compensation: $110K - $180K + 0.01% - 0.50% equity\n\n"
            "About the Role:\n"
            "Build and lead our Customer Success organization. Lead CS vision, strategy, and "
            "execution across the full customer lifecycle. Design and manage scalable onboarding "
            "and education programs that accelerate time-to-value. Establish health scoring "
            "systems and identify churn risks to enhance retention and expansion. Partner "
            "cross-functionally with Product and Sales to increase customer lifetime value. "
            "Optimize HubSpot and analytics tools for data-driven decisions.\n\n"
            "What We Look For:\n"
            "- 5+ years CS experience, 2+ in leadership at SaaS\n"
            "- Track record scaling CS teams\n"
            "- Data proficiency with SaaS metrics\n\n"
            "Bonus:\n"
            "- Creator/affiliate marketing platforms or social commerce background\n"
            "- Influencer marketing data and automation tool familiarity\n"
            "- Workshop facilitation or customer training program experience\n\n"
            "Interview Process:\n"
            "1. Head of GTM meeting\n"
            "2. Root cause analysis exercises with Co-Founder/President\n"
            "3. Presentation to CRO and Head of GTM on CS scaling strategy\n"
            "4. CEO interview\n\n"
            "Source: https://www.ycombinator.com/companies/reacher/jobs/FeFkQWj"
        ),
    },
    {
        "title": "Founding Account Executive",
        "vertical": None,
        "role_type": None,
        "location": "San Francisco, CA (office-based, travel required)",
        "salary_min": 70000,
        "salary_max": 240000,
        "requirements": [
            "3-5 years Account Executive experience at early or growth-stage startups",
            "Proven quota attainment and deal-closing track record",
            "Comfort operating in fast-paced, ambiguous environments",
            "Full sales cycle expertise: prospecting through retention",
            "Strong presentation and relationship-building abilities",
            "Willingness to be based in SF office and travel for meetings",
            "US citizen or valid work visa",
        ],
        "description": (
            "Founding Account Executive at Reacher (YC S25)\n\n"
            "Compensation: $70K - $240K + 0.01% - 0.50% equity\n\n"
            "About the Role:\n"
            "Supercharge our go-to-market motion as our founding AE. Own the full sales cycle "
            "from outbound prospecting to closing and onboarding. Build pipeline through "
            "outbound, inbound, partnerships and events. Drive revenue by closing deals and "
            "growing accounts. Help design repeatable sales playbooks and GTM strategies as "
            "the sales organization grows from scratch.\n\n"
            "What We Look For:\n"
            "- 3-5 years AE experience at startups\n"
            "- Proven quota attainment\n"
            "- Full sales cycle expertise\n\n"
            "Bonus:\n"
            "- TikTok Shop, social commerce, or creator marketing familiarity\n"
            "- Existing e-commerce or Amazon ecosystem network\n"
            "- HubSpot and CRM pipeline management experience\n"
            "- Proficiency with AI tools (ChatGPT, AI SDRs)\n"
            "- Startup hustle mentality\n\n"
            "Interview Process:\n"
            "1. Head of GTM meeting\n"
            "2. Mock sales interview with Head of GTM\n"
            "3. CRO interview (San Francisco)\n"
            "4. CEO meeting\n\n"
            "Source: https://www.ycombinator.com/companies/reacher/jobs/44JG1fa"
        ),
    },
]


def seed_reacher(session):
    """Seed Reacher company, organization, and all jobs."""

    # Check if already seeded
    existing = session.query(Employer).filter(
        Employer.company_name == "Reacher"
    ).first()
    if existing:
        print(f"  Reacher already exists (employer_id={existing.id}), skipping...")
        return existing.id

    # 1. Create Employer account
    employer_id = generate_cuid("e_")
    employer = Employer(
        id=employer_id,
        name=REACHER["name"],
        company_name=REACHER["company_name"],
        email=REACHER["email"],
        password=get_password_hash("ReacherYCS25!seed"),  # Placeholder password
        industry=REACHER["industry"],
        company_size=REACHER["company_size"],
        is_verified=True,
    )
    session.add(employer)
    print(f"  Created employer: {employer.company_name} ({employer_id})")

    # 2. Create Organization
    org_id = generate_cuid("o_")
    organization = Organization(
        id=org_id,
        name=REACHER["company_name"],
        slug="reacher",
        website=REACHER["website"],
        industry=REACHER["industry"],
        company_size=REACHER["company_size"],
        description=REACHER["description"],
        settings={
            "yc_batch": "S25",
            "team_size": 15,
            "hq": "San Francisco, CA",
            "founders": REACHER["founders"],
        },
    )
    session.add(organization)
    print(f"  Created organization: {organization.name} ({org_id})")

    # 3. Link employer to organization as owner
    member_id = generate_cuid("tm_")
    membership = OrganizationMember(
        id=member_id,
        organization_id=org_id,
        employer_id=employer_id,
        role=OrganizationRole.OWNER,
    )
    session.add(membership)
    print(f"  Linked employer as owner of organization")

    # 4. Create all jobs
    for job_data in REACHER_JOBS:
        job_id = generate_cuid("j_")
        job = Job(
            id=job_id,
            title=job_data["title"],
            description=job_data["description"],
            vertical=job_data["vertical"],
            role_type=job_data["role_type"],
            requirements=job_data["requirements"],
            location=job_data["location"],
            salary_min=job_data["salary_min"],
            salary_max=job_data["salary_max"],
            employer_id=employer_id,
            is_active=True,
        )
        session.add(job)
        salary_display = f"${job_data['salary_min']:,} - ${job_data['salary_max']:,}"
        print(f"  Created job: {job.title} ({salary_display})")

    session.commit()
    print(f"\n  Reacher seeded with {len(REACHER_JOBS)} jobs.")
    return employer_id


def main():
    print("=" * 60)
    print("Seeding YC Startup Jobs")
    print("=" * 60)

    engine = create_engine(settings.database_url)
    SessionLocal = sessionmaker(bind=engine)
    session = SessionLocal()

    try:
        print("\n[Reacher - YC S25]")
        print(f"  Founders:")
        for f in REACHER["founders"]:
            print(f"    - {f['name']} ({f['title']})")
            print(f"      LinkedIn: {f['linkedin']}")
            print(f"      Background: {f['background']}")

        seed_reacher(session)

        # Print summary
        total_jobs = session.query(Job).count()
        total_employers = session.query(Employer).count()
        print(f"\n{'=' * 60}")
        print(f"Database totals: {total_employers} employers, {total_jobs} jobs")
        print(f"{'=' * 60}")

    except Exception as e:
        session.rollback()
        print(f"\nError: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
