#!/usr/bin/env python3
"""
Seed intern jobs from Lightspeed Venture Partners portfolio companies.

FIRM: Lightspeed Venture Partners (LSVP)
JOB BOARD: https://jobs.lsvp.com
SCRIPT ID: lightspeed

Round 1 - 10 companies, 11 jobs (6 new companies, 4 existing w/ additional jobs):
- Affirm, Snap Inc., Rubrik, Glean, Databricks, Rippling,
- Anduril Industries, Abridge, Nominal, Epic Games

Round 2 - 4 new companies + additional jobs for 4 existing companies:
- NEW: Nutanix, Guardant Health, CertiK, Kodiak Robotics
- ADDITIONAL JOBS: Neuralink, Stripe, Verkada, Whatnot
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
            {"name": "Ion Stoica", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/ionstoica"},
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
            {"name": "Palmer Luckey", "title": "Founder", "linkedin": "https://linkedin.com/in/palmer-luckey-a5a75943"},
            {"name": "Trae Stephens", "title": "Co-Founder & Executive Chairman", "linkedin": ""},
            {"name": "Brian Schimpf", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/brian-schimpf"},
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
            {"name": "Cameron McCord", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/cameronmccord"},
            {"name": "Bryce Strauss", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/brycestrauss"},
            {"name": "Jason Hoch", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/jasonhoch"},
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
            {"name": "Tim Sweeney", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/timsweeney"},
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

    # ── 11. Nutanix ──
    {
        "company_name": "Nutanix",
        "email": "careers@nutanix.com",
        "name": "Rajiv Ramaswami",
        "industry": "Cloud Computing / Infrastructure",
        "company_size": "enterprise",
        "website": "https://www.nutanix.com",
        "slug": "nutanix",
        "description": (
            "Nutanix pioneered hyperconverged infrastructure, providing a unified cloud "
            "platform for private, public, and hybrid cloud operations. The Nutanix Cloud "
            "Platform simplifies enterprise computing across datacenters worldwide.\n\n"
            "Fund: Lightspeed | HQ: San Jose, CA"
        ),
        "founders": [
            {"name": "Dheeraj Pandey", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/dheerajpandey"},
            {"name": "Mohit Aron", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/mohitaron"},
            {"name": "Ajeet Singh", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/ajeetsingh1"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Jose, CA",
                "salary_min": 8667,
                "salary_max": 8667,
                "requirements": [
                    "Currently pursuing Bachelor's degree in Computer Science or related field",
                    "No professional experience required; prior internships acceptable",
                    "Must be authorized to work in US without visa sponsorship",
                    "Minimum 3 days/week in office",
                ],
                "description": (
                    "Software Engineering Intern at Nutanix (Summer 2026)\n\n"
                    "12-week paid internship starting May or June 2026. Join one of many "
                    "R&D teams including Nutanix Database, AI Organization, Cloud Clusters, "
                    "Flow, and Disaster Recovery & Backup. Also available in Durham, NC.\n\n"
                    "$50/hr | San Jose, CA or Durham, NC\n\n"
                    "Source: https://careers.nutanix.com/en/jobs/30256/software-engineering-intern-undergrad-please-only-apply/"
                ),
            },
        ],
    },

    # ── 12. Guardant Health ──
    {
        "company_name": "Guardant Health",
        "email": "careers@guardanthealth.com",
        "name": "Helmy Eltoukhy",
        "industry": "Biotechnology / Genomics / Healthcare",
        "company_size": "enterprise",
        "website": "https://guardanthealth.com",
        "slug": "guardant-health",
        "description": (
            "Guardant Health is a precision oncology company using liquid biopsy blood "
            "tests to detect cancer from genetic mutations. The company provides genomics-based "
            "cancer detection and treatment solutions for healthcare providers worldwide.\n\n"
            "Fund: Lightspeed | HQ: Palo Alto, CA"
        ),
        "founders": [
            {"name": "Helmy Eltoukhy", "title": "Co-CEO & Co-Founder", "linkedin": "https://linkedin.com/in/helmy-eltoukhy-8a48604"},
            {"name": "AmirAli Talasaz", "title": "Co-CEO & Co-Founder", "linkedin": "https://linkedin.com/in/amirali-talasaz-4476652"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern - LIMS (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 5000,
                "salary_max": 7280,
                "requirements": [
                    "Pursuing Bachelor's in Computer Science, Software Engineering, or related field",
                    "Exposure to OOP languages (Java, JavaScript, C#)",
                    "Exposure to UI frameworks (React, AngularJS)",
                    "Interest in healthcare technology and genomics",
                ],
                "description": (
                    "Software Engineer Intern (LIMS) at Guardant Health (Summer 2026)\n\n"
                    "Work on laboratory information management systems for cancer genomics. "
                    "Hybrid work model (onsite Mon/Tue/Thu). Compensation varies by level: "
                    "undergrad $29/hr, graduate $34/hr, doctorate $42/hr.\n\n"
                    "$29-$42/hr | Palo Alto, CA\n\n"
                    "Source: https://startup.jobs/summer-intern-software-engineer-guardant-health-5304427"
                ),
            },
        ],
    },

    # ── 13. CertiK ──
    {
        "company_name": "CertiK",
        "email": "careers@certik.com",
        "name": "Ronghui Gu",
        "industry": "Blockchain Security / Cybersecurity",
        "company_size": "startup",
        "website": "https://www.certik.com",
        "slug": "certik",
        "description": (
            "CertiK is the world's largest Web3 security services provider, using formal "
            "verification technology to protect blockchain protocols and smart contracts. "
            "The company has secured over $530 billion in digital assets and detected "
            "180,000+ vulnerabilities.\n\n"
            "Fund: Lightspeed | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Ronghui Gu", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/ronghuigu"},
        ],
        "jobs": [
            {
                "title": "Security Research Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 5000,
                "salary_max": 8000,
                "requirements": [
                    "Pursuing Masters or PhD in Computer Science or Cybersecurity",
                    "Knowledge of malware analysis, vulnerability detection, or reverse engineering",
                    "CTF experience and WASM/Rust/Go development skills valued",
                    "Interest in blockchain security and Web3",
                ],
                "description": (
                    "Security Research Intern at CertiK (Summer 2026)\n\n"
                    "Focus on malware analysis, vulnerability detection, network anomaly "
                    "detection, mobile app analysis, reverse engineering, and fraud detection "
                    "in the Web3 space. Also available in SF Bay Area and Seattle.\n\n"
                    "$3,000-$8,000/mo | NYC, SF, or Seattle\n\n"
                    "Source: https://jobs.lever.co/certik/148afcf8-106b-42fa-a516-6bb8f1184e33"
                ),
            },
        ],
    },

    # ── 14. Kodiak Robotics ──
    {
        "company_name": "Kodiak Robotics",
        "email": "careers@kodiak.ai",
        "name": "Don Burnette",
        "industry": "Autonomous Vehicles / Robotics",
        "company_size": "startup",
        "website": "https://kodiak.ai",
        "slug": "kodiak-robotics",
        "description": (
            "Kodiak Robotics is a leader in autonomous ground transportation, developing "
            "self-driving technology for long-haul trucking, industrial/off-road operations, "
            "and military defense applications. The company has achieved driverless "
            "semi-truck deliveries to customers.\n\n"
            "Fund: Lightspeed | HQ: Mountain View, CA"
        ),
        "founders": [
            {"name": "Don Burnette", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/donburnette"},
        ],
        "jobs": [
            {
                "title": "AI/Machine Learning Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 7100,
                "salary_max": 7100,
                "requirements": [
                    "Strong background in machine learning and computer vision",
                    "Experience with Python, PyTorch, or TensorFlow",
                    "Interest in autonomous vehicles and robotics",
                    "Available for 12-16 week program starting June 2026",
                ],
                "description": (
                    "AI/Machine Learning Intern at Kodiak Robotics (Summer 2026)\n\n"
                    "Work on perception, prediction, and planning systems for autonomous "
                    "trucks. 12-16 week program starting June 2026. Free catered lunch, "
                    "dog-friendly office in Mountain View.\n\n"
                    "~$41/hr | Mountain View, CA\n\n"
                    "Source: https://job-boards.greenhouse.io/kodiak/jobs/4024627009"
                ),
            },
            {
                "title": "Simulation Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 7100,
                "salary_max": 10000,
                "requirements": [
                    "Experience with simulation frameworks and 3D environments",
                    "Strong programming skills in C++ or Python",
                    "Interest in autonomous driving simulation",
                    "Background in physics, math, or robotics",
                ],
                "description": (
                    "Simulation Engineer Intern at Kodiak Robotics (Summer 2026)\n\n"
                    "Build and improve simulation environments for testing autonomous "
                    "driving systems. Work across Systems Engineering, Perception, "
                    "Hardware, and Motion Planning & Controls.\n\n"
                    "Mountain View, CA\n\n"
                    "Source: https://job-boards.greenhouse.io/kodiak/jobs/4024796009"
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
    # ── Neuralink (already in DB) ──
    {
        "company_name": "Neuralink",
        "jobs": [
            {
                "title": "Software Engineer Intern - Robotics (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Fremont, CA",
                "salary_min": 6067,
                "salary_max": 6067,
                "requirements": [
                    "Pursuing degree in Computer Science, Robotics, or related field",
                    "Experience with Python, C++, or similar languages",
                    "Interest in robotics and brain-computer interfaces",
                    "Available for 12-week internship Summer 2026",
                ],
                "description": (
                    "Software Engineer Intern (Robotics) at Neuralink (Summer 2026)\n\n"
                    "Work on software for Neuralink's robotic surgical systems that implant "
                    "brain-computer interfaces. Contribute to real-time control systems, "
                    "computer vision, and surgical automation.\n\n"
                    "$35/hr | Fremont, CA\n\n"
                    "Source: https://boards.greenhouse.io/neuralink"
                ),
            },
            {
                "title": "Software Engineer Intern - BCI Applications (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 6067,
                "salary_max": 6067,
                "requirements": [
                    "Pursuing degree in Computer Science, Neuroscience, or related field",
                    "Strong programming skills in Python or C++",
                    "Interest in neurotechnology and signal processing",
                    "Available for 12-week internship Summer 2026",
                ],
                "description": (
                    "Software Engineer Intern (BCI Applications) at Neuralink (Summer 2026)\n\n"
                    "Work on brain-computer interface applications, signal processing, "
                    "and user-facing software for Neuralink's neural implant platform.\n\n"
                    "$35/hr | Austin, TX\n\n"
                    "Source: https://boards.greenhouse.io/neuralink"
                ),
            },
        ],
    },
    # ── Stripe (already in DB) ──
    {
        "company_name": "Stripe",
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10833,
                "salary_max": 10833,
                "requirements": [
                    "Currently enrolled in a degree program in CS, Engineering, or related field",
                    "Strong coding skills in at least one programming language",
                    "Ability to learn and apply new technologies quickly",
                    "Graduating in Winter 2026 or Spring/Summer 2027",
                ],
                "description": (
                    "Software Engineering Intern at Stripe (Summer 2026)\n\n"
                    "Build the economic infrastructure for the internet. Work on payments, "
                    "billing, fraud prevention, or developer tools. 12-week internship with "
                    "1:1 mentor and real impact projects. Also available in Seattle, WA "
                    "and New York, NY.\n\n"
                    "~$62.50/hr | SF, Seattle, or NYC\n\n"
                    "Source: https://stripe.com/jobs/listing/software-engineering-intern"
                ),
            },
        ],
    },
    # ── Verkada (already in DB) ──
    {
        "company_name": "Verkada",
        "jobs": [
            {
                "title": "Backend Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 11267,
                "salary_max": 11267,
                "requirements": [
                    "Pursuing Bachelor's or Master's in Computer Science or related field",
                    "Experience with backend development and APIs",
                    "Proficiency in Go, Python, or Java",
                    "Available for 12-week summer internship",
                ],
                "description": (
                    "Backend Software Engineering Intern at Verkada (Summer 2026)\n\n"
                    "Build backend systems for Verkada's cloud-managed security platform. "
                    "Work on scalable APIs, data pipelines, and cloud infrastructure.\n\n"
                    "$65/hr | San Mateo, CA\n\n"
                    "Source: https://jobs.lever.co/verkada"
                ),
            },
            {
                "title": "Frontend Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 11267,
                "salary_max": 11267,
                "requirements": [
                    "Pursuing Bachelor's or Master's in Computer Science or related field",
                    "Experience with React, TypeScript, or modern frontend frameworks",
                    "Strong UI/UX sensibility",
                    "Available for 12-week summer internship",
                ],
                "description": (
                    "Frontend Software Engineering Intern at Verkada (Summer 2026)\n\n"
                    "Build user interfaces for Verkada's cloud-managed building security "
                    "platform. Work on React-based dashboards, real-time video interfaces, "
                    "and device management tools.\n\n"
                    "$65/hr | San Mateo, CA\n\n"
                    "Source: https://jobs.lever.co/verkada"
                ),
            },
            {
                "title": "Mobile Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 11267,
                "salary_max": 11267,
                "requirements": [
                    "Pursuing Bachelor's or Master's in Computer Science or related field",
                    "Experience with iOS (Swift) or Android (Kotlin) development",
                    "Understanding of mobile app architecture patterns",
                    "Available for 12-week summer internship",
                ],
                "description": (
                    "Mobile Software Engineering Intern at Verkada (Summer 2026)\n\n"
                    "Build mobile applications for Verkada's security platform. Work on "
                    "real-time video streaming, push notifications, and device control "
                    "features for iOS and Android.\n\n"
                    "$65/hr | San Mateo, CA\n\n"
                    "Source: https://jobs.lever.co/verkada"
                ),
            },
        ],
    },
    # ── Whatnot (already in DB) ──
    {
        "company_name": "Whatnot",
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Los Angeles, CA",
                "salary_min": 10000,
                "salary_max": 11267,
                "requirements": [
                    "Currently pursuing a degree in Computer Science or related field",
                    "Strong programming skills and ability to learn quickly",
                    "Interest in live commerce and marketplace platforms",
                    "Available for 12-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Whatnot (Summer 2026)\n\n"
                    "Work on the largest livestream shopping platform in the US. Build "
                    "features for real-time bidding, live video, and marketplace tools. "
                    "Also available in NYC, SF, and Seattle.\n\n"
                    "$57.69-$65/hr | LA, NYC, SF, or Seattle\n\n"
                    "Source: https://job-boards.greenhouse.io/whatnot"
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
