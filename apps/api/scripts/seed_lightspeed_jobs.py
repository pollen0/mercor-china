#!/usr/bin/env python3
"""
Seed intern jobs from Lightspeed Venture Partners portfolio companies.

FIRM: Lightspeed Venture Partners (LSVP)
JOB BOARD: https://jobs.lsvp.com
SCRIPT ID: lightspeed

Companies included (10 companies, 14 jobs):
- Affirm (FinTech / BNPL)
- Snap Inc. (Social Media / AR)
- Rubrik (Data Security / Cloud)
- Glean (AI / Enterprise Search)
- Databricks (Data / AI / Analytics)
- Rippling (HR / IT / Finance Platform)
- Anduril Industries (Defense Technology)
- Abridge (Healthcare / AI)
- Nominal (Hardware Data Platform)
- Epic Games (Gaming / Interactive Entertainment)
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
FIRM_NAME = "Lightspeed Venture Partners"
SCRIPT_ID = "lightspeed"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Affirm ──
    {
        "company_name": "Affirm",
        "email": "careers@affirm.com",
        "name": "Max Levchin",
        "industry": "FinTech / Consumer Banking",
        "company_size": "enterprise",
        "website": "https://www.affirm.com",
        "slug": "affirm",
        "description": (
            "Affirm provides honest financial products that improve lives. "
            "As the leading buy-now-pay-later platform, Affirm offers transparent "
            "payment options with no hidden fees, helping millions of consumers "
            "make purchases responsibly.\n\n"
            "Fund: Lightspeed (Series B lead) | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Max Levchin", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/mlevchin"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 9500,
                "requirements": [
                    "Experience with Python, C/C++, or Java",
                    "Familiarity with frontend development (React, JavaScript)",
                    "Understanding of object-oriented programming",
                    "Interest in deployment and testing frameworks",
                    "Passion for changing consumer banking",
                ],
                "description": (
                    "Software Engineering Intern at Affirm (Summer 2026)\n\n"
                    "As an intern at Affirm, you will be a contributing member of the "
                    "engineering team, developing and shipping a project that verifies "
                    "it works in production. 12-16 week internship with dedicated mentor. "
                    "Projects are meaningful — teams depend on your work. Present to the "
                    "entire engineering org at the end of the internship.\n\n"
                    "$55/hr | Hybrid (SF office 3 days/week)\n\n"
                    "Source: https://job-boards.greenhouse.io/affirm/jobs/7528020003"
                ),
            },
        ],
    },

    # ── 2. Snap Inc. ──
    {
        "company_name": "Snap Inc.",
        "email": "careers@snap.com",
        "name": "Evan Spiegel",
        "industry": "Social Media / AR Technology",
        "company_size": "enterprise",
        "website": "https://www.snap.com",
        "slug": "snap-inc",
        "description": (
            "Snap Inc. is a technology company that believes the camera presents "
            "the greatest opportunity to improve the way people live and communicate. "
            "The company created Snapchat, Spectacles, and is a leader in augmented "
            "reality technology.\n\n"
            "Fund: Lightspeed (first VC investor, seed) | HQ: Santa Monica"
        ),
        "founders": [
            {"name": "Evan Spiegel", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/evanspiegel"},
            {"name": "Bobby Murphy", "title": "CTO & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Los Angeles, CA",
                "salary_min": 10000,
                "salary_max": 11600,
                "requirements": [
                    "Currently enrolled in a Bachelor's or Master's program in Computer Science or related field",
                    "Passion for Snapchat and creative technology",
                    "Strong programming fundamentals",
                    "Interest in backend, full stack, iOS, or Android development",
                ],
                "description": (
                    "Software Engineer Intern at Snap Inc. (Summer 2026)\n\n"
                    "Join a 13-week internship program with projects focused on various "
                    "technical tracks including backend, full stack, iOS, and Android. "
                    "Work on meaningful projects, expand your skill sets, and see the "
                    "results of your work go live. Also available in Palo Alto, CA; "
                    "New York, NY; and Bellevue, WA.\n\n"
                    "~$67/hr | Multiple US locations\n\n"
                    "Source: https://careers.snap.com/job?id=H225SWEI"
                ),
            },
        ],
    },

    # ── 3. Rubrik ──
    {
        "company_name": "Rubrik",
        "email": "careers@rubrik.com",
        "name": "Bipul Sinha",
        "industry": "Data Security / Cloud Infrastructure",
        "company_size": "enterprise",
        "website": "https://www.rubrik.com",
        "slug": "rubrik",
        "description": (
            "Rubrik is a leader in data security, providing Zero Trust Data Security "
            "to help organizations achieve business resilience against cyberattacks, "
            "malicious insiders, and operational disruptions. Rubrik Security Cloud "
            "secures data across enterprise, cloud, and SaaS.\n\n"
            "Fund: Lightspeed (Series A lead, largest shareholder) | HQ: Palo Alto"
        ),
        "founders": [
            {"name": "Bipul Sinha", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/bipulsinha"},
        ],
        "jobs": [
            {
                "title": "Frontend Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 10400,
                "salary_max": 10400,
                "requirements": [
                    "Exposure to GraphQL APIs, responsive design, and modern frontend tools",
                    "Experience transforming Figma designs into React components using JSX and CSS",
                    "Ability to fetch and manage data through GraphQL APIs",
                    "Participation in code reviews and pair programming",
                ],
                "description": (
                    "Frontend Engineering Intern at Rubrik (Summer 2026)\n\n"
                    "Work with talented developers and designers to build intuitive, "
                    "visually stunning user interfaces for Rubrik Security Cloud. "
                    "Transform Figma designs into dynamic, responsive React components. "
                    "12-week program with 1:1 mentorship, social events, professional "
                    "development workshops, and volunteering events. Recognized as a "
                    "Top 100 Internship Program and Campus Forward Award Winner.\n\n"
                    "$60/hr | Palo Alto, CA\n\n"
                    "Source: https://www.rubrik.com/company/careers/departments/job.7071669"
                ),
            },
        ],
    },

    # ── 4. Glean ──
    {
        "company_name": "Glean",
        "email": "careers@glean.com",
        "name": "Arvind Jain",
        "industry": "AI / Enterprise Search",
        "company_size": "startup",
        "website": "https://www.glean.com",
        "slug": "glean",
        "description": (
            "Glean is the AI-powered work assistant that brings every team the answers "
            "they need. Founded by ex-Google distinguished engineer Arvind Jain, Glean "
            "integrates with enterprise tools to provide intelligent search and knowledge "
            "management. Named one of Fast Company's Most Innovative Companies (Top 10, 2025).\n\n"
            "Fund: Lightspeed | HQ: Palo Alto"
        ),
        "founders": [
            {"name": "Arvind Jain", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/jain-arvind"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 9900,
                "salary_max": 12000,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with B.S., M.S. or Ph.D. in Computer Science or equivalent",
                    "Team player with strong desire to learn and owner mentality",
                    "Comfortable in a fast-paced, data-driven environment",
                    "Prior internship experience in relevant areas preferred",
                ],
                "description": (
                    "Software Engineer Intern at Glean (Summer 2026)\n\n"
                    "Own a scoped, high-impact project end to end — from defining the "
                    "problem and writing a design, to building, testing, launching, and "
                    "measuring outcomes. Contribute across the stack based on your interests: "
                    "backend services, product engineering, ML/AI/search, infrastructure, "
                    "security, and more. Hybrid (3-4 days/week in Palo Alto or SF office).\n\n"
                    "$57-$69/hr | Palo Alto or San Francisco, CA\n\n"
                    "Source: https://job-boards.greenhouse.io/gleanwork/jobs/4595665005"
                ),
            },
        ],
    },

    # ── 5. Databricks ──
    {
        "company_name": "Databricks",
        "email": "careers@databricks.com",
        "name": "Ali Ghodsi",
        "industry": "Data / AI / Analytics",
        "company_size": "enterprise",
        "website": "https://www.databricks.com",
        "slug": "databricks",
        "description": (
            "Databricks is the data and AI company. Originally created by the team that "
            "built Apache Spark, Databricks provides a unified analytics platform combining "
            "data engineering, data science, machine learning, and analytics on a single "
            "lakehouse architecture.\n\n"
            "Fund: Lightspeed | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Ali Ghodsi", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/alighodsi"},
            {"name": "Matei Zaharia", "title": "CTO & Co-Founder", "linkedin": ""},
            {"name": "Ion Stoica", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10400,
                "salary_max": 10400,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with degree in Computer Science, Engineering, or related field",
                    "Implementation skills in Python, Java, or C++",
                    "Good knowledge of algorithms, data structures, and OOP principles",
                    "Excited to solve ambiguous problems with a collaborative team",
                ],
                "description": (
                    "Software Engineering Intern at Databricks (Summer 2026)\n\n"
                    "Join one of many teams including full stack, backend, infrastructure, "
                    "systems, tools, cloud, databases, and customer-facing products. "
                    "Options: Winter 16-week co-op, Summer 16-week co-op, or Summer "
                    "12-week internship. Dedicated mentor and intern cohort with "
                    "connections to engineers, other interns, and leaders across the company.\n\n"
                    "$60/hr | San Francisco, CA\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/software-engineering-intern-2026-6866531002"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Francisco, CA",
                "salary_min": 10400,
                "salary_max": 10400,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with degree in Data Science, Statistics, CS, or related field",
                    "Experience with Python, SQL, and data analysis frameworks",
                    "Knowledge of machine learning and statistical methods",
                    "Strong analytical and problem-solving skills",
                ],
                "description": (
                    "Data Science Intern at Databricks (Summer 2026)\n\n"
                    "Work on data science projects that drive business decisions and "
                    "product improvements. Collaborate with cross-functional teams to "
                    "analyze data, build models, and derive insights. Dedicated mentor "
                    "and intern cohort experience.\n\n"
                    "$60/hr | San Francisco, CA\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/data-science-intern-2026-start-6866538002"
                ),
            },
        ],
    },

    # ── 6. Rippling ──
    {
        "company_name": "Rippling",
        "email": "careers@rippling.com",
        "name": "Parker Conrad",
        "industry": "HR / IT / Finance Platform",
        "company_size": "startup",
        "website": "https://www.rippling.com",
        "slug": "rippling",
        "description": (
            "Rippling is the first workforce platform that lets companies manage all of "
            "their HR, IT, and Finance — payroll, benefits, expenses, corporate cards, "
            "computers, apps, and more — in one unified system. Rippling is hiring 150+ "
            "interns in 2026, more than double last year.\n\n"
            "Fund: Lightspeed | HQ: San Francisco"
        ),
        "founders": [
            {"name": "Parker Conrad", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/parkerconrad"},
            {"name": "Prasanna Sankar", "title": "CTO & Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Full Stack Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 11440,
                "salary_max": 11440,
                "requirements": [
                    "Previous internship/co-op experience in software engineering",
                    "Backend experience with Python and frontend with JavaScript, HTML/CSS",
                    "Currently enrolled in Bachelor's or Master's in CS or related field",
                    "At least 1 semester/quarter remaining after internship",
                ],
                "description": (
                    "Full Stack Software Engineer Intern at Rippling (Summer 2026)\n\n"
                    "Develop robust, well-designed products, implement new features, "
                    "and solve complex problems. End of May through August. Every intern "
                    "is paired with a mentor, managers set clear goals, and projects "
                    "are scoped for full lifecycle from start to finish. Also available "
                    "in New York, NY.\n\n"
                    "$66/hr | San Francisco, CA or New York, NY\n\n"
                    "Source: https://ats.rippling.com/rippling/jobs/2f242b59-eee3-41f5-a5d7-55b7545cb9fb"
                ),
            },
        ],
    },

    # ── 7. Anduril Industries ──
    {
        "company_name": "Anduril Industries",
        "email": "careers@anduril.com",
        "name": "Palmer Luckey",
        "industry": "Defense Technology",
        "company_size": "startup",
        "website": "https://www.anduril.com",
        "slug": "anduril-industries",
        "description": (
            "Anduril Industries is a defense technology company transforming U.S. and "
            "allied military capabilities with advanced technology. The company brings "
            "the expertise, technology, and business model of the 21st century's most "
            "innovative companies to the defense industry.\n\n"
            "Fund: Lightspeed | HQ: Costa Mesa, CA"
        ),
        "founders": [
            {"name": "Palmer Luckey", "title": "Founder", "linkedin": "https://linkedin.com/in/palmerluckey"},
            {"name": "Trae Stephens", "title": "Co-Founder & Executive Chairman", "linkedin": ""},
            {"name": "Brian Schimpf", "title": "Co-Founder & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Costa Mesa, CA",
                "salary_min": 8800,
                "salary_max": 8800,
                "requirements": [
                    "Pursuing Bachelor's or Master's in CS, Software Engineering, Mathematics, Physics, or related field",
                    "Rising senior returning to school after internship for at least one quarter/semester",
                    "Proficiency in C++, Go, Rust, Java, or Python",
                    "Familiarity with algorithms, data structures, and cloud infrastructure",
                    "U.S. Person status required (export controlled data access)",
                ],
                "description": (
                    "Software Engineer Intern at Anduril Industries (Summer 2026)\n\n"
                    "Paid, in-person, 12-week internship working on defense technology "
                    "systems. Multiple locations available: Costa Mesa, CA; Irvine, CA; "
                    "Atlanta, GA; Seattle, WA; Boston, MA; Reston, VA. Work on critical "
                    "national security projects with cutting-edge technology.\n\n"
                    "$51/hr | Multiple US locations\n\n"
                    "Source: https://job-boards.greenhouse.io/andurilindustries/jobs/4807506007"
                ),
            },
        ],
    },

    # ── 8. Abridge ──
    {
        "company_name": "Abridge",
        "email": "careers@abridge.com",
        "name": "Shiv Rao",
        "industry": "Healthcare / AI",
        "company_size": "startup",
        "website": "https://www.abridge.com",
        "slug": "abridge",
        "description": (
            "Abridge is a pioneer in generative AI for healthcare, transforming "
            "patient-clinician conversations into structured clinical notes in real-time "
            "with deep EMR integrations. Deployed across 100+ U.S. health systems, "
            "setting industry standards for responsible AI deployment.\n\n"
            "Fund: Lightspeed | HQ: Pittsburgh / San Francisco"
        ),
        "founders": [
            {"name": "Shiv Rao, MD", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/shivdevrao"},
        ],
        "jobs": [
            {
                "title": "Full Stack Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing Bachelor's or Master's in Computer Science, Software Engineering, or related field",
                    "Experience with TypeScript, React, and Node.js or Next.js",
                    "Prior hands-on experience developing web applications (internship or co-op)",
                    "Interest in healthcare technology and AI applications",
                ],
                "description": (
                    "Full Stack Engineering Intern at Abridge (Summer 2026)\n\n"
                    "Join Abridge's Product Engineering team for a 12-week program. "
                    "Work on AI-powered healthcare products that are transforming how "
                    "clinicians document patient interactions. Abridge covers flights to "
                    "and from SF, and rent/living expenses factored into salary. "
                    "High-performing interns eligible for full-time return offer in 2027.\n\n"
                    "Hybrid (San Francisco office)\n\n"
                    "Source: https://jobs.ashbyhq.com/abridge"
                ),
            },
        ],
    },

    # ── 9. Nominal ──
    {
        "company_name": "Nominal",
        "email": "careers@nominal.io",
        "name": "Cameron McCord",
        "industry": "Hardware Data / Defense Tech",
        "company_size": "startup",
        "website": "https://www.nominal.io",
        "slug": "nominal",
        "description": (
            "Nominal builds the data infrastructure platform for hardware engineering teams, "
            "helping organizations quickly and reliably test and validate critical systems "
            "across aerospace, defense, energy, automotive, and manufacturing. "
            "Backed by Lightspeed, Sequoia, General Catalyst, and Founders Fund.\n\n"
            "Fund: Lightspeed | HQ: Los Angeles / New York"
        ),
        "founders": [
            {"name": "Cameron McCord", "title": "Co-Founder", "linkedin": ""},
            {"name": "Bryce Strauss", "title": "Co-Founder", "linkedin": ""},
            {"name": "Jason Hoch", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8000,
                "salary_max": 9500,
                "requirements": [
                    "Strong engineering fundamentals and interest in data infrastructure",
                    "On track to graduate Summer 2027 or sooner",
                    "Experience with a general-purpose programming language",
                    "Interest in aerospace, defense, or hardware engineering",
                ],
                "description": (
                    "Software Engineer Intern at Nominal (Summer 2026)\n\n"
                    "Work closely with world-class engineers solving high-impact problems "
                    "in hardware data infrastructure. Build software that accelerates the "
                    "development of the world's most advanced hardware systems — from "
                    "spacecraft and autonomous vehicles to next-generation industrial machines.\n\n"
                    "New York, NY or Los Angeles, CA\n\n"
                    "Source: https://jobs.lever.co/nominal"
                ),
            },
        ],
    },

    # ── 10. Epic Games ──
    {
        "company_name": "Epic Games",
        "email": "careers@epicgames.com",
        "name": "Tim Sweeney",
        "industry": "Gaming / Interactive Entertainment",
        "company_size": "enterprise",
        "website": "https://www.epicgames.com",
        "slug": "epic-games",
        "description": (
            "Epic Games is the creator of Fortnite, Unreal Engine, and the Epic Games Store. "
            "The company builds games and the technology that powers them, including Unreal "
            "Engine — the world's most open and advanced real-time 3D creation tool.\n\n"
            "Fund: Lightspeed | HQ: Cary, NC"
        ),
        "founders": [
            {"name": "Tim Sweeney", "title": "CEO & Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Game Services Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "Cary, NC",
                "salary_min": 9000,
                "salary_max": 10500,
                "requirements": [
                    "Currently pursuing a degree in Computer Science, Software Engineering, or related field",
                    "Strong programming skills in C++ or similar languages",
                    "Interest in game development, real-time systems, or 3D technology",
                    "Available for full-time internship during Summer 2026",
                ],
                "description": (
                    "Game Services Engineer Intern at Epic Games (Summer 2026)\n\n"
                    "Join dev teams working on real-world projects that directly contribute "
                    "to game development, tools, or technology. Work on Fortnite, Unreal Engine, "
                    "or Epic Online Services. Interns are assigned to teams based on skills "
                    "and interests, working on meaningful projects from day one.\n\n"
                    "~$55-$66/hr | Cary, NC\n\n"
                    "Source: https://www.epicgames.com/site/en-US/careers/jobs?type=Intern"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # ── Affirm (already in DB) ──
    {
        "company_name": "Affirm",
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 9500,
                "requirements": [
                    "Experience with Python, C/C++, or Java",
                    "Familiarity with frontend development (React, JavaScript)",
                    "Understanding of object-oriented programming",
                    "Interest in deployment and testing frameworks",
                    "Passion for changing consumer banking",
                ],
                "description": (
                    "Software Engineering Intern at Affirm (Summer 2026)\n\n"
                    "As an intern at Affirm, you will be a contributing member of the "
                    "engineering team, developing and shipping a project that verifies "
                    "it works in production. 12-16 week internship with dedicated mentor. "
                    "$55/hr | Hybrid (SF office 3 days/week)\n\n"
                    "Source: https://job-boards.greenhouse.io/affirm/jobs/7528020003"
                ),
            },
        ],
    },
    # ── Glean (already in DB) ──
    {
        "company_name": "Glean",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 9900,
                "salary_max": 12000,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with B.S., M.S. or Ph.D. in Computer Science",
                    "Team player with strong desire to learn and owner mentality",
                    "Comfortable in a fast-paced, data-driven environment",
                    "Prior internship experience in relevant areas preferred",
                ],
                "description": (
                    "Software Engineer Intern at Glean (Summer 2026)\n\n"
                    "Own a scoped, high-impact project end to end. Contribute across the "
                    "stack: backend services, product engineering, ML/AI/search, infrastructure. "
                    "Hybrid (3-4 days/week in Palo Alto or SF office). $57-$69/hr\n\n"
                    "Source: https://job-boards.greenhouse.io/gleanwork/jobs/4595665005"
                ),
            },
        ],
    },
    # ── Databricks (already in DB) ──
    {
        "company_name": "Databricks",
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10400,
                "salary_max": 10400,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with degree in CS, Engineering, or related field",
                    "Implementation skills in Python, Java, or C++",
                    "Good knowledge of algorithms, data structures, and OOP principles",
                    "Excited to solve ambiguous problems with a collaborative team",
                ],
                "description": (
                    "Software Engineering Intern at Databricks (Summer 2026)\n\n"
                    "Join teams including full stack, backend, infrastructure, systems, tools, "
                    "cloud, databases. Options: Winter 16-week co-op, Summer 16-week co-op, "
                    "or Summer 12-week internship. $60/hr\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/software-engineering-intern-2026-6866531002"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Francisco, CA",
                "salary_min": 10400,
                "salary_max": 10400,
                "requirements": [
                    "Graduating Fall 2026 or Spring 2027 with degree in Data Science, Statistics, CS",
                    "Experience with Python, SQL, and data analysis frameworks",
                    "Knowledge of machine learning and statistical methods",
                    "Strong analytical and problem-solving skills",
                ],
                "description": (
                    "Data Science Intern at Databricks (Summer 2026)\n\n"
                    "Work on data science projects that drive business decisions and "
                    "product improvements. $60/hr\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/data-science-intern-2026-start-6866538002"
                ),
            },
        ],
    },
    # ── Anduril Industries (already in DB) ──
    {
        "company_name": "Anduril Industries",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Costa Mesa, CA",
                "salary_min": 8800,
                "salary_max": 8800,
                "requirements": [
                    "Pursuing Bachelor's or Master's in CS, Software Engineering, Mathematics, or Physics",
                    "Rising senior returning to school after internship",
                    "Proficiency in C++, Go, Rust, Java, or Python",
                    "U.S. Person status required",
                ],
                "description": (
                    "Software Engineer Intern at Anduril Industries (Summer 2026)\n\n"
                    "Paid, in-person, 12-week internship. Multiple locations: Costa Mesa, CA; "
                    "Irvine, CA; Atlanta, GA; Seattle, WA; Boston, MA; Reston, VA. $51/hr\n\n"
                    "Source: https://job-boards.greenhouse.io/andurilindustries/jobs/4807506007"
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
