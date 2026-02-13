#!/usr/bin/env python3
"""
Seed intern jobs from Khosla Ventures portfolio companies into the Pathway database.

Source: https://jobs.khoslaventures.com
Scraped: 2026-02-11, updated 2026-02-13
US-based intern positions only.

Companies: 21 (13 original + 8 new)
Jobs: 34 (17 original + 10 additional for existing + 7 new company jobs)
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
FIRM_NAME = "Khosla Ventures"
SCRIPT_ID = "khosla"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Affirm ──
    {
        "company_name": "Affirm",
        "email": "careers@affirm.com",
        "name": "Max Levchin",
        "industry": "Fintech / Payments",
        "company_size": "enterprise",
        "website": "https://www.affirm.com",
        "slug": "affirm",
        "description": (
            "Affirm is a financial technology company that provides buy now, pay later "
            "services. Founded by PayPal co-founder Max Levchin, Affirm offers transparent "
            "installment plans with no hidden fees.\n\n"
            "Fund: Khosla Ventures | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Max Levchin", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/maxlevchin"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Experience with Python, C/C++, or Java",
                    "Frontend skills with JavaScript, React, or AngularJS",
                    "Strong object-oriented programming knowledge",
                    "API development and deployment/testing frameworks experience",
                    "Available for 12-16 week internship, Summer 2026",
                ],
                "description": (
                    "Software Engineering Intern at Affirm (Summer 2026)\n\n"
                    "Develop and ship production code on real projects. Your team will depend "
                    "on your contributions. Mentorship provided with regular feedback sessions. "
                    "Present work to the engineering organization upon completion. $55/hr base pay.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/affirm/jobs/62641458-software-engineering-intern-summer-2026"
                ),
            },
        ],
    },
    # ── 2. DoorDash ──
    {
        "company_name": "DoorDash",
        "email": "careers@doordash.com",
        "name": "Tony Xu",
        "industry": "Logistics / Delivery",
        "company_size": "enterprise",
        "website": "https://www.doordash.com",
        "slug": "doordash",
        "description": (
            "DoorDash is the leading on-demand delivery platform connecting consumers with "
            "local businesses. Founded by Stanford students, DoorDash operates across the US, "
            "Canada, Australia, and Japan.\n\n"
            "Fund: Khosla Ventures | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Tony Xu", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/xutony"},
            {"name": "Andy Fang", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/fangsterr"},
            {"name": "Stanley Tang", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/stanleytang"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 13000,
                "requirements": [
                    "Pursuing B.S. or M.S. in Computer Science or equivalent",
                    "Maximum 2 years full-time work experience",
                    "Graduating Fall 2026 to Summer 2027",
                    "Strong algorithms, data structures, and OOP skills (Python, Java, Kotlin)",
                    "Database experience with AWS, SQL; must be authorized to work in the US",
                ],
                "description": (
                    "Software Engineer Intern at DoorDash (Summer 2026)\n\n"
                    "12-week in-person internship at DoorDash offices in New York, San Francisco, "
                    "Sunnyvale, Los Angeles, or Seattle. Develop, maintain, and ship products "
                    "with direct business impact. Attend leadership speaker sessions and present "
                    "learnings at program conclusion. Compensation: $107,400-$158,000/yr.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/doordash/jobs/60070337-software-engineer-intern-summer-2026-us"
                ),
            },
        ],
    },
    # ── 3. OpenAI ──
    {
        "company_name": "OpenAI",
        "email": "careers@openai.com",
        "name": "Sam Altman",
        "industry": "AI / Research",
        "company_size": "enterprise",
        "website": "https://www.openai.com",
        "slug": "openai",
        "description": (
            "OpenAI is an AI research and deployment company building safe and beneficial "
            "artificial general intelligence. Creators of GPT-4 and ChatGPT, OpenAI is at "
            "the forefront of AI development.\n\n"
            "Fund: Khosla Ventures | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Sam Altman", "title": "CEO", "linkedin": "https://linkedin.com/in/sam-altman-4384094"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern, Applied Emerging Talent (Fall 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 11000,
                "requirements": [
                    "Pursuing Bachelor's or Master's in Computer Science or related field",
                    "At least one semester remaining after internship",
                    "Proficiency in JavaScript, React, and backend languages (Python)",
                    "Experience with relational databases (Postgres/MySQL)",
                    "Interest in AI/ML preferred; ability to work in dynamic environments",
                ],
                "description": (
                    "Software Engineer Internship / Co-op at OpenAI (Fall 2026)\n\n"
                    "15-week paid, on-site internship in San Francisco. Build new customer-facing "
                    "ChatGPT and OpenAI API features. Collaborate across engineering, research, "
                    "product, and design teams. $60/hr + equity. Benefits include medical/dental/vision, "
                    "401(k) matching, relocation support, and daily office meals.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/openai/jobs/65336977-software-engineer-internship-co-op-applied-emerging-talent-fall-2026"
                ),
            },
        ],
    },
    # ── 4. Replit ──
    {
        "company_name": "Replit",
        "email": "careers@replit.com",
        "name": "Amjad Masad",
        "industry": "AI / Developer Tools",
        "company_size": "startup",
        "website": "https://replit.com",
        "slug": "replit",
        "description": (
            "Replit is a browser-based IDE and AI-powered development platform used by over "
            "30 million developers. Build, share, and ship software from anywhere with "
            "collaborative coding tools.\n\n"
            "Fund: Khosla Ventures | HQ: Foster City, CA"
        ),
        "founders": [
            {"name": "Amjad Masad", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/amjadmasad"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Foster City, CA",
                "salary_min": 7000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing Bachelor's, Master's, or PhD in Computer Science or related field",
                    "At least one semester remaining after internship",
                    "Proficient in programming; comfortable with full-stack development",
                    "Interest in developer tools, AI, or accessibility tech",
                ],
                "description": (
                    "Software Engineering Intern at Replit (Summer 2026)\n\n"
                    "12-week paid internship working alongside world-class engineers, designers, "
                    "and product managers. Ship real features to millions of developers. Work on "
                    "AI-powered development tools. Hybrid schedule (in-office M/W/F) in Foster City, CA.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/repl-it-2/jobs/59807815-software-engineering-intern-summer-2026"
                ),
            },
        ],
    },
    # ── 5. Zocdoc ──
    {
        "company_name": "Zocdoc",
        "email": "careers@zocdoc.com",
        "name": "Oliver Kharraz",
        "industry": "Healthcare / Tech",
        "company_size": "startup",
        "website": "https://www.zocdoc.com",
        "slug": "zocdoc",
        "description": (
            "Zocdoc is a digital health marketplace connecting patients with doctors. "
            "Patients can find doctors, read reviews, and book appointments instantly. "
            "Zocdoc serves millions of patients across the US.\n\n"
            "Fund: Khosla Ventures | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Oliver Kharraz", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/kharraz"},
            {"name": "Cyrus Massoumi", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/cyrus-massoumi-58330b"},
        ],
        "jobs": [
            {
                "title": "Machine Learning Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "New York, NY",
                "salary_min": 7000,
                "salary_max": 7500,
                "requirements": [
                    "Pursuing Master's with focus on ML, AI, or Data Science",
                    "Strong CS fundamentals (data structures, algorithms)",
                    "Experience with ML frameworks like TensorFlow, PyTorch, or Scikit-learn",
                    "Cloud computing experience (AWS, GCP, or Azure)",
                    "Available June 3 - August 14, 2026",
                ],
                "description": (
                    "Machine Learning Software Engineering Intern at Zocdoc (Summer 2026)\n\n"
                    "Work on ML/AI products in a production environment. Participate in ZocU "
                    "(week-long training), work with Python, Scala, C#, React, and LLM frameworks "
                    "from Anthropic and OpenAI. Present summer project to leadership. $40-$43/hr.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/zocdoc-3/jobs/66830269-machine-learning-software-engineering-internship"
                ),
            },
        ],
    },
    # ── 6. Okta ──
    {
        "company_name": "Okta",
        "email": "careers@okta.com",
        "name": "Todd McKinnon",
        "industry": "Cybersecurity / Identity",
        "company_size": "enterprise",
        "website": "https://www.okta.com",
        "slug": "okta",
        "description": (
            "Okta is the leading independent identity provider. Okta's platform enables "
            "secure access to applications, devices, and data for enterprises and individuals. "
            "Trusted by thousands of organizations worldwide.\n\n"
            "Fund: Khosla Ventures | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Todd McKinnon", "title": "CEO & Co-Founder", "linkedin": ""},
            {"name": "Frederic Kerrest", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Events Marketing Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.MARKETING_ASSOCIATE,
                "location": "San Francisco, CA",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Enrolled in Bachelor's or Master's program (Marketing, Business, or Communications)",
                    "Expected graduation December 2026 or May/June 2027",
                    "Proficiency with Excel/Google Sheets and Google Slides",
                    "Strong written communication and attention to detail",
                ],
                "description": (
                    "Events Marketing Intern at Okta (Summer 2026)\n\n"
                    "Join the Strategic Events and Experiences team. Support event planning, "
                    "logistics, and marketing initiatives. 12-week paid internship in San Francisco.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/okta/jobs/67510467-paid-media-intern-summer-2026"
                ),
            },
            {
                "title": "Paid Media Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.MARKETING_ASSOCIATE,
                "location": "San Francisco, CA",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Enrolled in Bachelor's or Master's program (Marketing, Business, Data Analytics, or Communications)",
                    "Expected graduation December 2026 or May/June 2027",
                    "Data analysis comfort and attention to detail",
                    "Understanding of paid vs. organic search results",
                ],
                "description": (
                    "Paid Media Intern at Okta (Summer 2026)\n\n"
                    "Manage paid advertising budgets across Google, Bing, and LinkedIn. "
                    "Campaign setup, creative asset coordination, ad copywriting, performance "
                    "reporting, and competitor analysis. San Francisco or Chicago.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/okta/jobs/67510467-paid-media-intern-summer-2026"
                ),
            },
            {
                "title": "Business Systems Analyst Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.BUSINESS_ANALYST,
                "location": "San Francisco, CA",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Enrolled in Bachelor's or Master's (Business Admin, HR, IS, CS or related)",
                    "Graduating December 2026 or Spring 2027",
                    "Basic understanding of cloud-based applications and data structures",
                    "Experience with Workday, Greenhouse, or Cornerstone preferred",
                ],
                "description": (
                    "Business Systems Analyst Intern at Okta (Summer 2026)\n\n"
                    "12-week internship supporting HR and business systems. Monitor ServiceNow "
                    "queue, triage requests, daily transaction processing, system configuration, "
                    "reporting, and cross-functional collaboration.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/okta/jobs/65706361-business-systems-analyst-intern-summer-2026"
                ),
            },
            {
                "title": "Digital Solutions Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Enrolled in Bachelor's or Master's program in CS, IS, or related field",
                    "Expected graduation December 2026 or May/June 2027",
                    "Interest in digital solutions and enterprise technology",
                    "Strong analytical and problem-solving skills",
                ],
                "description": (
                    "Digital Solutions Intern at Okta (Summer 2026)\n\n"
                    "Work on digital solutions and enterprise technology initiatives. "
                    "Locations: San Francisco, Chicago, Bellevue, or Seattle. "
                    "12-week paid internship.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/okta/jobs/7551302"
                ),
            },
        ],
    },
    # ── 7. Arista Networks ──
    {
        "company_name": "Arista Networks",
        "email": "careers@arista.com",
        "name": "Jayshree Ullal",
        "industry": "Networking / Cloud Infrastructure",
        "company_size": "enterprise",
        "website": "https://www.arista.com",
        "slug": "arista-networks",
        "description": (
            "Arista Networks is a leader in data-driven, client-to-cloud networking for "
            "large data centers, campuses, and routing environments. Known for their "
            "Extensible Operating System (EOS) and CloudVision platform.\n\n"
            "Fund: Khosla Ventures | HQ: Santa Clara, CA"
        ),
        "founders": [
            {"name": "Andy Bechtolsheim", "title": "Co-Founder", "linkedin": ""},
            {"name": "David Cheriton", "title": "Co-Founder", "linkedin": ""},
            {"name": "Ken Duda", "title": "Co-Founder & CTO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "System Test Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.QA_ENGINEER,
                "location": "Santa Clara, CA",
                "salary_min": 6500,
                "salary_max": 7000,
                "requirements": [
                    "BS in CS/CE/EE plus 1+ years of experience; MS preferred",
                    "Experience creating test methodologies and writing test plans",
                    "Knowledge of networking protocols and system software",
                    "Strong programming and scripting skills",
                ],
                "description": (
                    "System Test Engineer Intern at Arista Networks (Summer 2026)\n\n"
                    "Write test plans to validate Arista features and products. Design test "
                    "network topologies to validate functionality, performance, stability, and "
                    "scalability. Work as an agile member of a development and test team. "
                    "Base pay: $80,000-$85,000/yr.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/arista-networks-2/jobs/67547726-system-test-engineer-intern"
                ),
            },
        ],
    },
    # ── 8. Rocket Lab ──
    {
        "company_name": "Rocket Lab",
        "email": "careers@rocketlabusa.com",
        "name": "Peter Beck",
        "industry": "Aerospace / Space",
        "company_size": "startup",
        "website": "https://www.rocketlabusa.com",
        "slug": "rocket-lab",
        "description": (
            "Rocket Lab is a global leader in launch services and space systems. "
            "They design and manufacture the Electron and Neutron rockets, as well as "
            "spacecraft components and satellite systems.\n\n"
            "Fund: Khosla Ventures | HQ: Long Beach, CA"
        ),
        "founders": [
            {"name": "Peter Beck", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/peter-beck-ab7b63b"},
        ],
        "jobs": [
            {
                "title": "Business Development Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.BUSINESS_ANALYST,
                "location": "Long Beach, CA",
                "salary_min": 4000,
                "salary_max": 4500,
                "requirements": [
                    "Enrolled in bachelor's program (Engineering, Business Admin, CS, EE, Physics, or Math)",
                    "Minimum 3.0 GPA; 3.5+ preferred",
                    "3+ months applied engineering experience (internship, lab, or projects)",
                    "At least one semester remaining after internship",
                    "US citizenship or permanent residency required (ITAR)",
                ],
                "description": (
                    "Business Development Intern at Rocket Lab (Summer 2026)\n\n"
                    "Connect government and commercial customers with launch and space systems "
                    "solutions. Apply engineering concepts, attend mentoring sessions, and "
                    "participate in networking events. Full-time on-site for 12+ weeks. "
                    "$25/hr + equity + relocation stipend.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/rocket-lab/jobs/64162508-business-development-intern-summer-2026"
                ),
            },
            {
                "title": "Space Operations Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Long Beach, CA",
                "salary_min": 4000,
                "salary_max": 5000,
                "requirements": [
                    "Enrolled in bachelor's or master's program in Aerospace, CS, EE, or related field",
                    "Interest in space operations and satellite systems",
                    "Programming experience preferred",
                    "US citizenship or permanent residency required (ITAR)",
                ],
                "description": (
                    "Space Operations Intern at Rocket Lab (Summer 2026)\n\n"
                    "Support space operations and satellite systems at Rocket Lab's "
                    "Long Beach facility. On-site position.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/rocket-lab/jobs/space-operations-intern"
                ),
            },
        ],
    },
    # ── 9. Collaborative Robotics (Cobot) ──
    {
        "company_name": "Collaborative Robotics",
        "email": "careers@co.bot",
        "name": "Brad Porter",
        "industry": "Robotics / AI",
        "company_size": "startup",
        "website": "https://www.co.bot",
        "slug": "collaborative-robotics",
        "description": (
            "Collaborative Robotics (Cobot) builds robots that work alongside humans. "
            "Founded by former Amazon Robotics VP Brad Porter, backed by Sequoia, "
            "General Catalyst, and Khosla Ventures.\n\n"
            "Fund: Khosla Ventures | HQ: Santa Clara, CA"
        ),
        "founders": [
            {"name": "Brad Porter", "title": "CEO & Founder", "linkedin": "https://linkedin.com/in/brad-porter-cobot"},
        ],
        "jobs": [
            {
                "title": "Test Engineer Intern (6-Month Internship)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Santa Clara, CA",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing engineering degree (Robotics, Mechanical, Electrical, Computer, or similar)",
                    "Programming experience in Python or C++",
                    "Interest in robotics, hardware, and/or software testing",
                    "Must have and maintain US work authorization",
                ],
                "description": (
                    "Test Engineer Intern at Collaborative Robotics (Cobot)\n\n"
                    "6-month on-site internship in Santa Clara. Support testing and verification "
                    "of robotic systems. Run tests, analyze results, improve testing processes "
                    "for both software and hardware. Design tests for the robotics software stack, "
                    "test hardware components, and contribute to test automation.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/cobot-2-78ddc5fe-4d32-40b2-83f1-bcca662b07a6/jobs/63903700-test-engineer-intern-6-month-internship"
                ),
            },
        ],
    },
    # ── 10. Cape Analytics ──
    {
        "company_name": "Cape Analytics",
        "email": "careers@capeanalytics.com",
        "name": "Ryan Kottenstette",
        "industry": "AI / Insurance / Geospatial",
        "company_size": "startup",
        "website": "https://capeanalytics.com",
        "slug": "cape-analytics",
        "description": (
            "Cape Analytics provides AI-based geospatial imagery data for property risk "
            "investigation. Acquired by Moody's in 2025, Cape Analytics uses computer vision "
            "to analyze satellite and aerial imagery.\n\n"
            "Fund: Khosla Ventures | HQ: Mountain View, CA"
        ),
        "founders": [
            {"name": "Ryan Kottenstette", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/ryankottenstette"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Mountain View, CA",
                "salary_min": 6000,
                "salary_max": 6500,
                "requirements": [
                    "Bachelor's degree anticipated in CS or STEM field",
                    "Graduation December 2026 - June 2027",
                    "Experience with Python, SQL, AWS/GCP/Azure",
                    "Data pipeline and ETL/ELT familiarity; GitHub and Docker experience",
                    "Available June 1 - August 7, 2026",
                ],
                "description": (
                    "Software Engineer Intern at Cape Analytics / Moody's (Summer 2026)\n\n"
                    "Develop Python applications, implement OOP principles, SQL data work, "
                    "Docker containerization, and AWS projects. Participate in agile sprints. "
                    "$35/hr.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/cape-analytics/jobs/63214938-software-engineer-intern"
                ),
            },
        ],
    },
    # ── 11. BambooHR ──
    {
        "company_name": "BambooHR",
        "email": "careers@bamboohr.com",
        "name": "Brad Rencher",
        "industry": "HR Tech / SaaS",
        "company_size": "startup",
        "website": "https://www.bamboohr.com",
        "slug": "bamboohr",
        "description": (
            "BambooHR is a leading HR software provider for small and medium businesses. "
            "Offers tools for hiring, onboarding, compensation, performance management, "
            "and people data analytics.\n\n"
            "Fund: Khosla Ventures | HQ: Draper, UT"
        ),
        "founders": [
            {"name": "Ben Peterson", "title": "Co-Founder", "linkedin": ""},
            {"name": "Ryan Sanders", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/ryan-sanders-483113"},
        ],
        "jobs": [
            {
                "title": "AI Engineering / Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Draper, UT",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing Junior or Senior degree in Computer Science, Data Science, or related field",
                    "Proficiency with SQL and Python for data work",
                    "Experience with data exploration, visualization, and machine learning",
                    "Familiarity with LLMs and prompt engineering",
                    "Exposure to AWS or GCP cloud environments",
                ],
                "description": (
                    "AI Engineering / Data Science Intern at BambooHR (Summer 2026)\n\n"
                    "Full-time paid internship running May-August 2026 in Draper, Utah (hybrid). "
                    "Contribute to AI and machine learning initiatives alongside dedicated mentorship. "
                    "Collaborative data analysis, model development, NLP applications, and "
                    "deployment of AI systems.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/bamboohr-llc/jobs/66297606-ai-engineering-data-science-intern"
                ),
            },
        ],
    },
    # ── 12. Zendar ──
    {
        "company_name": "Zendar",
        "email": "careers@zendar.io",
        "name": "Vinayak Nagpal",
        "industry": "Autonomous Vehicles / Radar",
        "company_size": "startup",
        "website": "https://www.zendar.io",
        "slug": "zendar",
        "description": (
            "Zendar develops high-definition radar technology for autonomous vehicles. "
            "Founded by UC Berkeley PhDs, Zendar's Distributed Aperture Radar enables "
            "high-resolution 4D imaging for self-driving systems.\n\n"
            "Fund: Khosla Ventures | HQ: Berkeley, CA"
        ),
        "founders": [
            {"name": "Vinayak Nagpal", "title": "CEO & Co-Founder", "linkedin": ""},
            {"name": "Jimmy Wang", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Data Engineering Intern (2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_ENGINEER,
                "location": "Berkeley, CA",
                "salary_min": 6000,
                "salary_max": 6500,
                "requirements": [
                    "Recent graduate or enrolled in a graduate program in data science/engineering",
                    "Strong Python and SQL proficiency",
                    "Linux knowledge and cross-functional collaboration abilities",
                    "Interest in radar, autonomous vehicles, or sensor data a plus",
                ],
                "description": (
                    "Data Engineering Intern at Zendar (2026)\n\n"
                    "6-month, 40hr/week internship in Berkeley, CA. Maintain data indexing scripts, "
                    "evaluate data quality, enhance cleansing processes, support analysis through "
                    "reporting, and document workflows. $35/hr. Daily lunch provided.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/zendar/jobs/59286540-data-engineering-intern"
                ),
            },
        ],
    },
    # ── 13. Upstart ──
    {
        "company_name": "Upstart",
        "email": "careers@upstart.com",
        "name": "Dave Girouard",
        "industry": "Fintech / AI Lending",
        "company_size": "startup",
        "website": "https://www.upstart.com",
        "slug": "upstart",
        "description": (
            "Upstart is an AI lending platform that uses machine learning to improve access "
            "to affordable credit. Founded by former Google executives, Upstart partners with "
            "banks and credit unions to offer AI-powered loans.\n\n"
            "Fund: Khosla Ventures | HQ: San Mateo, CA"
        ),
        "founders": [
            {"name": "Dave Girouard", "title": "Co-Founder & Executive Chairman", "linkedin": "https://linkedin.com/in/davegirouard"},
            {"name": "Paul Gu", "title": "Co-Founder & CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Research Scientist Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Remote, US",
                "salary_min": 6000,
                "salary_max": 8000,
                "requirements": [
                    "Pursuing graduate degree in Statistics, Machine Learning, Economics, or related field",
                    "Strong programming skills in Python or R",
                    "Experience with statistical modeling and machine learning",
                    "Interest in fintech and AI-powered lending",
                ],
                "description": (
                    "Research Scientist Intern at Upstart (Summer 2026)\n\n"
                    "Remote internship within the United States. Apply machine learning and "
                    "statistical methods to improve lending models and credit decisions.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/upstart/jobs/7448874"
                ),
            },
        ],
    },
    # ── 14. Anchorage Digital ──
    {
        "company_name": "Anchorage Digital",
        "email": "careers@anchorage.com",
        "name": "Nathan McCauley",
        "industry": "Crypto / Fintech",
        "company_size": "startup",
        "website": "https://www.anchorage.com",
        "slug": "anchorage-digital",
        "description": (
            "Anchorage Digital is the first and only US federally chartered crypto bank. "
            "Provides institutional-grade custody, trading, staking, and governance services "
            "for digital assets.\n\n"
            "Fund: Khosla Ventures | HQ: New York, NY"
        ),
        "founders": [
            {"name": "Nathan McCauley", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/nathanmccauley"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Internship (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 7000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing Bachelor's or Master's in Computer Science or similar",
                    "Graduating December 2026 or Summer 2027",
                    "Ability to write, review, test, and document code to engineering standards",
                    "Experience with blockchain technology preferred but not required",
                ],
                "description": (
                    "Software Engineering Intern at Anchorage Digital (Summer 2026)\n\n"
                    "12-week program working within engineering teams to design, develop, and "
                    "deploy production code. Hybrid in New York (one day/week in-office). "
                    "Full software development lifecycle with mentorship.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/anchorage-digital/jobs/61003104-software-engineering-internship-summer-2026"
                ),
            },
        ],
    },
    # ── 15. Hermeus ──
    {
        "company_name": "Hermeus",
        "email": "careers@hermeus.com",
        "name": "AJ Piplica",
        "industry": "Aerospace / Hypersonic",
        "company_size": "startup",
        "website": "https://www.hermeus.com",
        "slug": "hermeus",
        "description": (
            "Hermeus is developing the fastest aircraft in the world — a hypersonic vehicle "
            "capable of Mach 5+ speeds. Backed by the US Air Force and top VCs, Hermeus is "
            "redefining high-speed travel.\n\n"
            "Fund: Khosla Ventures | HQ: Atlanta, GA"
        ),
        "founders": [
            {"name": "AJ Piplica", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/ajpiplica"},
        ],
        "jobs": [
            {
                "title": "Modeling & Simulation SWE Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Los Angeles, CA",
                "salary_min": 4300,
                "salary_max": 5700,
                "requirements": [
                    "Pursuing degree in CS, Aerospace Engineering, EE, Applied Math, or related",
                    "Proficiency in Julia or equivalent (Python, MATLAB, C++)",
                    "Understanding of 6DOF dynamics and simulation principles",
                    "Minimum 3.0 GPA; US person required (ITAR)",
                ],
                "description": (
                    "Modeling & Simulation SWE Intern at Hermeus (Summer 2026)\n\n"
                    "Develop high-performance simulation code for 6DOF Software-in-the-Loop "
                    "system. Collaborate across Flight Software, HMI, and Flight Sciences teams. "
                    "Design physics-informed models, validate against flight data. ~10 weeks, "
                    "$25-$33/hr.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/hermeus/jobs/59687412-modeling-simulation-software-engineering-intern-summer-2026"
                ),
            },
        ],
    },
    # ── 16. World (Worldcoin) ──
    {
        "company_name": "World",
        "email": "careers@world.org",
        "name": "Alex Blania",
        "industry": "Crypto / Identity / AI",
        "company_size": "startup",
        "website": "https://world.org",
        "slug": "world-worldcoin",
        "description": (
            "World (formerly Worldcoin) is building a global identity and financial network. "
            "Using biometric verification through the Orb device, World aims to create "
            "a universal proof of personhood. 17M+ verified World ID users.\n\n"
            "Fund: Khosla Ventures | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Alex Blania", "title": "CEO", "linkedin": ""},
            {"name": "Sam Altman", "title": "Co-Founder & Chairman", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Security Engineering Intern (2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7000,
                "salary_max": 10000,
                "requirements": [
                    "Experience or study in verifiable compute (zero knowledge ML, zkVMs)",
                    "Rust programming exposure",
                    "Critical thinking and communication skills",
                    "Familiarity with RiscZero, Succinct, or similar zkVM frameworks a plus",
                ],
                "description": (
                    "Security Engineering Intern at World (Summer 2026)\n\n"
                    "On-site in San Francisco. Build a blockchain-based verifiable compute system "
                    "for detection engineering. Work on distributed analytics platform protecting "
                    "17M+ World ID users across mobile, hardware, and blockchain infrastructure.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/world-2/jobs/64961374-security-engineering-internship"
                ),
            },
        ],
    },
    # ── 17. Checkr ──
    {
        "company_name": "Checkr",
        "email": "careers@checkr.com",
        "name": "Daniel Yanisse",
        "industry": "HR Tech / Background Checks",
        "company_size": "startup",
        "website": "https://checkr.com",
        "slug": "checkr",
        "description": (
            "Checkr is a leading background check platform built for the modern workforce. "
            "Uses AI and machine learning to streamline background screening for employers. "
            "Trusted by companies like Uber, DoorDash, and Instacart.\n\n"
            "Fund: Khosla Ventures | HQ: Denver, CO"
        ),
        "founders": [
            {"name": "Daniel Yanisse", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/yanisse"},
        ],
        "jobs": [
            {
                "title": "Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Denver, CO",
                "salary_min": 6000,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing degree in Computer Science or related field",
                    "Programming experience in one or more languages",
                    "Strong analytical and problem-solving skills",
                    "Not able to provide visa sponsorship",
                ],
                "description": (
                    "Engineering Intern at Checkr (Summer 2026)\n\n"
                    "10-week internship working on high-value engineering projects. "
                    "Work from Denver office 4 days/week. $35/hr.\n\n"
                    "Source: https://job-boards.greenhouse.io/checkr/jobs/7575425"
                ),
            },
        ],
    },
    # ── 18. Square (Block) ──
    {
        "company_name": "Square",
        "email": "careers@block.xyz",
        "name": "Jack Dorsey",
        "industry": "Fintech / Payments",
        "company_size": "enterprise",
        "website": "https://squareup.com",
        "slug": "square-block",
        "description": (
            "Square (a Block company) builds tools that help sellers of all sizes start, "
            "run, and grow their businesses. Products include Square POS, Cash App, and "
            "TIDAL. Founded by Jack Dorsey.\n\n"
            "Fund: Khosla Ventures | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Jack Dorsey", "title": "Co-Founder & Chairman", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Mobile Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 6750,
                "salary_max": 8850,
                "requirements": [
                    "Pursuing degree in CS, EE, Math, or related field (graduating May 2027-2030)",
                    "Previous internship or project experience building iOS or Android apps",
                    "Programming experience in Kotlin, Swift, Java, or Python",
                    "Strong problem-solving and communication skills",
                ],
                "description": (
                    "Mobile Software Engineer Intern at Square/Block (Summer 2026)\n\n"
                    "Work on iOS and Android mobile applications on a small team across "
                    "engineering, product, and creative. Build products serving millions of "
                    "users. San Francisco Bay Area. $39-$51/hr.\n\n"
                    "Source: https://block.xyz/careers/jobs/5083061008"
                ),
            },
        ],
    },
    # ── 19. Parallel Web Systems ──
    {
        "company_name": "Parallel Web Systems",
        "email": "careers@parallelweb.com",
        "name": "Parag Agrawal",
        "industry": "AI / Web Infrastructure",
        "company_size": "startup",
        "website": "https://parallelweb.com",
        "slug": "parallel-web-systems",
        "description": (
            "Parallel Web Systems is building a new web by and for AIs, with innovations "
            "across crawling, indexing, ranking, retrieval, and reasoning systems. "
            "Founded by former Twitter CEO Parag Agrawal.\n\n"
            "Fund: Khosla Ventures | HQ: Palo Alto, CA"
        ),
        "founders": [
            {"name": "Parag Agrawal", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/paragagr"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Palo Alto, CA",
                "salary_min": 7000,
                "salary_max": 10000,
                "requirements": [
                    "Strong programming skills",
                    "Interest in web infrastructure, search, or AI systems",
                    "Ability to work in-person in Palo Alto",
                    "Self-directed with strong problem-solving skills",
                ],
                "description": (
                    "Software Engineering Intern at Parallel Web Systems (Summer 2026)\n\n"
                    "Join a small, talent-dense team building AI-powered web infrastructure. "
                    "Fully in-person in Palo Alto. Work on crawling, indexing, ranking, retrieval, "
                    "and reasoning systems.\n\n"
                    "Source: https://jobs.ashbyhq.com/parallel/c77e251e-c976-451a-85da-564bfe2fb454"
                ),
            },
        ],
    },
    # ── 20. Glydways ──
    {
        "company_name": "Glydways",
        "email": "careers@glydways.com",
        "name": "Gokul Hemmady",
        "industry": "Autonomous Vehicles / Transit",
        "company_size": "startup",
        "website": "https://www.glydways.com",
        "slug": "glydways",
        "description": (
            "Glydways is building autonomous transit systems — small, electric, self-driving "
            "vehicles that operate on dedicated guideways. Reimagining public transit with "
            "on-demand, point-to-point autonomous pods.\n\n"
            "Fund: Khosla Ventures | HQ: San Mateo, CA"
        ),
        "founders": [
            {"name": "Mark Seeger", "title": "Founder", "linkedin": ""},
            {"name": "Gokul Hemmady", "title": "CEO", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern, Dispatch - Fleet Optimization (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 5000,
                "salary_max": 7000,
                "requirements": [
                    "Strong programming skills in C++ and/or Python",
                    "Background in optimization, robotics, applied math, or simulation",
                    "Interest in autonomous systems and fleet optimization",
                    "Ability to write production-quality code with tests and documentation",
                ],
                "description": (
                    "SWE Intern at Glydways - Dispatch & Fleet Optimization (Summer 2026)\n\n"
                    "Design and implement algorithms for fleet-level planning and optimization. "
                    "Work on real-time routing, load-balancing, charging decisions, and "
                    "simulation experiments. C++ and Python codebase.\n\n"
                    "Source: https://job-boards.greenhouse.io/glydways/jobs/5032392007"
                ),
            },
        ],
    },
    # ── 21. Commonwealth Fusion Systems ──
    {
        "company_name": "Commonwealth Fusion Systems",
        "email": "careers@cfs.energy",
        "name": "Bob Mumgaard",
        "industry": "Energy / Fusion",
        "company_size": "startup",
        "website": "https://cfs.energy",
        "slug": "commonwealth-fusion-systems",
        "description": (
            "Commonwealth Fusion Systems is developing commercial fusion energy using "
            "high-temperature superconducting magnets. A spinout from MIT, CFS is building "
            "SPARC, a compact fusion device.\n\n"
            "Fund: Khosla Ventures | HQ: Devens, MA"
        ),
        "founders": [
            {"name": "Bob Mumgaard", "title": "Co-Founder & CEO", "linkedin": "https://linkedin.com/in/mumgaard"},
        ],
        "jobs": [
            {
                "title": "Materials Test Engineer Intern - Fall Co-op 2026",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.EMBEDDED_ENGINEER,
                "location": "Devens, MA",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing degree in Materials Science, Mechanical Engineering, or related field",
                    "Lab experience with materials testing preferred",
                    "Strong analytical and problem-solving skills",
                    "Interest in fusion energy and clean energy technology",
                ],
                "description": (
                    "Materials Test Engineer Intern at Commonwealth Fusion Systems (Fall 2026)\n\n"
                    "Co-op position in Devens, MA. Work on testing and characterization of "
                    "materials for fusion energy systems. Hands-on lab work supporting "
                    "the SPARC fusion project.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/commonwealth-fusion-systems"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    # ── DoorDash: ML Intern ──
    {
        "company_name": "DoorDash",
        "jobs": [
            {
                "title": "Machine Learning Intern, Masters (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 11000,
                "salary_max": 16000,
                "requirements": [
                    "Pursuing Master's in CS, ML, NLP, Statistics, or related",
                    "Graduating Fall 2026 to Summer 2027",
                    "Proficiency in Python, Java, C++, or ML frameworks",
                    "Research experience in ML/AI preferred",
                ],
                "description": (
                    "Machine Learning Intern at DoorDash (Summer 2026)\n\n"
                    "12-week internship in SF, Sunnyvale, NYC, or Seattle. Work on ML/AI, "
                    "NLP, RecSys, Ranking, Computer Vision, Causal Inference, Ad Tech. "
                    "$130,600-$192,000/yr.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/doordash/jobs/60463270-machine-learning-intern-masters-summer-2026"
                ),
            },
        ],
    },
    # ── Rocket Lab: Software Intern (Colorado) ──
    {
        "company_name": "Rocket Lab",
        "jobs": [
            {
                "title": "Software Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Littleton, CO",
                "salary_min": 4700,
                "salary_max": 4700,
                "requirements": [
                    "Enrolled in BS/MS/PhD in CS, Computer Engineering, or Software Engineering",
                    "Minimum 3.0 GPA; 3.5+ preferred",
                    "3+ months applied engineering experience",
                    "Python, C/C++, or Git experience preferred",
                    "US person required (ITAR)",
                ],
                "description": (
                    "Software Intern at Rocket Lab (Summer 2026)\n\n"
                    "Support Flight Software Team in Littleton, CO. Develop modern software "
                    "engineering products to advance spacecraft software development, simulation, "
                    "configuration, and test. $27/hr + relocation stipend. 12+ weeks on-site.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/rocket-lab/jobs/58037527-software-intern-summer-2026"
                ),
            },
        ],
    },
    # ── Okta: BDR Intern ──
    {
        "company_name": "Okta",
        "jobs": [
            {
                "title": "Business Development Representative Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.BUSINESS_ANALYST,
                "location": "San Francisco, CA",
                "salary_min": 4000,
                "salary_max": 5500,
                "requirements": [
                    "Pursuing Bachelor's degree (graduating December 2026 or Spring 2027)",
                    "Excellent verbal and written communication skills",
                    "Strong organizational and analytical abilities",
                    "Interest in sales career",
                ],
                "description": (
                    "BDR Intern at Okta (Summer 2026)\n\n"
                    "12-week internship on Okta's Business Development team. Research prospects, "
                    "use Salesforce, attend enablement meetings, qualify leads. In-office 4 days/week. "
                    "Multiple US locations: SF, Chicago, Seattle, Bellevue, DC.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/okta/jobs/65218878-business-development-representative-intern-summer-2026"
                ),
            },
        ],
    },
    # ── Zocdoc: SWE Summer Internship ──
    {
        "company_name": "Zocdoc",
        "jobs": [
            {
                "title": "Software Engineering Summer Internship (2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 7000,
                "salary_max": 7500,
                "requirements": [
                    "Pursuing degree in Computer Science or related field",
                    "Strong CS fundamentals (data structures, algorithms)",
                    "Experience with object-oriented or functional programming",
                    "Available for summer 2026",
                ],
                "description": (
                    "Software Engineering Summer Intern at Zocdoc (2026)\n\n"
                    "Work on production code in New York. Technologies include Python, Scala, "
                    "C#, React. Participate in ZocU training and present project to leadership. "
                    "$40-$43/hr.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/zocdoc-3"
                ),
            },
        ],
    },
    # ── BambooHR: Cloud Engineering + Business Systems ──
    {
        "company_name": "BambooHR",
        "jobs": [
            {
                "title": "Cloud Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Draper, UT",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing degree in Computer Science, IT, or related field",
                    "Interest in cloud infrastructure and DevOps",
                    "Familiarity with AWS or GCP",
                    "Strong problem-solving skills",
                ],
                "description": (
                    "Cloud Engineering Intern at BambooHR (Summer 2026)\n\n"
                    "Work on cloud infrastructure projects in Draper, UT (hybrid/remote). "
                    "Full-time paid internship May-August 2026.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/bamboohr-llc"
                ),
            },
            {
                "title": "Business Systems Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Draper, UT",
                "salary_min": 4500,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing degree in CS, Information Systems, or related field",
                    "Interest in business systems and integrations",
                    "SQL and scripting experience preferred",
                    "Strong analytical skills",
                ],
                "description": (
                    "Business Systems Engineering Intern at BambooHR (Summer 2026)\n\n"
                    "Work on business systems and integrations in Draper, UT (hybrid/remote). "
                    "Full-time paid internship May-August 2026.\n\n"
                    "Source: https://jobs.khoslaventures.com/companies/bamboohr-llc"
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
