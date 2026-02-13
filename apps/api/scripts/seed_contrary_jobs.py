#!/usr/bin/env python3
"""
Seed intern jobs from Contrary portfolio companies into the Pathway database.

JOB BOARD: https://jobs.contrary.com
FIRM: Contrary
SCRIPT ID: contrary

Sources:
- https://www.contrary.com/companies (portfolio list)
- https://jobs.contrary.com (job board - JS rendered, scraped via web search)
- Individual company career pages (Base Power, Warp, Armada, Leland, AtoB)
- Levels.fyi, ZipRecruiter, Prosple for salary data

Note: The Contrary job board is JS-rendered and not directly scrapeable.
Jobs were found via web search across individual company career pages.
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
FIRM_NAME = "Contrary"
SCRIPT_ID = "contrary"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Base Power Company ──
    {
        "company_name": "Base Power",
        "email": "careers@basepowercompany.com",
        "name": "Zach Dell",
        "industry": "Energy / Clean Tech",
        "company_size": "startup",
        "website": "https://www.basepowercompany.com",
        "slug": "base-power",
        "description": (
            "Base Power is building the operating system for American power, deploying "
            "a nationwide network of distributed batteries that strengthens critical "
            "infrastructure and saves Americans money. Raised $1B+ in funding from "
            "top-tier investors.\n\n"
            "Fund: Contrary, a16z, Lightspeed, Thrive | HQ: Austin, TX"
        ),
        "founders": [
            {"name": "Zach Dell", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/zach-dell-a631a554"},
            {"name": "Justin Lopas", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/justinlopas"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 3600,
                "salary_max": 5200,
                "requirements": [
                    "Demonstrated ability to build and ship working software through side projects, coursework, or prior internships",
                    "Clear communicator who thrives in collaborative environments",
                    "Builder's mindset — curious, self-directed, and eager to work on problems that matter",
                    "Available for full-time, in-person internship in Austin, TX",
                ],
                "description": (
                    "Software Engineering Intern at Base Power Company\n\n"
                    "At Base, interns work on the same codebases as full-time engineers — no toy projects. "
                    "Areas of work include Fleet Software & Embedded Systems, Internal Software, "
                    "Market Infrastructure, and Product Engineering. You'll learn from a team that's "
                    "built and scaled complex systems across energy, aerospace, and hardware industries.\n\n"
                    "This is not a 9-to-5. Base expects in-person, full-time work in the Austin office.\n\n"
                    "Source: https://www.basepowercompany.com/open-roles"
                ),
            },
            {
                "title": "Quantitative Developer Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Austin, TX",
                "salary_min": 4000,
                "salary_max": 6000,
                "requirements": [
                    "Strong programming skills in Python or similar quantitative languages",
                    "Background in mathematics, statistics, or quantitative finance",
                    "Experience with data analysis and numerical computing (NumPy, Pandas)",
                    "Available for full-time, in-person internship in Austin, TX",
                ],
                "description": (
                    "Quantitative Developer Intern at Base Power Company\n\n"
                    "Work on quantitative models and market infrastructure for energy trading "
                    "and battery optimization. Base is building software that connects batteries, "
                    "homes, neighborhoods, and the grid.\n\n"
                    "Source: https://www.basepowercompany.com/open-roles"
                ),
            },
            {
                "title": "Firmware Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 3600,
                "salary_max": 5200,
                "requirements": [
                    "Experience with embedded systems programming (C/C++)",
                    "Understanding of hardware-software interfaces and real-time systems",
                    "Strong debugging and problem-solving skills",
                    "Available for full-time, in-person internship in Austin, TX",
                ],
                "description": (
                    "Firmware Engineering Intern at Base Power Company\n\n"
                    "Work on firmware for Base's distributed battery network. Design, test, "
                    "and deploy firmware for battery management systems and grid-connected devices. "
                    "Base deploys hardware across the US that requires reliable, low-latency firmware.\n\n"
                    "Source: https://www.basepowercompany.com/open-roles"
                ),
            },
        ],
    },

    # ── Warp ──
    {
        "company_name": "Warp",
        "email": "careers@warp.dev",
        "name": "Zach Lloyd",
        "industry": "Developer Tools / AI",
        "company_size": "startup",
        "website": "https://www.warp.dev",
        "slug": "warp",
        "description": (
            "Warp is a next-generation agentic development environment that reinvents how "
            "engineers build and collaborate. Users launch 3M+ agents per day, generating "
            "250M lines of code weekly with a 97% acceptance rate. Raised $70M+ from top investors.\n\n"
            "Fund: Contrary, Sequoia, GV | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Zach Lloyd", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/zachlloyd"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 6500,
                "salary_max": 7500,
                "requirements": [
                    "Outstanding software engineering student passionate about developer tools",
                    "Interest in tackling difficult technical problems (Rust, terminal infrastructure, AI agents)",
                    "Strong programming fundamentals and ability to ship high-quality code",
                    "Available for summer 2026 internship",
                ],
                "description": (
                    "Software Engineering Intern at Warp\n\n"
                    "Join Warp to build the future of agentic development. Work on agents, "
                    "terminal infrastructure, and developer tools used by millions of developers. "
                    "Warp is built in Rust and pushes the boundaries of what's possible in "
                    "developer productivity. Successful interns may receive a full-time offer.\n\n"
                    "Source: https://www.warp.dev/careers"
                ),
            },
        ],
    },

    # ── Armada ──
    {
        "company_name": "Armada",
        "email": "careers@armada.ai",
        "name": "Dan Wright",
        "industry": "Edge Computing / AI",
        "company_size": "startup",
        "website": "https://www.armada.ai",
        "slug": "armada-ai",
        "description": (
            "Armada is the world's first full-stack edge computing platform, providing "
            "connectivity, compute, and AI solutions anywhere on Earth. Deploys ruggedized "
            "mobile data centers for industries like mining, oil & gas, logistics, and defense. "
            "Raised $239M including from Microsoft M12.\n\n"
            "Fund: Contrary | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Dan Wright", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/wrightdh"},
            {"name": "Jon Runyan", "title": "COO & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "AI/ML Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing or recently completed degree in Computer Science, Data Science, AI, or related field",
                    "Familiarity with Python and AI/ML frameworks (TensorFlow, PyTorch, Scikit-learn)",
                    "Experience with data manipulation using Pandas, NumPy, and SQL",
                    "Strong problem-solving skills and eagerness to learn",
                ],
                "description": (
                    "AI/ML Intern at Armada\n\n"
                    "Join Armada's AI/ML team to contribute to projects in artificial intelligence "
                    "and machine learning for edge computing. Work on deploying AI models to "
                    "ruggedized data centers operating in some of the most challenging environments "
                    "on Earth — from remote mines to offshore platforms.\n\n"
                    "Source: https://www.armada.ai/careers"
                ),
            },
        ],
    },

    # ── Leland ──
    {
        "company_name": "Leland",
        "email": "careers@joinleland.com",
        "name": "John Koelliker",
        "industry": "EdTech / Career Coaching",
        "company_size": "startup",
        "website": "https://www.joinleland.com",
        "slug": "leland",
        "description": (
            "Leland is the daily home for ambitious people — a platform with coaching, content, "
            "AI tools, and community to help you reach your career and educational goals. "
            "Trusted by thousands of students and professionals. Raised $20M+ from top investors.\n\n"
            "Fund: Contrary, Forerunner, GSV Ventures | HQ: Lehi, UT"
        ),
        "founders": [
            {"name": "John Koelliker", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/john-koelliker"},
            {"name": "Erika Mahterian", "title": "Co-Founder", "linkedin": ""},
            {"name": "Zando Ward", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Growth Intern - Sales (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.MARKETING_ASSOCIATE,
                "location": "Remote",
                "salary_min": 3500,
                "salary_max": 5000,
                "requirements": [
                    "Interest in sales, growth marketing, or business development",
                    "Strong communication and analytical skills",
                    "Self-starter comfortable working independently in a remote environment",
                    "Currently enrolled in an undergraduate program",
                ],
                "description": (
                    "Growth Intern (Sales) at Leland\n\n"
                    "Help drive Leland's growth by supporting the sales team in outreach, "
                    "user acquisition, and market analysis. Work directly with the founding "
                    "team to shape go-to-market strategy for a platform used by thousands "
                    "of ambitious people pursuing top careers.\n\n"
                    "Source: https://jobs.ashbyhq.com/leland"
                ),
            },
            {
                "title": "Growth & Ops Intern - Coach Recruiting (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.BUSINESS_ANALYST,
                "location": "Lehi, UT",
                "salary_min": 3500,
                "salary_max": 5000,
                "requirements": [
                    "Interest in operations, recruiting, or marketplace businesses",
                    "Strong organizational and communication skills",
                    "Ability to manage multiple priorities in a fast-paced environment",
                    "Available for hybrid work in Lehi, UT office",
                ],
                "description": (
                    "Growth & Ops Intern (Coach Recruiting) at Leland\n\n"
                    "Help build the supply side of Leland's coaching marketplace by recruiting "
                    "and onboarding world-class coaches. Work on operational processes, coach "
                    "quality assessment, and marketplace growth. Hybrid role at Leland HQ in Lehi, UT.\n\n"
                    "Source: https://jobs.ashbyhq.com/leland"
                ),
            },
        ],
    },

    # ── AtoB ──
    {
        "company_name": "AtoB",
        "email": "careers@atob.com",
        "name": "Vignan Velivela",
        "industry": "Fintech / Transportation",
        "company_size": "startup",
        "website": "https://www.atob.com",
        "slug": "atob",
        "description": (
            "AtoB is building Stripe for Transportation — modernizing the payments "
            "infrastructure for trucking and logistics. Trusted by thousands of fleets "
            "across the US. Series C with $205M+ raised at $800M valuation.\n\n"
            "Fund: Contrary, General Catalyst, Y Combinator | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Vignan Velivela", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/vignanv8"},
            {"name": "Tushar Misra", "title": "Co-Founder", "linkedin": ""},
            {"name": "Harshita Arora", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6000,
                "salary_max": 9000,
                "requirements": [
                    "Strong programming skills and experience building software",
                    "Interest in fintech, payments, or transportation technology",
                    "Track record of shipping features or side projects",
                    "Currently enrolled in CS or related undergraduate program",
                ],
                "description": (
                    "Software Engineer Intern at AtoB\n\n"
                    "Work alongside experienced engineers on critical parts of AtoB's stack. "
                    "Contribute to new features and systems across frontend, backend, and platform "
                    "projects end-to-end — from design to production ops. AtoB's intern-to-hire "
                    "program provides real-world experience building payments infrastructure "
                    "that powers thousands of trucking fleets.\n\n"
                    "Source: https://jobs.ashbyhq.com/atob"
                ),
            },
        ],
    },

    # ── Hallow ──
    {
        "company_name": "Hallow",
        "email": "careers@hallow.com",
        "name": "Alex Jones",
        "industry": "Consumer / Wellness",
        "company_size": "startup",
        "website": "https://hallow.com",
        "slug": "hallow-app",
        "description": (
            "Hallow is the #1 prayer and meditation app, downloaded 20M+ times worldwide. "
            "Features audio-guided Bible stories, prayers, meditations, and Christian music. "
            "Backed by top investors including Peter Thiel and featured in a Super Bowl commercial.\n\n"
            "Fund: Contrary | HQ: Chicago, IL"
        ),
        "founders": [
            {"name": "Alex Jones", "title": "CEO & Co-Founder", "linkedin": ""},
            {"name": "Erich Kerekes", "title": "Co-Founder", "linkedin": ""},
            {"name": "Alessandro DiSanto", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Strong programming skills (mobile or web development experience preferred)",
                    "Interest in consumer apps and building products used by millions",
                    "Ability to work in a fast-paced startup environment",
                    "Currently enrolled in CS or related undergraduate program",
                ],
                "description": (
                    "Software Engineering Intern at Hallow\n\n"
                    "Help build features for the #1 prayer and meditation app used by "
                    "millions worldwide. Work on mobile (iOS/Android) or web engineering "
                    "in a mission-driven startup that has been featured in a Super Bowl "
                    "commercial and is growing rapidly.\n\n"
                    "Source: https://jobs.contrary.com/jobs/hallow"
                ),
            },
        ],
    },

    # ── Pave ──
    {
        "company_name": "Pave",
        "email": "careers@pave.com",
        "name": "Matt Schulman",
        "industry": "HR Tech / Compensation",
        "company_size": "startup",
        "website": "https://www.pave.com",
        "slug": "pave",
        "description": (
            "Pave is the leading compensation management platform helping companies plan, "
            "communicate, and benchmark compensation in real-time. Trusted by 3,500+ companies "
            "and valued at $1.6B. Founded by a former Facebook engineer.\n\n"
            "Fund: Contrary, a16z, Y Combinator | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Matt Schulman", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/matt-schulman-15911861"},
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
                    "Strong programming skills in modern web technologies",
                    "Interest in HR tech, compensation data, or SaaS platforms",
                    "Experience with React, TypeScript, or Python preferred",
                    "Currently enrolled in CS or related undergraduate program",
                ],
                "description": (
                    "Software Engineering Intern at Pave\n\n"
                    "Help build the platform that powers compensation decisions at 3,500+ "
                    "companies. Work on real-time compensation benchmarking, pay equity "
                    "analysis, and total rewards communication tools. Pave processes "
                    "compensation data from millions of employees to provide market insights.\n\n"
                    "Source: https://www.pave.com/careers"
                ),
            },
        ],
    },

    # ── Nomic ──
    {
        "company_name": "Nomic",
        "email": "careers@nomic.ai",
        "name": "Nomic Team",
        "industry": "AI / Data Infrastructure",
        "company_size": "startup",
        "website": "https://www.nomic.ai",
        "slug": "nomic-ai",
        "description": (
            "Nomic builds models and infrastructure for knowledge agents, empowering "
            "organizations to unlock their complex, unstructured institutional knowledge "
            "using AI. Known for open-source embedding models and Atlas data visualization.\n\n"
            "Fund: Contrary, a16z | HQ: New York, NY"
        ),
        "founders": [],
        "jobs": [
            {
                "title": "ML Engineering Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "New York, NY",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Strong background in machine learning and deep learning",
                    "Experience with PyTorch, transformer architectures, or embedding models",
                    "Proficiency in Python and familiarity with ML infrastructure",
                    "Currently enrolled in CS, ML, or related graduate/undergraduate program",
                ],
                "description": (
                    "ML Engineering Intern at Nomic\n\n"
                    "Work on cutting-edge AI models and infrastructure for knowledge agents. "
                    "Nomic is known for its open-source embedding models (nomic-embed) and "
                    "Atlas data visualization platform. Contribute to models used by thousands "
                    "of developers and researchers worldwide.\n\n"
                    "Source: https://www.nomic.ai/careers"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # ── Anduril Industries (already in DB) ──
    {
        "company_name": "Anduril Industries",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Costa Mesa, CA",
                "salary_min": 8500,
                "salary_max": 9000,
                "requirements": [
                    "Rising senior returning to school for at least one quarter/semester after internship",
                    "Strong programming skills and CS fundamentals (algorithms, data structures)",
                    "U.S. Person status required for access to export-controlled data",
                    "Available for 12-week paid in-person internship",
                ],
                "description": (
                    "Software Engineer Intern at Anduril Industries (Summer 2026)\n\n"
                    "Join Anduril for a paid, in-person 12-week internship building defense "
                    "technology systems incorporating AI and robotics. Work on real production "
                    "systems at one of the fastest-growing defense tech companies.\n\n"
                    "Locations: Costa Mesa, CA; Irvine, CA; Atlanta, GA; Seattle, WA; "
                    "Boston, MA; Reston, VA\n"
                    "Compensation: ~$51/hr\n\n"
                    "Source: https://www.anduril.com/careers"
                ),
            },
        ],
    },

    # ── Ramp (already in DB) ──
    {
        "company_name": "Ramp",
        "jobs": [
            {
                "title": "Software Engineer Intern - Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 10500,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing Bachelor's degree (or higher) in CS or related field, graduating Dec 2026 - 2028",
                    "Track record of shipping high-quality products or a portfolio of side projects",
                    "Strong backend engineering fundamentals",
                    "Available for 12-16 week internship in NYC",
                ],
                "description": (
                    "Software Engineer Intern (Backend) at Ramp\n\n"
                    "Build the future of finance operations at Ramp. Work on payments, "
                    "corporate cards, vendor management, procurement, travel booking, and "
                    "automated bookkeeping. Ramp is the fastest-growing corporate card in "
                    "America. Includes housing stipend and catered lunches.\n\n"
                    "Compensation: ~$63/hr ($11,000/mo)\n\n"
                    "Source: https://ramp.com/emerging-talent"
                ),
            },
            {
                "title": "Software Engineer Intern - Frontend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 10500,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing Bachelor's degree (or higher) in CS or related field, graduating Dec 2026 - 2028",
                    "Track record of shipping high-quality products or a portfolio of side projects",
                    "Strong frontend engineering fundamentals (React, TypeScript)",
                    "Available for 10-week internship in NYC",
                ],
                "description": (
                    "Software Engineer Intern (Frontend) at Ramp\n\n"
                    "Build beautiful, performant interfaces for Ramp's finance platform "
                    "used by thousands of companies. Work on the product that's saving "
                    "companies 5% on spend on average. Includes housing stipend.\n\n"
                    "Compensation: ~$63/hr ($11,000/mo)\n\n"
                    "Source: https://ramp.com/emerging-talent"
                ),
            },
            {
                "title": "Software Engineer Intern - iOS (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 10500,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing Bachelor's degree (or higher) in CS or related field, graduating Dec 2026 - 2028",
                    "Experience with iOS development (Swift, SwiftUI)",
                    "Track record of shipping apps or a portfolio of mobile projects",
                    "Available for 10-week internship in NYC",
                ],
                "description": (
                    "Software Engineer Intern (iOS) at Ramp\n\n"
                    "Build Ramp's mobile experience used by finance teams on the go. "
                    "Work on expense management, receipt capture, and real-time spend "
                    "tracking features. Includes housing stipend.\n\n"
                    "Compensation: ~$63/hr ($11,000/mo)\n\n"
                    "Source: https://ramp.com/emerging-talent"
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
