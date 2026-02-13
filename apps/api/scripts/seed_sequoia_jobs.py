#!/usr/bin/env python3
"""
Seed intern jobs from Sequoia Capital portfolio companies.

FIRM: Sequoia Capital
SCRIPT ID: sequoia
SOURCE: jobs.sequoiacap.com + individual company career pages

Companies seeded (12 new + 1 additional):
  New: Harvey, Ramp, Clay, Notion, Zip, Figma, Stripe, Semgrep,
       Rippling, Mercury, Glean, Verkada
  Additional jobs: Athelas (already in DB as "Athelas")

Total: ~22 intern jobs across 13 companies
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
FIRM_NAME = "Sequoia"
SCRIPT_ID = "sequoia"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Harvey AI ──
    {
        "company_name": "Harvey",
        "email": "careers@harvey.ai",
        "name": "Winston Weinberg",
        "industry": "AI / Legal Technology",
        "company_size": "startup",
        "website": "https://www.harvey.ai",
        "slug": "harvey",
        "description": (
            "Harvey builds AI for legal professionals, helping law firms and "
            "legal departments work more efficiently. Used by a majority of the "
            "top 10 US law firms across 63 countries.\n\n"
            "Fund: Sequoia | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Winston Weinberg", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/winston-weinberg"},
            {"name": "Gabriel Pereyra", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing a Bachelor's in CS, Engineering or related field (graduating Fall 2026 - Spring 2028)",
                    "Prior experience building and shipping software from coursework, projects, or internships",
                    "Interest in building product-focused software and working cross-functionally",
                    "Collaborative mindset with strong communication skills",
                ],
                "description": (
                    "Software Engineering Intern on the Product Engineering team at Harvey. "
                    "Work alongside experienced engineers on projects powering AI products for "
                    "legal professionals. Gain hands-on experience across the stack, contribute "
                    "to real features, and experiment with cutting-edge LLMs.\n\n"
                    "12-week internship. Collaborate with AI, Legal, and GTM teams.\n\n"
                    "Source: https://www.harvey.ai/company/careers/b6509622-5c1e-4a3f-916b-6e56b8fd212f"
                ),
            },
        ],
    },

    # ── 2. Ramp ──
    {
        "company_name": "Ramp",
        "email": "careers@ramp.com",
        "name": "Eric Glyman",
        "industry": "Fintech / Corporate Finance",
        "company_size": "startup",
        "website": "https://ramp.com",
        "slug": "ramp",
        "description": (
            "Ramp is a corporate finance platform that helps businesses control spend, "
            "close books faster, and operate more efficiently. Valued at $32B with over "
            "$1B in annualized revenue.\n\n"
            "Fund: Sequoia | HQ: New York"
        ),
        "founders": [
            {"name": "Eric Glyman", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/eglyman"},
            {"name": "Karim Atiyeh", "title": "CTO & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern, Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 11000,
                "salary_max": 12000,
                "requirements": [
                    "Pursuing a B.S. or higher in CS or related field (graduating Dec 2026 - 2028)",
                    "Track record of shipping high quality products or portfolio of side projects",
                    "Ability to turn business and product ideas into engineering solutions",
                    "Desire to work in a fast-paced environment",
                ],
                "description": (
                    "Backend Software Engineer Intern at Ramp. Contribute to financial products "
                    "platform (Risk, Fraud, Treasury Management) and/or savings platform. Work closely "
                    "with product and business teams. 10-16 week internship at $11,700/mo.\n\n"
                    "Source: https://jobs.ashbyhq.com/ramp/c50962b5-c641-4d44-bbe5-7f1d6e7ce51f"
                ),
            },
            {
                "title": "Software Engineer Intern, Frontend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 11000,
                "salary_max": 12000,
                "requirements": [
                    "Pursuing a B.S. or higher in CS or related field (graduating Dec 2026 - 2028)",
                    "Experience with frontend technologies (React, TypeScript)",
                    "Track record of shipping high quality products or strong portfolio",
                    "Strong communication and collaboration skills",
                ],
                "description": (
                    "Frontend Software Engineer Intern at Ramp. Build user-facing financial tools "
                    "and interfaces for Ramp's corporate finance platform. Work with product and "
                    "design teams. 10-16 week internship.\n\n"
                    "Source: https://jobs.ashbyhq.com/ramp/31f7e045-9a51-4a75-9ffc-d815d6db6daa"
                ),
            },
        ],
    },

    # ── 3. Clay ──
    {
        "company_name": "Clay",
        "email": "careers@clay.com",
        "name": "Kareem Amin",
        "industry": "AI / Sales / Data Enrichment",
        "company_size": "startup",
        "website": "https://www.clay.com",
        "slug": "clay",
        "description": (
            "Clay helps companies scale outbound campaigns with AI-powered data enrichment "
            "from 50+ databases. Over 100,000 users including Anthropic, Intercom, and Notion.\n\n"
            "Fund: Sequoia | HQ: New York"
        ),
        "founders": [
            {"name": "Kareem Amin", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/kareemamin"},
            {"name": "Nicolae Rusan", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a B.S. in CS or related field (graduating 2026-2027)",
                    "Experience in JavaScript/TypeScript",
                    "Interest in AI/LLMs for workflow automation and data inference",
                    "Available for 12-week summer program (May - August)",
                ],
                "description": (
                    "Software Engineer Intern at Clay. Work on end-to-end software development "
                    "projects, build and maintain features using JavaScript/TypeScript. Leverage "
                    "LLMs for workflow automation, data inference, and text generation. Office in "
                    "Flatiron, NYC.\n\n"
                    "Source: https://www.builtinnyc.com/job/software-engineer-intern-summer-2025/289566"
                ),
            },
        ],
    },

    # ── 4. Notion ──
    {
        "company_name": "Notion",
        "email": "careers@makenotion.com",
        "name": "Ivan Zhao",
        "industry": "Productivity / SaaS",
        "company_size": "startup",
        "website": "https://www.notion.so",
        "slug": "notion",
        "description": (
            "Notion is an all-in-one AI workspace for notes, docs, project management, "
            "and wikis. Over 100 million users worldwide. Valued at $10B.\n\n"
            "Fund: Sequoia | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Ivan Zhao", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/ivanhzhao"},
            {"name": "Simon Last", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9100,
                "salary_max": 9800,
                "requirements": [
                    "Pursuing a Bachelor's or Master's in CS, Engineering, or related field",
                    "Strong programming fundamentals",
                    "Interest in product engineering, infrastructure, or security",
                    "Available May - September for 12-week internship in SF or NYC office",
                ],
                "description": (
                    "Software Engineer Intern at Notion. Paired with a mentor to build and ship "
                    "impactful projects across product engineering, mobile, infrastructure, and "
                    "security teams. $57/hr (Bachelors) or $61/hr (Masters).\n\n"
                    "Source: https://jobs.ashbyhq.com/notion/23ac2477-0008-4bed-b1c1-81f90a32e9e6"
                ),
            },
            {
                "title": "Software Engineer, AI Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9100,
                "salary_max": 9800,
                "requirements": [
                    "Pursuing a Bachelor's or Master's in CS, Engineering, or related field",
                    "Experience with machine learning or AI systems",
                    "Strong programming skills in Python or similar",
                    "Available for summer 2026 in SF or NYC office",
                ],
                "description": (
                    "AI-focused Software Engineer Intern at Notion. Work on AI features powering "
                    "Notion's AI workspace. Apply machine learning and LLM techniques to enhance "
                    "the Notion product experience.\n\n"
                    "Source: https://joinrise.co/notion/software-engineer-ai-intern-summer-2026-ee1y"
                ),
            },
        ],
    },

    # ── 5. Zip ──
    {
        "company_name": "Zip",
        "email": "careers@ziphq.com",
        "name": "Rujul Zaparde",
        "industry": "Enterprise SaaS / Procurement",
        "company_size": "startup",
        "website": "https://ziphq.com",
        "slug": "zip-hq",
        "description": (
            "Zip is the leading procurement orchestration platform, bringing a consumer-grade "
            "experience to B2B purchasing. Backed by Sequoia, a16z, and Bessemer. Serves "
            "companies like OpenAI, Discover, and Sephora.\n\n"
            "Fund: Sequoia | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Rujul Zaparde", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/rujulzaparde"},
            {"name": "Lu Cheng", "title": "CTO & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8800,
                "salary_max": 9600,
                "requirements": [
                    "Pursuing a degree in CS or related field (graduating Dec 2026 - June 2027)",
                    "Experience with web applications and API development",
                    "Ability to quickly learn new frameworks and programming languages",
                    "Strong communication skills",
                ],
                "description": (
                    "Software Engineer Intern at Zip. Build Zip's core products and architecture, "
                    "shipping features used immediately by customers. Tech stack: Python, "
                    "JavaScript/TypeScript, React, GraphQL. $55-60/hr.\n\n"
                    "Previous intern projects: internal AI bot, dev environment bootstrapping tool, "
                    "virtual card auto-lock feature.\n\n"
                    "Source: https://jobs.ashbyhq.com/zip/2bad03a8-4e98-480e-b8cb-bc65d36e429f"
                ),
            },
        ],
    },

    # ── 6. Figma ──
    {
        "company_name": "Figma",
        "email": "careers@figma.com",
        "name": "Dylan Field",
        "industry": "Design / Developer Tools",
        "company_size": "startup",
        "website": "https://www.figma.com",
        "slug": "figma",
        "description": (
            "Figma is a collaborative design platform used by millions of designers and "
            "developers worldwide. IPO on NYSE in 2025. Products include Figma Design, "
            "FigJam, and Dev Mode.\n\n"
            "Fund: Sequoia | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Dylan Field", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/dylanfield"},
            {"name": "Evan Wallace", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8200,
                "salary_max": 8800,
                "requirements": [
                    "Strong programming fundamentals in JavaScript, Python, or Java",
                    "Understanding of core CS concepts (data structures, algorithms)",
                    "Excellent collaboration and communication skills",
                    "Interest in design tools, creative software, or developer platforms",
                ],
                "description": (
                    "Software Engineer Intern at Figma. Matched with a team aligned to your skills "
                    "and interests: Product Engineering (Figma Design, FigJam, Dev Mode), Tech Platform, "
                    "Infrastructure, Security, or Desktop Engineering. $51/hr + housing stipend.\n\n"
                    "Source: https://job-boards.greenhouse.io/figma/jobs/5602159004"
                ),
            },
        ],
    },

    # ── 7. Stripe ──
    {
        "company_name": "Stripe",
        "email": "careers@stripe.com",
        "name": "Patrick Collison",
        "industry": "Fintech / Payments",
        "company_size": "startup",
        "website": "https://stripe.com",
        "slug": "stripe",
        "description": (
            "Stripe is the financial infrastructure platform for the internet, powering "
            "payments and commerce for millions of businesses. Founded by Patrick and John "
            "Collison.\n\n"
            "Fund: Sequoia | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Patrick Collison", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/patrickcollison"},
            {"name": "John Collison", "title": "President & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 10800,
                "requirements": [
                    "At least 2 years of university education or equivalent work experience",
                    "Understanding of and experience writing high quality pull requests with good test coverage",
                    "One or more areas of specialized knowledge balanced with general skills",
                    "Available for 12 or 16 week internship",
                ],
                "description": (
                    "Software Engineer Intern at Stripe. Tackle important projects to increase "
                    "global commerce. Work with many systems and technologies, gain experience in "
                    "systems design and testing. $62.50/hr + housing benefit.\n\n"
                    "Source: https://stripe.com/jobs/listing/software-engineer-intern-summer/7210115"
                ),
            },
        ],
    },

    # ── 8. Semgrep ──
    {
        "company_name": "Semgrep",
        "email": "careers@semgrep.dev",
        "name": "Isaac Evans",
        "industry": "Security / Developer Tools",
        "company_size": "startup",
        "website": "https://semgrep.dev",
        "slug": "semgrep",
        "description": (
            "Semgrep builds software security tools used by companies like Figma, Dropbox, "
            "Slack, and Snowflake. Open-source static analysis for finding bugs and enforcing "
            "code standards.\n\n"
            "Fund: Sequoia | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Isaac Evans", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/isaacevans"},
            {"name": "Drew Dennison", "title": "Co-Founder", "linkedin": ""},
            {"name": "Luke O'Malley", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern, Cloud Platform (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9600,
                "salary_max": 10400,
                "requirements": [
                    "Multiple college courses in CS or equivalent experience",
                    "Interest in software security and developer enablement",
                    "Ability to work in SF office 5 days/week",
                    "Experience with Python, PostgreSQL, TypeScript, or React",
                ],
                "description": (
                    "Software Engineer Intern on the Cloud Platform team at Semgrep. Design and "
                    "ship new features in a full-stack codebase using Python, PostgreSQL, TypeScript, "
                    "and React. $2,400/week.\n\n"
                    "Source: https://www.builtinsf.com/job/software-engineer-intern-cloud-platform/7007424"
                ),
            },
            {
                "title": "Software Engineer Intern, Program Analysis (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9600,
                "salary_max": 10400,
                "requirements": [
                    "Experience with functional programming languages",
                    "Interest in compiler and programming language work",
                    "Multiple college courses in CS or equivalent experience",
                    "Ability to work in SF office 5 days/week",
                ],
                "description": (
                    "Software Engineer Intern on the Program Analysis team at Semgrep. Work on "
                    "compiler and programming language tooling for static code analysis. $2,400/week. "
                    "Start dates: May 26 or June 23, 2026.\n\n"
                    "Source: https://semgrep.dev/about/careers"
                ),
            },
        ],
    },

    # ── 9. Rippling ──
    {
        "company_name": "Rippling",
        "email": "careers@rippling.com",
        "name": "Parker Conrad",
        "industry": "HR / Finance / Enterprise SaaS",
        "company_size": "startup",
        "website": "https://www.rippling.com",
        "slug": "rippling",
        "description": (
            "Rippling is a workforce management platform that unifies HR, IT, and finance. "
            "Manages everything from payroll to device management in one system. Hiring 150+ "
            "interns in 2026.\n\n"
            "Fund: Sequoia | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Parker Conrad", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/parkerconrad"},
        ],
        "jobs": [
            {
                "title": "Full Stack Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10500,
                "salary_max": 11500,
                "requirements": [
                    "Currently enrolled in Bachelor's or Master's in CS or related field",
                    "At least 1 semester/quarter remaining after internship",
                    "Previous internship/co-op experience in software engineering",
                    "Experience with Python (backend) and JavaScript/HTML/CSS (frontend)",
                ],
                "description": (
                    "Full Stack Software Engineer Intern at Rippling. Join one of many teams in "
                    "Summer 2026 (May-August) to develop robust products, implement new features, "
                    "and solve complex problems. $66/hr. Hybrid model (3 days in-office).\n\n"
                    "Source: https://ats.rippling.com/rippling/jobs/2f242b59-eee3-41f5-a5d7-55b7545cb9fb"
                ),
            },
        ],
    },

    # ── 10. Mercury ──
    {
        "company_name": "Mercury",
        "email": "careers@mercury.com",
        "name": "Immad Akhund",
        "industry": "Fintech / Banking",
        "company_size": "startup",
        "website": "https://mercury.com",
        "slug": "mercury",
        "description": (
            "Mercury is a financial technology company building banking for startups and SMBs. "
            "$500M+ ARR and profitable. Raised $300M from Sequoia at $3.5B valuation.\n\n"
            "Fund: Sequoia | HQ: San Francisco (Remote-friendly)"
        ),
        "founders": [
            {"name": "Immad Akhund", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/iakhund"},
            {"name": "Max Tagher", "title": "Co-Founder", "linkedin": ""},
            {"name": "Jason Zhang", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8800,
                "salary_max": 9500,
                "requirements": [
                    "Currently enrolled in an academic program (undergraduate or graduate)",
                    "Interest in fintech and banking technology",
                    "Familiarity with Haskell, TypeScript, or SQL is a plus",
                    "Available for 12-16 week summer internship (May-August)",
                ],
                "description": (
                    "Software Engineering Intern at Mercury. Work on backend, frontend, or "
                    "full-stack projects building banking products for startups. $55/hr. Remote-"
                    "friendly with offices in SF and NYC.\n\n"
                    "Source: https://startup.jobs/software-engineering-intern-mercury-banking-for-startups-4069017"
                ),
            },
        ],
    },

    # ── 11. Glean ──
    {
        "company_name": "Glean",
        "email": "careers@glean.com",
        "name": "Arvind Jain",
        "industry": "AI / Enterprise Search",
        "company_size": "startup",
        "website": "https://www.glean.com",
        "slug": "glean",
        "description": (
            "Glean is an AI-powered enterprise search platform that connects and searches "
            "across all company tools and applications. $100M+ ARR, valued at $7.2B. Founded "
            "by ex-Google Distinguished Engineer.\n\n"
            "Fund: Sequoia | HQ: Palo Alto"
        ),
        "founders": [
            {"name": "Arvind Jain", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/jain-arvind"},
            {"name": "T.R. Vishwanath", "title": "Co-Founder", "linkedin": ""},
            {"name": "Tony Gentilcore", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 9100,
                "salary_max": 11000,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with B.S., M.S., or Ph.D. in CS or equivalent",
                    "Interest in backend services, product engineering, ML/AI/search, or infrastructure",
                    "Hybrid work (3-4 days/week in Palo Alto or SF office)",
                    "Strong programming and problem-solving skills",
                ],
                "description": (
                    "Software Engineer Intern at Glean. Learn and contribute across the stack "
                    "including backend services, product engineering, ML/AI/search, infrastructure, "
                    "and security. $57-69/hr depending on experience.\n\n"
                    "Source: https://job-boards.greenhouse.io/gleanwork/jobs/4595665005"
                ),
            },
        ],
    },

    # ── 12. Verkada ──
    {
        "company_name": "Verkada",
        "email": "careers@verkada.com",
        "name": "Filip Kaliszan",
        "industry": "Security / IoT / Hardware-Software",
        "company_size": "startup",
        "website": "https://www.verkada.com",
        "slug": "verkada",
        "description": (
            "Verkada builds cloud-managed building security systems — cameras, access control, "
            "environmental sensors, and alarms. Protects 10,000+ organizations. Nearly $1B in "
            "annual revenue.\n\n"
            "Fund: Sequoia | HQ: San Mateo"
        ),
        "founders": [
            {"name": "Filip Kaliszan", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/filipkaliszan"},
            {"name": "James Ren", "title": "Co-Founder", "linkedin": ""},
            {"name": "Benjamin Bercovitz", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern, Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 9000,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing a Bachelor's or Master's in CS or similar technical field",
                    "Familiarity with Python, Golang, Distributed Systems, or AWS/Docker",
                    "Prior internship experience developing and launching products",
                    "Available for summer internship at San Mateo HQ",
                ],
                "description": (
                    "Backend Software Engineering Intern at Verkada. Build and ship features for "
                    "cloud-managed security infrastructure used by customers globally. Monthly "
                    "housing stipend + competitive hourly wages.\n\n"
                    "Source: https://job-boards.greenhouse.io/verkada/jobs/4836993007"
                ),
            },
            {
                "title": "Software Engineering Intern, Mobile (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 9000,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing a Bachelor's or Master's in CS or similar technical field",
                    "Experience with iOS or Android development",
                    "Interest in building native mobile applications",
                    "Available for summer internship at San Mateo HQ",
                ],
                "description": (
                    "Mobile Engineering Intern at Verkada. Collaborate cross-functionally to "
                    "build native mobile experiences for iOS and Android applications controlling "
                    "Verkada security systems.\n\n"
                    "Source: https://www.builtinsf.com/job/software-engineering-intern-mobile-2026/7164930"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — Athelas already exists in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    {
        "company_name": "Athelas",
        "jobs": [
            {
                "title": "Software Engineering Intern, Sequoia (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 8000,
                "salary_max": 10000,
                "requirements": [
                    "Prior internship or project experience building production-like systems",
                    "Familiarity with modern frontend frameworks (React) or mobile (iOS/Android)",
                    "Exposure to cloud/container technologies (AWS/GCP, Docker, Kubernetes)",
                    "Knowledge of secure API design and data modeling",
                ],
                "description": (
                    "Software Engineering Intern at Commure + Athelas. Join the engineering team "
                    "building AI solutions for healthcare: ambient AI clinical documentation, "
                    "provider copilots, autonomous coding, and revenue cycle management. Backed by "
                    "Sequoia, General Catalyst, Y Combinator.\n\n"
                    "Source: https://jobs.ashbyhq.com/Commure-Athelas/566a84fb-d93e-4177-ac07-3c16d3ae8e8d"
                ),
            },
        ],
    },
    {
        "company_name": "Ramp",
        "jobs": [
            {
                "title": "Software Engineer Intern, Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 11000,
                "salary_max": 12000,
                "requirements": [
                    "Pursuing a B.S. or higher in CS or related field (graduating Dec 2026 - 2028)",
                    "Track record of shipping high quality products or portfolio of side projects",
                    "Ability to turn business and product ideas into engineering solutions",
                    "Desire to work in a fast-paced environment",
                ],
                "description": (
                    "Backend Software Engineer Intern at Ramp. Contribute to financial products "
                    "platform (Risk, Fraud, Treasury Management) and/or savings platform. Work closely "
                    "with product and business teams. 10-16 week internship at $11,700/mo.\n\n"
                    "Source: https://jobs.ashbyhq.com/ramp/c50962b5-c641-4d44-bbe5-7f1d6e7ce51f"
                ),
            },
            {
                "title": "Software Engineer Intern, Frontend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "New York, NY",
                "salary_min": 11000,
                "salary_max": 12000,
                "requirements": [
                    "Pursuing a B.S. or higher in CS or related field (graduating Dec 2026 - 2028)",
                    "Experience with frontend technologies (React, TypeScript)",
                    "Track record of shipping high quality products or strong portfolio",
                    "Strong communication and collaboration skills",
                ],
                "description": (
                    "Frontend Software Engineer Intern at Ramp. Build user-facing financial tools "
                    "and interfaces for Ramp's corporate finance platform. Work with product and "
                    "design teams. 10-16 week internship.\n\n"
                    "Source: https://jobs.ashbyhq.com/ramp/31f7e045-9a51-4a75-9ffc-d815d6db6daa"
                ),
            },
        ],
    },
    {
        "company_name": "Zip",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8800,
                "salary_max": 9600,
                "requirements": [
                    "Pursuing a degree in CS or related field (graduating Dec 2026 - June 2027)",
                    "Experience with web applications and API development",
                    "Ability to quickly learn new frameworks and programming languages",
                    "Strong communication skills",
                ],
                "description": (
                    "Software Engineer Intern at Zip. Build Zip's core products and architecture, "
                    "shipping features used immediately by customers. Tech stack: Python, "
                    "JavaScript/TypeScript, React, GraphQL. $55-60/hr.\n\n"
                    "Source: https://jobs.ashbyhq.com/zip/2bad03a8-4e98-480e-b8cb-bc65d36e429f"
                ),
            },
        ],
    },
    {
        "company_name": "Figma",
        "jobs": [
            {
                "title": "Software Engineer Intern (2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8200,
                "salary_max": 8800,
                "requirements": [
                    "Strong programming fundamentals in JavaScript, Python, or Java",
                    "Understanding of core CS concepts (data structures, algorithms)",
                    "Excellent collaboration and communication skills",
                    "Interest in design tools, creative software, or developer platforms",
                ],
                "description": (
                    "Software Engineer Intern at Figma. Matched with a team aligned to your skills "
                    "and interests: Product Engineering (Figma Design, FigJam, Dev Mode), Tech Platform, "
                    "Infrastructure, Security, or Desktop Engineering. $51/hr + housing stipend.\n\n"
                    "Source: https://job-boards.greenhouse.io/figma/jobs/5602159004"
                ),
            },
        ],
    },
    {
        "company_name": "Stripe",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 10800,
                "requirements": [
                    "At least 2 years of university education or equivalent work experience",
                    "Understanding of and experience writing high quality pull requests with good test coverage",
                    "One or more areas of specialized knowledge balanced with general skills",
                    "Available for 12 or 16 week internship",
                ],
                "description": (
                    "Software Engineer Intern at Stripe. Tackle important projects to increase "
                    "global commerce. Work with many systems and technologies, gain experience in "
                    "systems design and testing. $62.50/hr + housing benefit.\n\n"
                    "Source: https://stripe.com/jobs/listing/software-engineer-intern-summer/7210115"
                ),
            },
        ],
    },
    {
        "company_name": "Rippling",
        "jobs": [
            {
                "title": "Full Stack Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10500,
                "salary_max": 11500,
                "requirements": [
                    "Currently enrolled in Bachelor's or Master's in CS or related field",
                    "At least 1 semester/quarter remaining after internship",
                    "Previous internship/co-op experience in software engineering",
                    "Experience with Python (backend) and JavaScript/HTML/CSS (frontend)",
                ],
                "description": (
                    "Full Stack Software Engineer Intern at Rippling. Join one of many teams in "
                    "Summer 2026 (May-August) to develop robust products, implement new features, "
                    "and solve complex problems. $66/hr. Hybrid model (3 days in-office).\n\n"
                    "Source: https://ats.rippling.com/rippling/jobs/2f242b59-eee3-41f5-a5d7-55b7545cb9fb"
                ),
            },
        ],
    },
    {
        "company_name": "Glean",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 9100,
                "salary_max": 11000,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with B.S., M.S., or Ph.D. in CS or equivalent",
                    "Interest in backend services, product engineering, ML/AI/search, or infrastructure",
                    "Hybrid work (3-4 days/week in Palo Alto or SF office)",
                    "Strong programming and problem-solving skills",
                ],
                "description": (
                    "Software Engineer Intern at Glean. Learn and contribute across the stack "
                    "including backend services, product engineering, ML/AI/search, infrastructure, "
                    "and security. $57-69/hr depending on experience.\n\n"
                    "Source: https://job-boards.greenhouse.io/gleanwork/jobs/4595665005"
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
