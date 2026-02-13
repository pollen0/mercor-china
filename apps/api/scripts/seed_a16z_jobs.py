#!/usr/bin/env python3
"""
Seed intern jobs from a16z (Andreessen Horowitz) portfolio companies.

Usage:
    cd apps/api
    python -m scripts.seed_a16z_jobs

Source: jobs.a16z.com, individual company career pages (Feb 2026)
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


FIRM_NAME = "a16z"
SCRIPT_ID = "a16z"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Decagon ──
    {
        "company_name": "Decagon",
        "email": "careers@decagon.ai",
        "name": "Jesse Zhang",
        "industry": "AI / Enterprise / Customer Experience",
        "company_size": "startup",
        "website": "https://decagon.ai",
        "slug": "decagon",
        "description": (
            "Decagon is the leading conversational AI platform empowering brands like "
            "Cash App, Chime, and Oura Health to deploy AI agents across voice, chat, "
            "email, and SMS. Backed by a16z, Accel, Bain Capital Ventures, and Coatue.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Jesse Zhang", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/thejessezhang/"},
            {"name": "Ashwin Sreenivas", "title": "Co-Founder & President",
             "linkedin": "https://www.linkedin.com/in/sreenivasashwin/"},
        ],
        "jobs": [
            {
                "title": "Agent Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9600,
                "salary_max": 9600,
                "requirements": [
                    "Graduating by Summer 2027 with CS or related degree",
                    "Prior software engineering internship experience",
                    "Strong coding abilities and rapid development",
                    "Experience with multi-modal AI models a plus",
                ],
                "description": (
                    "Agent Software Engineer Intern at Decagon (a16z)\n\n"
                    "Design and build AI agents that outperform human agents in managing "
                    "complex customer interactions. Experiment with latest text and voice "
                    "models, then integrate them at scale with enterprise customers.\n\n"
                    "Compensation: $2,400/week + $10,000 housing stipend\n"
                    "On-site 5 days/week, May-September 2026\n\n"
                    "Source: https://jobs.ashbyhq.com/decagon/aa9c9d2a-aba9-429e-bf91-8303247fbcd6"
                ),
            },
        ],
    },

    # ── Whatnot ──
    {
        "company_name": "Whatnot",
        "email": "careers@whatnot.com",
        "name": "Grant LaFontaine",
        "industry": "E-commerce / Live Shopping / Marketplace",
        "company_size": "startup",
        "website": "https://whatnot.com",
        "slug": "whatnot",
        "description": (
            "Whatnot is the largest live shopping platform in North America and Europe. "
            "Buy, sell, and discover collectibles, trading cards, fashion, and more through "
            "community-driven live streams. Backed by a16z, DST Global, and CapitalG.\n\n"
            "Fund: a16z | HQ: Los Angeles, CA"
        ),
        "founders": [
            {"name": "Grant LaFontaine", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Logan Head", "title": "Co-Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Los Angeles / NYC / San Francisco / Seattle",
                "salary_min": 10000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing CS degree, graduating Dec 2026 or by Summer 2027",
                    "Some industry software engineering experience",
                    "Problem solver willing to build for 1M+ users",
                    "Able to quickly pick up new technologies",
                ],
                "description": (
                    "Software Engineer Intern at Whatnot (a16z)\n\n"
                    "Work on the largest live shopping platform. Build features for live "
                    "streams, implement growth tactics for buyer/seller flows, and build "
                    "systems at scale for a high-trust marketplace.\n\n"
                    "Compensation: ~$57.69/hr (~$10,000/month)\n"
                    "12-16 week hybrid internship\n\n"
                    "Source: https://jobs.ashbyhq.com/whatnot/8250532f-4bfd-4ee5-a041-4a2e54047cf7"
                ),
            },
        ],
    },

    # ── Ramp ──
    {
        "company_name": "Ramp",
        "email": "careers@ramp.com",
        "name": "Eric Glyman",
        "industry": "Fintech / Corporate Finance / Payments",
        "company_size": "startup",
        "website": "https://ramp.com",
        "slug": "ramp",
        "description": (
            "Ramp is a financial operations platform combining payments, corporate cards, "
            "vendor management, procurement, and automated bookkeeping. The fastest-growing "
            "fintech in history. Valued at $22.5B.\n\n"
            "Fund: a16z | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Eric Glyman", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Karim Atiyeh", "title": "Co-Founder & CTO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern, Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 11700,
                "salary_max": 11700,
                "requirements": [
                    "Pursuing BS+ in CS or related field",
                    "Expected graduation Dec 2026 - 2028",
                    "Strong programming fundamentals",
                    "Interest in fintech and financial operations",
                ],
                "description": (
                    "Software Engineer Intern (Backend) at Ramp (a16z)\n\n"
                    "Build the financial operations platform used by thousands of companies. "
                    "Work on payments, corporate cards, vendor management, and automated "
                    "bookkeeping at one of the fastest-growing fintechs.\n\n"
                    "Compensation: $11,700/month + housing stipend\n"
                    "12 or 16 weeks, May-August 2026\n\n"
                    "Source: https://jobs.ashbyhq.com/ramp/c50962b5-c641-4d44-bbe5-7f1d6e7ce51f"
                ),
            },
            {
                "title": "Software Engineer Intern, Frontend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 11700,
                "salary_max": 11700,
                "requirements": [
                    "Pursuing BS+ in CS or related field",
                    "Expected graduation Dec 2026 - 2028",
                    "Experience with React or modern frontend frameworks",
                    "Interest in fintech and user experience",
                ],
                "description": (
                    "Software Engineer Intern (Frontend) at Ramp (a16z)\n\n"
                    "Build beautiful, performant interfaces for the Ramp financial operations "
                    "platform. Ship features used by thousands of companies.\n\n"
                    "Compensation: $11,700/month + housing stipend\n"
                    "12 or 16 weeks, May-August 2026\n\n"
                    "Source: https://jobs.ashbyhq.com/ramp/31f7e045-9a51-4a75-9ffc-d815d6db6daa"
                ),
            },
        ],
    },

    # ── Glean ──
    {
        "company_name": "Glean",
        "email": "careers@glean.com",
        "name": "Arvind Jain",
        "industry": "AI / Enterprise Search / Knowledge Management",
        "company_size": "startup",
        "website": "https://glean.com",
        "slug": "glean",
        "description": (
            "Glean is an AI-powered knowledge management platform that helps organizations "
            "find, organize, and share information. Founded by ex-Google Distinguished "
            "Engineer Arvind Jain. Valued at $4.6B.\n\n"
            "Fund: a16z | HQ: Palo Alto, CA"
        ),
        "founders": [
            {"name": "Arvind Jain", "title": "Co-Founder & CEO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto / San Francisco, CA",
                "salary_min": 9900,
                "salary_max": 12000,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with BS/MS/PhD in CS",
                    "Prior internship in Backend, Infrastructure, Security, or ML/NLP/Search",
                    "Comfortable in fast-paced data-driven environment",
                    "Strong desire to learn with owner mentality",
                ],
                "description": (
                    "Software Engineer Intern at Glean (a16z)\n\n"
                    "Own a scoped, high-impact project end to end. Ship production code "
                    "for the enterprise AI search platform used by major companies.\n\n"
                    "Compensation: $57-$69/hr ($9,900-$12,000/month)\n"
                    "Hybrid (3-4 days/week in office)\n\n"
                    "Source: https://job-boards.greenhouse.io/gleanwork/jobs/4595665005"
                ),
            },
        ],
    },

    # ── Anduril ──
    {
        "company_name": "Anduril Industries",
        "email": "careers@anduril.com",
        "name": "Brian Schimpf",
        "industry": "Defense Technology / AI / Robotics",
        "company_size": "startup",
        "website": "https://anduril.com",
        "slug": "anduril",
        "description": (
            "Anduril builds advanced defense technology including autonomous systems, "
            "sensor fusion, and AI-powered platforms. Founded by Palmer Luckey (Oculus VR). "
            "Valued at $14B+.\n\n"
            "Fund: a16z | HQ: Costa Mesa, CA"
        ),
        "founders": [
            {"name": "Palmer Luckey", "title": "Founder",
             "linkedin": ""},
            {"name": "Brian Schimpf", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Trae Stephens", "title": "Co-Founder & Executive Chairman",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Costa Mesa, CA / Seattle, WA / Atlanta, GA / Boston, MA",
                "salary_min": 8800,
                "salary_max": 8800,
                "requirements": [
                    "Rising senior pursuing a technical degree",
                    "Strong C++, Go, Rust, Java, or Python skills",
                    "Understanding of fundamental CS concepts",
                    "Must be a US Person (ITAR/export control requirement)",
                ],
                "description": (
                    "Software Engineer Intern at Anduril Industries (a16z)\n\n"
                    "Build defense technology that protects. Work on autonomous systems, "
                    "sensor fusion, and AI platforms. 12-week paid in-person internship "
                    "with comprehensive benefits.\n\n"
                    "Compensation: ~$51/hr (~$8,800/month)\n"
                    "Multiple locations: Costa Mesa, Seattle, Atlanta, Boston, Reston\n\n"
                    "Source: https://job-boards.greenhouse.io/andurilindustries/jobs/4807506007"
                ),
            },
        ],
    },

    # ── Benchling ──
    {
        "company_name": "Benchling",
        "email": "careers@benchling.com",
        "name": "Sajith Wickramasekara",
        "industry": "Biotech / Life Sciences / Cloud Platform",
        "company_size": "startup",
        "website": "https://benchling.com",
        "slug": "benchling",
        "description": (
            "Benchling is the life sciences R&D cloud platform used by biotech and pharma "
            "companies to accelerate research. Founded by two MIT alumni.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Sajith Wickramasekara", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Ashu Singhal", "title": "Co-Founder & President",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10400,
                "salary_max": 10400,
                "requirements": [
                    "Currently enrolled in BS/MS in CS or STEM",
                    "Expected graduation Dec 2026 - Summer 2027",
                    "Prior software engineering internship preferred",
                    "Interest in life sciences and biotech",
                ],
                "description": (
                    "Software Engineer Intern at Benchling (a16z)\n\n"
                    "Build the R&D cloud platform used by leading biotech companies. "
                    "Work on platform/infrastructure or product teams with significant "
                    "ownership. 10-14 weeks, hybrid (4 days/week onsite).\n\n"
                    "Compensation: $60/hr (~$10,400/month)\n\n"
                    "Source: https://job-boards.greenhouse.io/benchling/jobs/7362703"
                ),
            },
        ],
    },

    # ── Figma ──
    {
        "company_name": "Figma",
        "email": "careers@figma.com",
        "name": "Dylan Field",
        "industry": "Design Tools / Collaboration / Developer Tools",
        "company_size": "startup",
        "website": "https://figma.com",
        "slug": "figma",
        "description": (
            "Figma is the collaborative design and prototyping platform used by millions. "
            "Founded by Dylan Field (Thiel Fellow) and Evan Wallace.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Dylan Field", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Evan Wallace", "title": "Co-Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA / New York, NY",
                "salary_min": 8850,
                "salary_max": 8850,
                "requirements": [
                    "Experience writing clean code in C++, JavaScript, Python, or Java",
                    "Comfortable with data structures and algorithms",
                    "Projects requiring technical problem-solving",
                    "Strong communication skills",
                ],
                "description": (
                    "Software Engineer Intern at Figma (a16z)\n\n"
                    "Embedded into small teams across Product Engineering, Tech Platform, "
                    "Infrastructure, Security, or Desktop Engineering. Work on Figma Design, "
                    "FigJam, Dev Mode, and more. Housing stipend and travel reimbursement.\n\n"
                    "Compensation: $51.06/hr (~$8,850/month)\n\n"
                    "Source: https://job-boards.greenhouse.io/figma/jobs/5602159004"
                ),
            },
        ],
    },

    # ── Vercel ──
    {
        "company_name": "Vercel",
        "email": "careers@vercel.com",
        "name": "Guillermo Rauch",
        "industry": "Developer Tools / Cloud / Infrastructure",
        "company_size": "startup",
        "website": "https://vercel.com",
        "slug": "vercel",
        "description": (
            "Vercel is the developer platform for frontend frameworks. Creators of Next.js. "
            "Used by companies like Washington Post, Notion, and Loom. Valued at $3.25B.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Guillermo Rauch", "title": "Founder & CEO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Engineering Summer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing CS degree, graduating Dec 2026 or May 2027",
                    "Strong JavaScript/TypeScript knowledge",
                    "Interest in developer tools and infrastructure",
                    "Experience with React or Next.js a plus",
                ],
                "description": (
                    "Engineering Summer Intern at Vercel (a16z)\n\n"
                    "Build the developer platform behind Next.js. Work on frontend cloud "
                    "infrastructure, developer experience, and edge computing.\n\n"
                    "Compensation: ~$9,500-$11,000/month (hybrid)\n\n"
                    "Source: https://vercel.com/careers/engineering-summer-intern-5628292004"
                ),
            },
        ],
    },

    # ── Flock Safety ──
    {
        "company_name": "Flock Safety",
        "email": "careers@flocksafety.com",
        "name": "Garrett Langley",
        "industry": "Public Safety / AI / Computer Vision",
        "company_size": "startup",
        "website": "https://flocksafety.com",
        "slug": "flock-safety",
        "description": (
            "Flock Safety builds AI-powered public safety technology including license "
            "plate readers and video analytics. Used by 5,000+ communities. "
            "Founded by Georgia Tech alumni. Valued at $7.5B.\n\n"
            "Fund: a16z | HQ: Atlanta, GA"
        ),
        "founders": [
            {"name": "Garrett Langley", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Matt Feury", "title": "Co-Founder & CTO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Atlanta, GA",
                "salary_min": 5200,
                "salary_max": 6100,
                "requirements": [
                    "Pursuing BS or MS in Computer Science or related field",
                    "Solid understanding of programming fundamentals and data structures",
                    "Experience with React, Node.js, or Go a plus",
                    "Must relocate to Atlanta for 12 weeks",
                ],
                "description": (
                    "Software Engineering Intern at Flock Safety (a16z)\n\n"
                    "Build full-stack applications using React, Node.js and Go. Treated "
                    "like full-time employees from day one — real projects with real impact.\n\n"
                    "Compensation: $30-$35/hr ($5,200-$6,100/month)\n"
                    "Dates: May 18 - August 7, 2026\n\n"
                    "Source: https://www.flocksafety.com/careers/positions"
                ),
            },
        ],
    },

    # ── Replit ──
    {
        "company_name": "Replit",
        "email": "careers@replit.com",
        "name": "Amjad Masad",
        "industry": "Developer Tools / AI / Cloud IDE",
        "company_size": "startup",
        "website": "https://replit.com",
        "slug": "replit",
        "description": (
            "Replit is the agentic software creation platform enabling anyone to build "
            "apps using natural language. 500,000+ business users. "
            "Founded by Amjad Masad (ex-Facebook). Valued at $3B.\n\n"
            "Fund: a16z | HQ: Foster City, CA"
        ),
        "founders": [
            {"name": "Amjad Masad", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/amjadmasad/"},
            {"name": "Faris Masad", "title": "Co-Founder",
             "linkedin": ""},
            {"name": "Haya Odeh", "title": "Co-Founder & Designer",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Foster City, CA",
                "salary_min": 8000,
                "salary_max": 10000,
                "requirements": [
                    "Enrolled in BS/MS/PhD in CS with at least one semester remaining",
                    "Proficiency in at least one programming language",
                    "Comfortable with full-stack development",
                    "Passion for developer tools, AI, or accessible technology",
                ],
                "description": (
                    "Software Engineering Intern at Replit (a16z)\n\n"
                    "Ship real features to millions of users. Build developer tools, AI "
                    "features, and cloud infrastructure. Hybrid (Mon/Wed/Fri in office).\n\n"
                    "12 weeks. Must be authorized to work in US.\n\n"
                    "Source: https://jobs.ashbyhq.com/replit/12737078-74c7-4e63-98a7-5e8da1e9deb1"
                ),
            },
        ],
    },

    # ── Northwood Space ──
    {
        "company_name": "Northwood Space",
        "email": "careers@northwoodspace.io",
        "name": "Bridgit Mendler",
        "industry": "Space / Satellite Ground Stations / Infrastructure",
        "company_size": "startup",
        "website": "https://northwoodspace.io",
        "slug": "northwood-space",
        "description": (
            "Northwood Space builds an advanced, scalable satellite ground station network "
            "powered by phased array technology. Founded by Bridgit Mendler (MIT/Harvard Law), "
            "Griffin Cleverly, and Shaurya Luthra (ex-Lockheed Martin).\n\n"
            "Fund: a16z | HQ: Torrance, CA"
        ),
        "founders": [
            {"name": "Bridgit Mendler", "title": "Co-Founder & CEO",
             "linkedin": "https://www.linkedin.com/in/bridgit-mendler/"},
            {"name": "Griffin Cleverly", "title": "Co-Founder & CTO",
             "linkedin": ""},
            {"name": "Shaurya Luthra", "title": "Co-Founder & Head of Software",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Torrance, CA",
                "salary_min": 5200,
                "salary_max": 5900,
                "requirements": [
                    "Strong interest in networking and scalable distributed systems",
                    "Experience with CI/CD and containerization (Docker, Terraform) a plus",
                    "ITAR compliance: must be US citizen or lawful permanent resident",
                    "Available 12 weeks (Jun-Aug 2026)",
                ],
                "description": (
                    "Software Engineer Intern at Northwood Space (a16z)\n\n"
                    "Support the design, implementation, and optimization of data movement "
                    "within a global ground station network infrastructure.\n\n"
                    "Compensation: $30-$34/hr + $4,000 housing stipend\n"
                    "Lunch and dinner catered daily. On-site.\n\n"
                    "Source: https://jobs.spacetalent.org/companies/northwood-space/jobs/42051292-software-engineer-intern-summer-2026"
                ),
            },
        ],
    },

    # ── Astranis ──
    {
        "company_name": "Astranis",
        "email": "careers@astranis.com",
        "name": "John Gedmark",
        "industry": "Space / Telecommunications / Satellites",
        "company_size": "startup",
        "website": "https://astranis.com",
        "slug": "astranis",
        "description": (
            "Astranis builds small geostationary telecommunications satellites to connect "
            "the 4 billion people without reliable internet. Raised $750M from a16z, "
            "BlackRock, and Fidelity. 400+ employees.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "John Gedmark", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Ryan McLinko", "title": "Co-Founder & CTO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Backend Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 5000,
                "requirements": [
                    "Pursuing BS or MS in Computer Science or equivalent",
                    "Strong Python proficiency",
                    "Database experience (Postgres)",
                    "Must be US citizen or permanent resident (ITAR)",
                ],
                "description": (
                    "Software Engineer Backend Intern at Astranis (a16z)\n\n"
                    "Design and build high-performance, reliable, mission-critical software "
                    "for commanding spacecraft and monitoring fleet telemetry. Full ownership "
                    "of features working across backend and infrastructure.\n\n"
                    "Compensation: $29/hr (~$5,000/month)\n"
                    "12 weeks, onsite 5 days/week at SF HQ\n\n"
                    "Source: https://job-boards.greenhouse.io/astranis/jobs/4648080006"
                ),
            },
        ],
    },

    # ── Neuralink ──
    {
        "company_name": "Neuralink",
        "email": "careers@neuralink.com",
        "name": "Elon Musk",
        "industry": "Neurotechnology / Brain-Computer Interfaces / Medical Devices",
        "company_size": "startup",
        "website": "https://neuralink.com",
        "slug": "neuralink",
        "description": (
            "Neuralink develops brain-computer interfaces to help people with paralysis "
            "control devices with their thoughts. Building the future of human-computer "
            "interaction.\n\n"
            "Fund: a16z | HQ: Fremont, CA"
        ),
        "founders": [
            {"name": "Elon Musk", "title": "Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Fremont, CA",
                "salary_min": 6100,
                "salary_max": 6100,
                "requirements": [
                    "Strong programming fundamentals",
                    "Rapid learner comfortable with ambiguity",
                    "Interest in neurotechnology or medical devices",
                    "Available 10-12 weeks onsite in Fremont",
                ],
                "description": (
                    "Software Engineer Intern at Neuralink (a16z)\n\n"
                    "Work on brain-computer interface technology across areas including "
                    "surgical robotics, implant communication, manufacturing automation, "
                    "cloud infrastructure, and BCI software.\n\n"
                    "Compensation: $35/hr (~$6,100/month)\n"
                    "10-12 weeks, onsite in Fremont\n\n"
                    "Source: https://job-boards.greenhouse.io/neuralink/jobs/6672977003"
                ),
            },
        ],
    },

    # ── Genesis Therapeutics ──
    {
        "company_name": "Genesis Therapeutics",
        "email": "careers@genesistherapeutics.ai",
        "name": "Evan Feinberg",
        "industry": "Biotech / AI Drug Discovery / Healthcare",
        "company_size": "startup",
        "website": "https://genesistherapeutics.ai",
        "slug": "genesis-therapeutics",
        "description": (
            "Genesis Therapeutics uses AI (GEMS platform) to discover new drugs by "
            "modeling molecular interactions. Raised $300M+. Supports teams in finance, "
            "healthcare, and bio-pharma.\n\n"
            "Fund: a16z | HQ: Burlingame, CA"
        ),
        "founders": [
            {"name": "Evan Feinberg", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Ben Sklaroff", "title": "Co-Founder & CTO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 4300,
                "salary_max": 5900,
                "requirements": [
                    "Strong programming skills (Python, TypeScript, or similar)",
                    "Interest in molecular visualization and scientific tooling",
                    "Experience with web development frameworks",
                    "Available for onsite work in San Mateo",
                ],
                "description": (
                    "Software Engineer Intern at Genesis Therapeutics (a16z)\n\n"
                    "Build tools for molecule/protein visualization, ML model analysis, "
                    "and chemical workflow management. Work alongside ML engineers and "
                    "medicinal chemists.\n\n"
                    "Compensation: $25-$34/hr ($4,300-$5,900/month)\n\n"
                    "Source: https://jobs.ashbyhq.com/genesis-therapeutics/37500c1e-9f2b-4b1a-89ab-53393a4a6ffe"
                ),
            },
            {
                "title": "ML Research Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Burlingame, CA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing BS/MS in CS, computational biology, or related field",
                    "Experience with generative modeling or molecular systems",
                    "Strong ML/AI fundamentals (PyTorch or TensorFlow)",
                    "Interest in AI drug discovery",
                ],
                "description": (
                    "ML Research Intern at Genesis Therapeutics (a16z)\n\n"
                    "Work on generative modeling of molecular systems. Apply AI to "
                    "drug discovery using the GEMS platform.\n\n"
                    "Source: https://jobs.ashbyhq.com/genesis-therapeutics/e2f3cc15-0006-4ab1-b38a-c941d4cc5ce9"
                ),
            },
        ],
    },

    # ── Lightspark ──
    {
        "company_name": "Lightspark",
        "email": "careers@lightspark.com",
        "name": "David Marcus",
        "industry": "Fintech / Crypto / Payments Infrastructure",
        "company_size": "startup",
        "website": "https://lightspark.com",
        "slug": "lightspark",
        "description": (
            "Lightspark builds Bitcoin and Lightning Network payment infrastructure. "
            "Founded by David Marcus, former President of PayPal and head of crypto at Meta.\n\n"
            "Fund: a16z | HQ: Culver City, CA (Los Angeles)"
        ),
        "founders": [
            {"name": "David Marcus", "title": "Founder & CEO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Culver City, CA (Los Angeles)",
                "salary_min": 4000,
                "salary_max": 5500,
                "requirements": [
                    "Pursuing CS degree with 2+ years completed",
                    "At least 1 prior software engineering internship",
                    "Python, React, TypeScript, or Rust experience",
                    "Interest in fintech, crypto, or payments",
                ],
                "description": (
                    "Software Engineer Intern at Lightspark (a16z)\n\n"
                    "Build production services, websites, and applications for Bitcoin "
                    "and Lightning Network payments. Work in-office at Culver City HQ.\n\n"
                    "Compensation: $23-$32/hr ($4,000-$5,500/month)\n\n"
                    "Source: https://jobs.ashbyhq.com/lightspark/1063b990-1f08-45ae-8155-506165e82c95"
                ),
            },
        ],
    },

    # ── Radiant Nuclear ──
    {
        "company_name": "Radiant Nuclear",
        "email": "careers@radiantnuclear.com",
        "name": "Doug Bernauer",
        "industry": "Energy / Nuclear / Clean Tech",
        "company_size": "startup",
        "website": "https://radiantnuclear.com",
        "slug": "radiant-nuclear",
        "description": (
            "Radiant builds portable nuclear microreactors for clean, reliable energy "
            "anywhere. Raised $154M. ~44 employees working on the future of energy.\n\n"
            "Fund: a16z | HQ: El Segundo, CA"
        ),
        "founders": [
            {"name": "Doug Bernauer", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Bob Urberger", "title": "Co-Founder & CTO",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "El Segundo, CA",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Pursuing BS/MS in Computer Science",
                    "Strong Python and C++ skills",
                    "Interest in simulation tooling for nuclear systems",
                    "100% onsite at El Segundo HQ",
                ],
                "description": (
                    "Software Engineering Intern at Radiant Nuclear (a16z)\n\n"
                    "Build software for portable nuclear microreactors. Work on simulation "
                    "tooling, control systems, and infrastructure for clean energy. "
                    "Includes equity and full health benefits.\n\n"
                    "Source: https://job-boards.greenhouse.io/radiant/jobs/4606581005"
                ),
            },
        ],
    },

    # ── Zipline ──
    {
        "company_name": "Zipline",
        "email": "careers@flyzipline.com",
        "name": "Keller Rinaudo Cliffton",
        "industry": "Drones / Logistics / Autonomous Delivery",
        "company_size": "startup",
        "website": "https://flyzipline.com",
        "slug": "zipline",
        "description": (
            "Zipline operates the world's largest autonomous drone delivery system, "
            "delivering medical supplies, food, and e-commerce packages. Operating in "
            "multiple countries. Backed by a16z, Sequoia, and Google Ventures.\n\n"
            "Fund: a16z | HQ: South San Francisco"
        ),
        "founders": [
            {"name": "Keller Rinaudo Cliffton", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Jeremy Baker", "title": "Co-Founder & CTO",
             "linkedin": ""},
            {"name": "Keenan Wyrobek", "title": "Co-Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Embedded Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "South San Francisco, CA / Dallas, TX",
                "salary_min": 6600,
                "salary_max": 7300,
                "requirements": [
                    "Pursuing degree in CS, EE, or related field",
                    "Experience with embedded systems or low-level programming",
                    "C/C++ proficiency",
                    "Full-time onsite availability",
                ],
                "description": (
                    "Embedded Engineering Intern at Zipline (a16z)\n\n"
                    "Work on the autonomous drone delivery system delivering medical "
                    "supplies and packages worldwide. Build embedded software for "
                    "flight systems and delivery mechanisms.\n\n"
                    "Compensation: $38-$42/hr ($6,600-$7,300/month)\n"
                    "May include housing stipend and relocation support\n\n"
                    "Source: https://www.flyzipline.com/careers"
                ),
            },
            {
                "title": "DevOps Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "South San Francisco, CA / Dallas, TX",
                "salary_min": 6600,
                "salary_max": 7300,
                "requirements": [
                    "Pursuing degree in CS or related field",
                    "Experience with cloud infrastructure or CI/CD",
                    "Linux and scripting experience",
                    "Full-time onsite availability",
                ],
                "description": (
                    "DevOps Engineering Intern at Zipline (a16z)\n\n"
                    "Build and maintain infrastructure for the world's largest autonomous "
                    "drone delivery system. Work on CI/CD, cloud systems, and deployment.\n\n"
                    "Compensation: $38-$42/hr ($6,600-$7,300/month)\n\n"
                    "Source: https://www.flyzipline.com/careers"
                ),
            },
        ],
    },

    # ── Vanta ──
    {
        "company_name": "Vanta",
        "email": "careers@vanta.com",
        "name": "Christina Cacioppo",
        "industry": "Security / Compliance / Enterprise Software",
        "company_size": "startup",
        "website": "https://vanta.com",
        "slug": "vanta",
        "description": (
            "Vanta automates security compliance (SOC 2, ISO 27001, HIPAA) for thousands "
            "of companies. Founded by Christina Cacioppo (Stanford, ex-Dropbox). "
            "Valued at $4.15B.\n\n"
            "Fund: a16z | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Christina Cacioppo", "title": "Co-Founder & CEO",
             "linkedin": ""},
            {"name": "Matt Spitz", "title": "Co-Founder",
             "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA / New York, NY",
                "salary_min": 8000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing 4-year degree or 2-year graduate degree in CS",
                    "Previous SWE internship experience required",
                    "Interest in security and compliance tooling",
                    "Strong programming fundamentals",
                ],
                "description": (
                    "Software Engineer Intern at Vanta (a16z)\n\n"
                    "Build automated security compliance tools used by thousands of "
                    "companies. Paired with experienced engineer mentor.\n\n"
                    "Source: https://www.vanta.com/company/careers"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS (companies already in DB)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = []


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DB OPERATIONS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def seed_new_company(session, company_data):
    """Create a new company with employer, org, membership, and jobs."""
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
    """Add new jobs to a company already in the DB."""
    company_name = entry["company_name"]
    employer = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()

    if not employer:
        print(f"  SKIP (not found): {company_name}")
        return 0

    existing_titles = {
        j.title for j in session.query(Job).filter(Job.employer_id == employer.id).all()
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
                errors.append(f"{company_name}: {e}")
                print(f"  ERROR: {e}")
            finally:
                session.close()

    if ADDITIONAL_JOBS:
        print(f"\n--- Phase 2: Additional Jobs ---")
        for entry in ADDITIONAL_JOBS:
            company_name = entry["company_name"]
            session = Session()
            try:
                print(f"\n[{company_name}]")
                jobs_added = add_jobs_to_existing(session, entry)
                session.commit()
                total_jobs += jobs_added
            except Exception as e:
                session.rollback()
                errors.append(f"{company_name}: {e}")
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
