#!/usr/bin/env python3
"""
Seed intern jobs from Dragoneer Investment Group portfolio companies.

Dragoneer is a growth-oriented investment firm with $23B+ AUM, founded by Marc Stad.
Portfolio includes Databricks, Discord, Chime, Roblox, DoorDash, Samsara, Snowflake,
UiPath, Procore, Gusto, Strava, Wealthfront, AppFolio, Instacart, ServiceTitan, Tekion.

SCRIPT ID: dragoneer
RUN: cd apps/api && python -m scripts.seed_dragoneer_jobs
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
FIRM_NAME = "Dragoneer Investment Group"
SCRIPT_ID = "dragoneer"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── Databricks & DoorDash already exist in DB — see ADDITIONAL_JOBS below ──
    # ── 1. Discord ──
    {
        "company_name": "Discord",
        "email": "careers@discord.com",
        "name": "Jason Citron",
        "industry": "Social / Communication",
        "company_size": "startup",
        "website": "https://discord.com",
        "slug": "discord",
        "description": (
            "Discord is a communication platform where people create communities around shared "
            "interests — from gaming to education to just hanging out. Over 200 million monthly "
            "active users connect through voice, video, and text.\n\n"
            "Fund: Dragoneer | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Jason Citron", "title": "Co-founder", "linkedin": "https://linkedin.com/in/jasoncitron"},
            {"name": "Stanislav Vishnevskiy", "title": "CTO & Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 10900,
                "requirements": [
                    "Currently enrolled in a Bachelor's program as a rising Junior or Senior",
                    "Proficient in at least one of: Rust, JavaScript/TypeScript, Python, or C/C++",
                    "Strong understanding of algorithms and data structures",
                    "Experience building applications or contributing to open source",
                ],
                "description": (
                    "Software Engineer Intern at Discord — Summer 2026\n\n"
                    "Work on real projects that ship to millions of users. Teams include "
                    "Native Framework & Tools, Data Products, and core platform engineering. "
                    "Remote-friendly within the US. Compensation: ~$63/hr.\n\n"
                    "Source: https://discord.com/careers"
                ),
            },
        ],
    },
    # ── 3. Chime ──
    {
        "company_name": "Chime",
        "email": "careers@chime.com",
        "name": "Chris Britt",
        "industry": "Fintech / Banking",
        "company_size": "startup",
        "website": "https://www.chime.com",
        "slug": "chime",
        "description": (
            "Chime is a financial technology company providing fee-free mobile banking services "
            "to millions of Americans. Went public on Nasdaq in 2025 at an $11.6B valuation. "
            "Products include checking, savings, credit building, and instant transfers.\n\n"
            "Fund: Dragoneer | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Chris Britt", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/cbritt"},
            {"name": "Ryan King", "title": "CTO & Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7500,
                "salary_max": 8500,
                "requirements": [
                    "Pursuing a BS or MS in Computer Science or related field",
                    "Strong programming skills in Python, Java, or similar",
                    "Interest in fintech, payments, or consumer banking",
                    "Available for a 12-week summer internship (June-August)",
                ],
                "description": (
                    "Software Engineer Intern at Chime — Summer 2026\n\n"
                    "Join one of Chime's engineering teams (Spend & Credit, SpotMe, FinPlat, "
                    "Cash & Checks) building products that serve millions. 12-week program with "
                    "mentorship and real project ownership. Compensation: ~$45-49/hr + housing stipend.\n\n"
                    "Source: https://careers.chime.com/en/early-talent/"
                ),
            },
        ],
    },
    # ── 4. Roblox ──
    {
        "company_name": "Roblox",
        "email": "careers@roblox.com",
        "name": "David Baszucki",
        "industry": "Gaming / Metaverse",
        "company_size": "startup",
        "website": "https://www.roblox.com",
        "slug": "roblox",
        "description": (
            "Roblox is a global platform where millions of people create, share, and "
            "experience 3D content together. Over 70 million daily active users across "
            "distributed systems, real-time communication, and immersive co-experiences.\n\n"
            "Fund: Dragoneer | HQ: San Mateo, CA"
        ),
        "founders": [
            {"name": "David Baszucki", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/davidbaszucki"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 10000,
                "salary_max": 10700,
                "requirements": [
                    "Pursuing an undergraduate or graduate degree in CS, Engineering, or related field",
                    "Proficient in one or more of: Go, Node.js, Ruby, Python, C++, Lua, Swift, C#, or Java",
                    "Strong problem-solving skills in distributed systems, real-time communication, or 3D",
                    "Available for a 12-week summer internship",
                ],
                "description": (
                    "Software Engineer Intern at Roblox — Summer 2026\n\n"
                    "Tackle problems in distributed systems, real-time communication, 3D co-experience, "
                    "extensive data processing, social networking, rendering, and physics. Join a "
                    "supportive team with mentorship from top-tier engineers. Compensation: ~$62/hr.\n\n"
                    "Source: https://careers.roblox.com/jobs/7114765"
                ),
            },
        ],
    },
    # ── DoorDash already exists in DB — see ADDITIONAL_JOBS below ──
    # ── 5. Samsara ──
    {
        "company_name": "Samsara",
        "email": "careers@samsara.com",
        "name": "Sanjit Biswas",
        "industry": "IoT / Operations",
        "company_size": "startup",
        "website": "https://www.samsara.com",
        "slug": "samsara",
        "description": (
            "Samsara is the pioneer of the Connected Operations Cloud, helping organizations "
            "that rely on physical operations harness IoT data to develop actionable insights "
            "and improve operations. Founded by the team behind Meraki (acquired by Cisco for $1.2B).\n\n"
            "Fund: Dragoneer | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Sanjit Biswas", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/sanjitbiswas"},
            {"name": "John Bicket", "title": "CTO & Co-founder", "linkedin": "https://linkedin.com/in/jbicket"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 9000,
                "requirements": [
                    "Completing a Bachelor's in CS, Mathematics, Software Engineering, Physics, or Data Science (graduating Spring/Summer/Fall 2027)",
                    "Proficiency in Backend, Infrastructure, Fullstack, Frontend, or Mobile engineering",
                    "Ability to work in a hybrid model (3 days/week in SF office)",
                    "Available for a 12-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Samsara — Summer 2026\n\n"
                    "Dive into challenging, real-world IoT projects with the same freedom and "
                    "responsibility as full-time engineers. Shape the future of industrial IoT "
                    "across fleet management, industrial automation, and connected operations.\n\n"
                    "Source: https://www.samsara.com/company/careers/emerging-talent"
                ),
            },
        ],
    },
    # ── 7. Snowflake ──
    {
        "company_name": "Snowflake",
        "email": "careers@snowflake.com",
        "name": "Sridhar Ramaswamy",
        "industry": "Data Cloud / Infrastructure",
        "company_size": "startup",
        "website": "https://www.snowflake.com",
        "slug": "snowflake",
        "description": (
            "Snowflake delivers the Data Cloud — a global network powering data warehousing, "
            "data lakes, data engineering, data science, and data sharing. Enables near-unlimited "
            "scale, concurrency, and performance across multiple clouds.\n\n"
            "Fund: Dragoneer | HQ: Bozeman, MT"
        ),
        "founders": [
            {"name": "Benoit Dageville", "title": "Co-founder", "linkedin": "https://linkedin.com/in/benoit-dageville-3011845"},
            {"name": "Thierry Cruanes", "title": "Co-founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Mateo, CA",
                "salary_min": 9000,
                "salary_max": 10400,
                "requirements": [
                    "3rd/4th year Undergraduate, Master's, or PhD in CS, Computer Engineering, EE, Physics, or Math",
                    "Strong programming skills in C++, Java, Python, or Go",
                    "Understanding of distributed systems, databases, or cloud infrastructure",
                    "Available for a minimum 12-week internship (16 weeks recommended)",
                ],
                "description": (
                    "Software Engineer Intern at Snowflake — Summer 2026\n\n"
                    "Work on core engineering, cloud infrastructure, or platform teams building "
                    "the Data Cloud. Competitive benefits package including medical, dental, vision. "
                    "Compensation: $42-60/hr depending on level and location.\n\n"
                    "Source: https://careers.snowflake.com/us/en/university"
                ),
            },
        ],
    },
    # ── 8. UiPath ──
    {
        "company_name": "UiPath",
        "email": "careers@uipath.com",
        "name": "Daniel Dines",
        "industry": "Automation / AI",
        "company_size": "startup",
        "website": "https://www.uipath.com",
        "slug": "uipath",
        "description": (
            "UiPath is the leading enterprise automation and AI platform. Their robotic "
            "process automation (RPA) technology helps organizations automate repetitive "
            "tasks, freeing people for higher-value work. Public on NYSE.\n\n"
            "Fund: Dragoneer | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Daniel Dines", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/danieldines"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 8500,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a Bachelor's, Master's, or PhD in CS, Math, or related discipline",
                    "Programming proficiency in C#, C/C++, Java, Python, JavaScript, or TypeScript",
                    "Python and TypeScript proficiency preferred",
                    "Experience from previous internships or open-source contributions",
                ],
                "description": (
                    "Software Engineer Intern at UiPath — Summer 2026\n\n"
                    "Join UiPath's Future Forward Internship Program. Work on enterprise "
                    "automation and agentic AI products used by Fortune 500 companies. "
                    "3-month full-time paid internship with path to full-time. Compensation: ~$52/hr.\n\n"
                    "Source: https://jobs.ashbyhq.com/uipath"
                ),
            },
        ],
    },
    # ── 9. Procore ──
    {
        "company_name": "Procore",
        "email": "careers@procore.com",
        "name": "Tooey Courtemanche",
        "industry": "Construction Tech / SaaS",
        "company_size": "startup",
        "website": "https://www.procore.com",
        "slug": "procore",
        "description": (
            "Procore is the leading cloud-based construction management platform. Connects "
            "every project stakeholder to solutions built specifically for the construction "
            "industry — project management, quality & safety, and financials.\n\n"
            "Fund: Dragoneer | HQ: Carpinteria, CA"
        ),
        "founders": [
            {"name": "Tooey Courtemanche", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/tooey"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 4500,
                "salary_max": 7500,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Experience with web development technologies",
                    "Strong problem-solving and communication skills",
                    "Available for a 12-week paid summer internship at Austin, TX office",
                ],
                "description": (
                    "Software Engineer Intern at Procore — Summer 2026\n\n"
                    "Join the Product & Technology team working on real construction management "
                    "projects. You'll have a dedicated mentor and present an innovative concept "
                    "at the end of the internship. Compensation: $25-45/hr.\n\n"
                    "Source: https://careers.procore.com/early-careers"
                ),
            },
            {
                "title": "Product Design Intern (Summer 2026)",
                "vertical": Vertical.DESIGN,
                "role_type": RoleType.PRODUCT_DESIGNER,
                "location": "Austin, TX",
                "salary_min": 4300,
                "salary_max": 5700,
                "requirements": [
                    "Pursuing a degree in Design, HCI, or related field",
                    "Portfolio demonstrating UX/UI design skills",
                    "Experience with Figma or similar design tools",
                    "Available for a 12-week paid summer internship",
                ],
                "description": (
                    "Product Design Intern at Procore — Summer 2026\n\n"
                    "Design user experiences for the construction industry's leading platform. "
                    "Work with cross-functional teams on real projects impacting how buildings "
                    "get built. Compensation: $25-33/hr + equity.\n\n"
                    "Source: https://careers.procore.com/early-careers"
                ),
            },
        ],
    },
    # ── 10. Gusto ──
    {
        "company_name": "Gusto",
        "email": "careers@gusto.com",
        "name": "Josh Reeves",
        "industry": "HR / Payroll SaaS",
        "company_size": "startup",
        "website": "https://gusto.com",
        "slug": "gusto",
        "description": (
            "Gusto is an all-in-one people platform for payroll, benefits, hiring, and "
            "HR management, serving over 300,000 small businesses. Valued at $9.6B. "
            "On a mission to create a world where work empowers a better life.\n\n"
            "Fund: Dragoneer | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Josh Reeves", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/joshuareeves"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 11100,
                "requirements": [
                    "Pursuing a BS or MS in Computer Science, Software Engineering, or related field (graduating Dec 2026 - Jun 2029)",
                    "U.S. work authorization required (no sponsorship)",
                    "Ability to work hybrid (at least twice a week in SF, NYC, or Denver office)",
                    "Available for a 12 or 16-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Gusto — Summer 2026\n\n"
                    "Paired with a dedicated mentor and team manager, make immediate contributions "
                    "to the team's roadmap. Work on payroll, benefits, or HR products that serve "
                    "300,000+ businesses. Relocation assistance provided. Compensation: $58-64/hr.\n\n"
                    "Source: https://job-boards.greenhouse.io/gusto/jobs/7238671"
                ),
            },
        ],
    },
    # ── 11. Strava ──
    {
        "company_name": "Strava",
        "email": "careers@strava.com",
        "name": "Michael Martin",
        "industry": "Fitness / Social",
        "company_size": "startup",
        "website": "https://www.strava.com",
        "slug": "strava",
        "description": (
            "Strava is the leading digital community for active people with 120M+ users. "
            "Athletes track activities, connect with others, and find motivation through "
            "social features, challenges, and detailed performance analytics.\n\n"
            "Fund: Dragoneer | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Michael Horvath", "title": "Co-founder", "linkedin": "https://linkedin.com/in/mtkhorvath"},
            {"name": "Mark Gainey", "title": "Co-founder & Chairman", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern, Web (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6500,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing a CS degree with graduation date May 2026 or later",
                    "Proficiency with React and modern web technologies",
                    "Strong JavaScript/TypeScript skills",
                    "Available for a 10-12 week remote summer internship",
                ],
                "description": (
                    "Software Engineering Intern (Web) at Strava — Summer 2026\n\n"
                    "Embedded in an engineering team working on real features that ship to "
                    "120M+ athletes. Treated like a full-time member of the team. "
                    "10-12 week remote internship. Compensation: ~$40/hr + housing stipend.\n\n"
                    "Source: https://www.strava.com/careers"
                ),
            },
            {
                "title": "Software Engineering Intern, Server (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6500,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing a CS degree with graduation date May 2026 or later",
                    "Proficiency in backend languages (Ruby, Python, Java, or Go)",
                    "Understanding of APIs, databases, and distributed systems",
                    "Available for a 10-12 week remote summer internship",
                ],
                "description": (
                    "Software Engineering Intern (Server) at Strava — Summer 2026\n\n"
                    "Work on backend systems powering activity tracking, social features, and "
                    "analytics for millions of athletes worldwide. 10-12 week remote internship "
                    "with mentorship and real project ownership. Compensation: ~$40/hr.\n\n"
                    "Source: https://www.strava.com/careers"
                ),
            },
        ],
    },
    # ── 12. Wealthfront ──
    {
        "company_name": "Wealthfront",
        "email": "careers@wealthfront.com",
        "name": "David Fortunato",
        "industry": "Fintech / Wealth Management",
        "company_size": "startup",
        "website": "https://www.wealthfront.com",
        "slug": "wealthfront",
        "description": (
            "Wealthfront is the leading automated investment service with $70B+ in assets "
            "under management. Offers automated investing, financial planning, banking, and "
            "borrowing — all through a simple, beautifully designed app.\n\n"
            "Fund: Dragoneer | HQ: Palo Alto, CA"
        ),
        "founders": [
            {"name": "Andy Rachleff", "title": "Co-founder & Executive Chairman", "linkedin": "https://linkedin.com/in/rachleff"},
            {"name": "Dan Carroll", "title": "Co-founder & Chief Strategy Officer", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 7500,
                "salary_max": 7900,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Strong programming skills and interest in fintech",
                    "Motivated to ship production code during the internship",
                    "Available for a 12-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Wealthfront — Summer 2026\n\n"
                    "Onboard onto the tech stack, work on small features to start, then design "
                    "and implement a solution to a real business problem under mentor guidance. "
                    "Ship to production and present results at all-hands. Compensation: ~$45.50/hr.\n\n"
                    "Source: https://www.wealthfront.com/careers"
                ),
            },
        ],
    },
    # ── 13. AppFolio ──
    {
        "company_name": "AppFolio",
        "email": "careers@appfolio.com",
        "name": "Shane Trigg",
        "industry": "Property Management / SaaS",
        "company_size": "startup",
        "website": "https://www.appfolio.com",
        "slug": "appfolio",
        "description": (
            "AppFolio provides cloud-based property management software for residential and "
            "commercial real estate. Serves thousands of property managers across the US "
            "with tools for leasing, accounting, maintenance, and communications.\n\n"
            "Fund: Dragoneer | HQ: Santa Barbara, CA"
        ),
        "founders": [
            {"name": "Klaus Schauser", "title": "Co-founder & Chief Strategist", "linkedin": "https://linkedin.com/in/klausschauser"},
            {"name": "Jon Walker", "title": "Co-founder", "linkedin": "https://linkedin.com/in/jonwalker1"},
        ],
        "jobs": [
            {
                "title": "Full Stack Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Santa Barbara, CA",
                "salary_min": 7000,
                "salary_max": 8300,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Experience with Ruby, Java, Python, JavaScript, or similar languages",
                    "Interest in SaaS and property technology",
                    "Available for a summer internship at Santa Barbara or San Diego office",
                ],
                "description": (
                    "Full Stack Software Engineering Intern at AppFolio — Summer 2026\n\n"
                    "Work on real, impactful projects developing new features for property "
                    "management SaaS. Integrated into cross-functional agile teams with "
                    "mentorship and ownership of tasks. Compensation: $40-48/hr.\n\n"
                    "Source: https://www.appfolio.com/company/careers"
                ),
            },
        ],
    },
    # ── 14. Instacart ──
    {
        "company_name": "Instacart",
        "email": "careers@instacart.com",
        "name": "Apoorva Mehta",
        "industry": "Delivery / E-commerce",
        "company_size": "startup",
        "website": "https://www.instacart.com",
        "slug": "instacart",
        "description": (
            "Instacart is the leading grocery technology company in North America, partnering "
            "with more than 1,500 national, regional, and local retail banners to deliver from "
            "more than 85,000 stores. IPO'd on Nasdaq in 2023.\n\n"
            "Fund: Dragoneer | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Apoorva Mehta", "title": "Founder", "linkedin": "https://linkedin.com/in/apoorvamehta"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 9500,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Strong programming skills and interest in e-commerce/logistics",
                    "Experience with at least one backend or frontend technology stack",
                    "Available for a 12-week summer internship (June-August)",
                ],
                "description": (
                    "Software Engineering Intern at Instacart — Summer 2026\n\n"
                    "Work on real engineering projects in one of the world's largest grocery "
                    "technology platforms. Teams span marketplace, logistics, ads, ML, and "
                    "infrastructure. SF housing provided. Highly competitive (<5% acceptance rate).\n\n"
                    "Source: https://instacart.careers/current-openings/"
                ),
            },
        ],
    },
    # ── 15. ServiceTitan ──
    {
        "company_name": "ServiceTitan",
        "email": "careers@servicetitan.com",
        "name": "Ara Mahdessian",
        "industry": "Field Service / SaaS",
        "company_size": "startup",
        "website": "https://www.servicetitan.com",
        "slug": "servicetitan",
        "description": (
            "ServiceTitan is the world's leading software for residential and commercial "
            "field service businesses (HVAC, plumbing, electrical). IPO'd on Nasdaq in 2024. "
            "Founded by children of immigrant tradesmen who saw the need for better tools.\n\n"
            "Fund: Dragoneer | HQ: Glendale, CA"
        ),
        "founders": [
            {"name": "Ara Mahdessian", "title": "CEO & Co-founder", "linkedin": "https://linkedin.com/in/ara-mahdessian-1116232"},
            {"name": "Vahe Kuzoyan", "title": "President & Co-founder", "linkedin": "https://linkedin.com/in/vahe-kuzoyan-34327221"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Glendale, CA",
                "salary_min": 7000,
                "salary_max": 8700,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Strong programming skills in modern languages",
                    "Interest in SaaS and field service technology",
                    "Available for a summer internship",
                ],
                "description": (
                    "Software Engineer Intern at ServiceTitan — Summer 2026\n\n"
                    "Build software that powers millions of service businesses. Work on the "
                    "leading cloud-based platform for the trades — scheduling, dispatching, "
                    "invoicing, and marketing tools used by tens of thousands of companies.\n\n"
                    "Source: https://www.servicetitan.com/job-openings"
                ),
            },
        ],
    },
    # ── 16. Tekion ──
    {
        "company_name": "Tekion",
        "email": "careers@tekion.com",
        "name": "Jay Vijayan",
        "industry": "Automotive Tech / SaaS",
        "company_size": "startup",
        "website": "https://tekion.com",
        "slug": "tekion",
        "description": (
            "Tekion is a cloud-native automotive retail platform with AI and ML capabilities. "
            "Founded by Tesla's former CIO, Tekion is transforming how cars are sold and "
            "serviced. Valued at $4B+ after $200M from Dragoneer in 2024.\n\n"
            "Fund: Dragoneer | HQ: Pleasanton, CA"
        ),
        "founders": [
            {"name": "Jay Vijayan", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/jayvijayan"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Pleasanton, CA",
                "salary_min": 7000,
                "salary_max": 8700,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, or related field",
                    "Strong programming skills in Java, Python, or JavaScript",
                    "Interest in automotive technology and enterprise SaaS",
                    "Available for a summer internship",
                ],
                "description": (
                    "Software Engineer Intern at Tekion — Summer 2026\n\n"
                    "Work on a cloud-native platform built from scratch using modern architecture "
                    "and machine learning. Founded by Tesla's former CIO with a vision to digitize "
                    "the automotive retail industry. Fast-growing $4B+ company.\n\n"
                    "Source: https://tekion.com/job-openings/united-states/all"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # ── Databricks (already in DB) ──
    {
        "company_name": "Databricks",
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 10400,
                "requirements": [
                    "Graduating between Fall 2026 and Summer 2027 with a degree in CS, Engineering, or related field",
                    "Implementation skills in Python, Java, or C++ with strong algorithms and data structures",
                    "Good knowledge of OOP principles",
                    "Available for a 12-week summer internship or 16-week co-op",
                ],
                "description": (
                    "Software Engineering Intern at Databricks — Summer 2026\n\n"
                    "Join one of Databricks' engineering teams (full stack, backend, infrastructure, "
                    "systems, tools, cloud, databases, or customer-facing products). Dedicated mentor "
                    "and 2026 intern cohort. Compensation: ~$60/hr.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 10400,
                "requirements": [
                    "Graduating between Fall 2026 and Summer 2027 with a degree in Data Science, Statistics, CS, or related",
                    "Strong programming skills in Python and SQL",
                    "Experience with statistical analysis, ML, or data engineering",
                    "Available for a 12-week summer internship",
                ],
                "description": (
                    "Data Science Intern at Databricks — Summer 2026\n\n"
                    "Work on data-driven problems at the intersection of AI and data infrastructure. "
                    "Analyze large-scale datasets, build ML models, and contribute to products "
                    "used by thousands of organizations worldwide.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting"
                ),
            },
            {
                "title": "Product Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 9700,
                "requirements": [
                    "Graduating between Fall 2026 and Summer 2027 with a degree in CS, Business, or related field",
                    "Strong analytical and communication skills",
                    "Interest in data, AI, and developer tools",
                    "Available for a 12-week summer internship in SF, Mountain View, or Bellevue",
                ],
                "description": (
                    "Product Management Intern at Databricks — Summer 2026\n\n"
                    "Work across teams including Machine Learning, Unity Catalog, Databricks SQL, "
                    "ETL, Streaming, EDA, and Content Organization. Compensation: $54-56/hr (SF).\n\n"
                    "Source: https://www.databricks.com/company/careers/product/product-management-intern-summer-2026-6883068002"
                ),
            },
        ],
    },
    # ── DoorDash (already in DB) ──
    {
        "company_name": "DoorDash",
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 10400,
                "requirements": [
                    "Pursuing a B.S. or M.S. in CS or equivalent, graduating Fall 2026 to Summer 2027",
                    "Experience with databases (AWS, SQL) and solid understanding of algorithms",
                    "Proficient in at least one OOP language (Python, Java, Kotlin)",
                    "Available for a May or June 2026 start date (12-week program)",
                ],
                "description": (
                    "Software Engineer Intern at DoorDash — Summer 2026\n\n"
                    "During the 12-week internship, develop, maintain, and ship products. "
                    "Hosted in-person at NYC, SF, Sunnyvale, LA, or Seattle. "
                    "Relocation and housing assistance provided.\n\n"
                    "Source: https://careersatdoordash.com/jobs/software-engineer-intern-summer-2026---us/7262223"
                ),
            },
            {
                "title": "Machine Learning Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing a Master's or PhD in CS, ML, Statistics, or related field",
                    "Strong programming skills in Python and ML frameworks (PyTorch, TensorFlow)",
                    "Experience with NLP, recommendation systems, or computer vision",
                    "Available for a summer 2026 internship",
                ],
                "description": (
                    "Machine Learning Intern at DoorDash — Summer 2026\n\n"
                    "Work on ML problems at scale — recommendation systems, search ranking, "
                    "delivery optimization, fraud detection, and more.\n\n"
                    "Source: https://careersatdoordash.com/jobs/machine-learning-intern-masters---summer-2026/7295800/"
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
