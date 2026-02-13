#!/usr/bin/env python3
"""
Seed intern jobs from NEA (New Enterprise Associates) portfolio companies.

NEA is a global venture capital firm with $28B+ AUM, investing in technology
and healthcare companies at all stages. Portfolio includes Databricks, Cloudflare,
Plaid, Robinhood, MongoDB, Coursera, Tempus AI, Patreon, and GoodLeap.

Sources:
- https://www.nea.com/portfolio
- https://careers.nea.com/
- Individual company career pages

SCRIPT ID: nea
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
FIRM_NAME = "NEA"
SCRIPT_ID = "nea"


def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# NEW COMPANIES — Companies not yet in the database
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

COMPANIES = [
    # ── 1. Databricks ──
    {
        "company_name": "Databricks",
        "email": "careers@databricks.com",
        "name": "Ali Ghodsi",
        "industry": "AI / Data Infrastructure",
        "company_size": "enterprise",
        "website": "https://www.databricks.com",
        "slug": "databricks",
        "description": (
            "Databricks is the unified analytics platform for data engineering, "
            "data science, and machine learning. Founded by the creators of Apache Spark, "
            "Databricks helps organizations accelerate innovation by unifying data, analytics, and AI.\n\n"
            "Fund: NEA | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Ali Ghodsi", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/alighodsi"},
            {"name": "Matei Zaharia", "title": "CTO & Co-Founder", "linkedin": "https://linkedin.com/in/mateizaharia"},
            {"name": "Reynold Xin", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/rxin"},
            {"name": "Patrick Wendell", "title": "Co-Founder", "linkedin": "https://linkedin.com/in/patrick-wendell"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 10000,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, or related field (graduating Fall 2026 or Spring 2027)",
                    "Proficiency in Python, Java, or C++ with strong knowledge of algorithms and data structures",
                    "Interest in deep learning and experience with PyTorch preferred",
                    "Available for 12-week or 16-week summer internship",
                ],
                "description": (
                    "Software Engineering Intern at Databricks. Work across full stack, backend, "
                    "infrastructure, systems, tools, cloud, databases, and customer-facing products. "
                    "Hiring across all teams including data platform and AI/ML infrastructure.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/software-engineering-intern-2026-6866531002"
                ),
            },
            {
                "title": "Software Engineering Intern - Bellevue (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Bellevue, WA",
                "salary_min": 10000,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, or related field (graduating Fall 2026 or Spring 2027)",
                    "Implementation skills with Python, Java, or C++",
                    "Good knowledge of algorithms, data structures, and OOP principles",
                    "Available for 12-week or 16-week summer program",
                ],
                "description": (
                    "Software Engineering Intern at Databricks Bellevue office. Work alongside experienced "
                    "engineers on cloud infrastructure, data platform, and analytics products. "
                    "Options include winter 16-week co-op, summer 16-week co-op, or summer 12-week internship.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/software-engineering-intern-2026-6866534002"
                ),
            },
            {
                "title": "Data Science Intern (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 9500,
                "requirements": [
                    "Pursuing a degree in Computer Science, Statistics, Data Science, or related field",
                    "Strong foundation in machine learning and statistical modeling",
                    "Proficiency in Python and SQL",
                    "Experience with data analysis and visualization tools",
                ],
                "description": (
                    "Data Science Intern at Databricks. Apply machine learning and statistical methods "
                    "to solve real-world data challenges on the Databricks lakehouse platform. "
                    "Work with massive datasets and cutting-edge ML infrastructure.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/data-science-intern-2026-start-6866538002"
                ),
            },
            {
                "title": "Product Management Intern (Summer 2026)",
                "vertical": Vertical.PRODUCT,
                "role_type": RoleType.PRODUCT_MANAGER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 9500,
                "requirements": [
                    "Pursuing a degree in Computer Science, Business, or related field",
                    "Strong analytical and problem-solving skills",
                    "Excellent written and verbal communication",
                    "Interest in data infrastructure and AI/ML platforms",
                ],
                "description": (
                    "Product Management Intern at Databricks. Define product strategy, work with "
                    "engineering teams, and drive the roadmap for the unified analytics platform "
                    "used by thousands of organizations worldwide.\n\n"
                    "Source: https://www.databricks.com/company/careers/product/product-management-intern-summer-2026-6883068002"
                ),
            },
        ],
    },

    # ── 2. Cloudflare ──
    {
        "company_name": "Cloudflare",
        "email": "careers@cloudflare.com",
        "name": "Matthew Prince",
        "industry": "Cloud / Security / Infrastructure",
        "company_size": "enterprise",
        "website": "https://www.cloudflare.com",
        "slug": "cloudflare",
        "description": (
            "Cloudflare is a global cloud platform that provides a range of network services "
            "to businesses of all sizes, making them more secure and performant. "
            "Cloudflare announced a goal to hire 1,111 interns in 2026.\n\n"
            "Fund: NEA | HQ: San Francisco, CA | NYSE: NET"
        ),
        "founders": [
            {"name": "Matthew Prince", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/mprince"},
            {"name": "Michelle Zatlyn", "title": "President & Co-Founder", "linkedin": "https://linkedin.com/in/michellezatlyn"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026) - Austin",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 8000,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, Mathematics, or related field",
                    "Demonstrated critical thinking skills and drive to learn new technologies",
                    "In-office presence 3-5 days a week in Austin, TX",
                    "Available for 12-16 week summer internship",
                ],
                "description": (
                    "Software Engineer Intern at Cloudflare (Austin). Work alongside experienced engineers "
                    "to ship and deliver projects at Internet scale. Present your project to the entire "
                    "company at the end of the internship. Connect and learn from executives and co-founders.\n\n"
                    "Source: https://job-boards.greenhouse.io/cloudflare/jobs/7206269"
                ),
            },
            {
                "title": "Software Engineer Intern (Summer 2026) - San Francisco",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 8500,
                "salary_max": 9000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, Mathematics, or related field",
                    "Curiosity, empathy, and ability to get things done",
                    "Available for 12-16 week summer internship",
                    "Interest in building a better Internet at massive scale",
                ],
                "description": (
                    "Software Engineer Intern at Cloudflare (San Francisco HQ). Part of the 1,111 intern "
                    "program for 2026. Work on networking, security, performance, and developer tools "
                    "that power millions of Internet properties worldwide.\n\n"
                    "Source: https://job-boards.greenhouse.io/cloudflare/jobs/7296923"
                ),
            },
        ],
    },

    # ── 3. Plaid ──
    {
        "company_name": "Plaid",
        "email": "careers@plaid.com",
        "name": "Zach Perret",
        "industry": "Fintech / Banking Data",
        "company_size": "startup",
        "website": "https://plaid.com",
        "slug": "plaid",
        "description": (
            "Plaid is a fintech company that builds the infrastructure connecting consumer bank accounts "
            "to financial applications. Plaid's API powers thousands of apps including Venmo, Coinbase, "
            "and Betterment, enabling millions of people to manage their financial lives.\n\n"
            "Fund: NEA | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Zach Perret", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/zperret"},
            {"name": "William Hockey", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026) - SF",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9500,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, ML, Data Science, Physics, Math, or related field (graduating Winter 2026 or Spring 2027)",
                    "Strong grasp of computer science fundamentals",
                    "Proficiency in at least one programming language (Go, TypeScript, or Python preferred)",
                    "Project experience demonstrating technical ability",
                ],
                "description": (
                    "Software Engineering Intern at Plaid (San Francisco). Work with decoupled services, "
                    "distributed systems, and various programming languages. Gain hands-on experience "
                    "building financial infrastructure used by millions. $55.96/hr.\n\n"
                    "Source: https://builtin.com/job/plaid-software-engineering-intern-summer-2026-application-ripplematch/7094240"
                ),
            },
            {
                "title": "Software Engineering Intern (Summer 2026) - NYC",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 9500,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, ML, Data Science, Physics, Math, or related field (graduating Winter 2026 or Spring 2027)",
                    "Strong grasp of computer science fundamentals",
                    "Proficiency in at least one programming language (Go, TypeScript, or Python preferred)",
                    "Project experience demonstrating technical ability",
                ],
                "description": (
                    "Software Engineering Intern at Plaid (New York). Work on financial data infrastructure "
                    "that connects thousands of banks and fintechs. Build lasting connections while "
                    "contributing meaningful work. $55.96/hr.\n\n"
                    "Source: https://www.builtinnyc.com/job/plaid-software-engineering-intern-summer-2026-application-ripplematch/7094247"
                ),
            },
        ],
    },

    # ── 4. Robinhood ──
    {
        "company_name": "Robinhood",
        "email": "careers@robinhood.com",
        "name": "Vlad Tenev",
        "industry": "Fintech / Brokerage",
        "company_size": "enterprise",
        "website": "https://robinhood.com",
        "slug": "robinhood",
        "description": (
            "Robinhood is a financial services company that democratizes finance for all. "
            "The platform provides commission-free trading of stocks, ETFs, options, and crypto. "
            "Robinhood has millions of users and is publicly traded on NASDAQ.\n\n"
            "Fund: NEA | HQ: Menlo Park, CA | NASDAQ: HOOD"
        ),
        "founders": [
            {"name": "Vlad Tenev", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/vlad-tenev-7037591b"},
            {"name": "Baiju Bhatt", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern, Backend (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "Menlo Park, CA",
                "salary_min": 8000,
                "salary_max": 8500,
                "requirements": [
                    "Full-time student in penultimate year of undergraduate or graduate studies",
                    "Experience with Python/Django, Go, PostgreSQL, or Kafka",
                    "Understanding of distributed systems and scalable architectures",
                    "Passion for democratizing finance",
                ],
                "description": (
                    "Backend Software Engineering Intern at Robinhood. Maintain and scale an existing "
                    "codebase using Python/Django, Go, PostgreSQL, Kafka, Redis, Memcached, AWS, and "
                    "Kubernetes. Build features that serve millions of users.\n\n"
                    "Source: https://www.indexventures.com/startup-jobs/robinhood/software-developer-intern-backend-summer-2026/"
                ),
            },
            {
                "title": "Software Engineering Intern, Web (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.FRONTEND_ENGINEER,
                "location": "Menlo Park, CA",
                "salary_min": 8000,
                "salary_max": 8500,
                "requirements": [
                    "Full-time student in penultimate year of undergraduate or graduate studies",
                    "Experience with Modern JavaScript (ES6+), React, Redux, TypeScript",
                    "Familiarity with Babel, Webpack, and modern frontend tooling",
                    "Strong CS fundamentals",
                ],
                "description": (
                    "Web Software Engineering Intern at Robinhood. Build and improve the web trading "
                    "platform using React, Redux/Immutable, TypeScript, Babel + Webpack, Django, and Go. "
                    "Competitive compensation with stipends and lifestyle benefits.\n\n"
                    "Source: https://job-boards.greenhouse.io/robinhood/jobs/7239280"
                ),
            },
            {
                "title": "Software Engineering Intern, iOS (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Menlo Park, CA",
                "salary_min": 8000,
                "salary_max": 8500,
                "requirements": [
                    "Full-time student in penultimate year of undergraduate or graduate studies",
                    "Experience with UIKit, Auto Layout, Swift, or RxSwift",
                    "Understanding of iOS architecture patterns (VIPER, MVVM)",
                    "Strong CS fundamentals",
                ],
                "description": (
                    "iOS Software Engineering Intern at Robinhood. Work on the flagship mobile trading "
                    "app using UIKit, Auto Layout, RxSwift, Core Graphics, Core Animation, Lottie, "
                    "Core Data, and a VIPER-esque Architecture.\n\n"
                    "Source: https://job-boards.greenhouse.io/robinhood/jobs/7239268"
                ),
            },
            {
                "title": "Software Engineering Intern, Android (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Menlo Park, CA",
                "salary_min": 8000,
                "salary_max": 8500,
                "requirements": [
                    "Full-time student in penultimate year of undergraduate or graduate studies",
                    "Experience with Kotlin, RxJava 2, or Android development",
                    "Familiarity with Retrofit/OkHttp, Dagger 2, and Room",
                    "Strong CS fundamentals",
                ],
                "description": (
                    "Android Software Engineering Intern at Robinhood. Build and improve the Android "
                    "trading app using Kotlin, RxJava 2, Retrofit/OkHttp, Dagger 2, and Room. "
                    "Join a vibrant office with catered meals and commuter benefits.\n\n"
                    "Source: https://www.indexventures.com/startup-jobs/robinhood/software-engineering-intern-android-summer-2026/"
                ),
            },
        ],
    },

    # ── 5. MongoDB ──
    {
        "company_name": "MongoDB",
        "email": "careers@mongodb.com",
        "name": "CJ Desai",
        "industry": "Database / Infrastructure",
        "company_size": "enterprise",
        "website": "https://www.mongodb.com",
        "slug": "mongodb",
        "description": (
            "MongoDB is the leading modern, general-purpose database platform, designed to unleash "
            "the power of software and data for developers. The document database model is the best "
            "way to work with data, making it easier and faster to build applications.\n\n"
            "Fund: NEA | HQ: New York, NY | NASDAQ: MDB"
        ),
        "founders": [
            {"name": "Dwight Merriman", "title": "Co-Founder", "linkedin": ""},
            {"name": "Eliot Horowitz", "title": "Co-Founder", "linkedin": ""},
            {"name": "Kevin P. Ryan", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern, AMER - NYC (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 7000,
                "salary_max": 7500,
                "requirements": [
                    "Second year of a Bachelor's or Master's degree in Computer Science or related field (graduating Fall 2026 - Summer 2027)",
                    "Knowledge in Java, Python, Go, C++, JavaScript, or Node.js",
                    "Authorized to work in the United States",
                    "Available for 10 consecutive weeks (June to August), hybrid 3-5 days/week",
                ],
                "description": (
                    "Software Engineering Intern at MongoDB (New York). Full-time 40 hours/week for "
                    "10 weeks. Hybrid work expected 3-5 days in office. Chance to receive a full-time "
                    "offer at the end of summer. ~$41/hr.\n\n"
                    "Source: https://www.mongodb.com/careers/jobs/7239454"
                ),
            },
            {
                "title": "Software Engineering Intern, AMER - Austin (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Austin, TX",
                "salary_min": 7000,
                "salary_max": 7500,
                "requirements": [
                    "Second year of a Bachelor's or Master's degree in Computer Science or related field",
                    "Knowledge in Java, Python, Go, C++, JavaScript, or Node.js",
                    "Authorized to work in the United States",
                    "Available for 10 consecutive weeks, hybrid 3-5 days/week",
                ],
                "description": (
                    "Software Engineering Intern at MongoDB (Austin). Work on the world's most popular "
                    "document database. Collaborate with experienced engineers on database internals, "
                    "cloud services, and developer tools.\n\n"
                    "Source: https://www.mongodb.com/careers/jobs/7239454"
                ),
            },
            {
                "title": "Software Engineering Intern, AMER - SF (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 7000,
                "salary_max": 7500,
                "requirements": [
                    "Second year of a Bachelor's or Master's degree in Computer Science or related field",
                    "Knowledge in Java, Python, Go, C++, JavaScript, or Node.js",
                    "Authorized to work in the United States",
                    "Available for 10 consecutive weeks, hybrid 3-5 days/week",
                ],
                "description": (
                    "Software Engineering Intern at MongoDB (San Francisco). Build and scale one of the "
                    "most widely-used database platforms in the world. Potential for full-time conversion "
                    "at the end of the program.\n\n"
                    "Source: https://www.mongodb.com/careers/jobs/7239454"
                ),
            },
        ],
    },

    # ── 6. Coursera ──
    {
        "company_name": "Coursera",
        "email": "careers@coursera.org",
        "name": "Greg Hart",
        "industry": "EdTech / Online Learning",
        "company_size": "enterprise",
        "website": "https://www.coursera.org",
        "slug": "coursera",
        "description": (
            "Coursera is an online learning platform offering courses, certificates, and degrees from "
            "world-class universities and companies. With 100+ million learners worldwide, Coursera "
            "is transforming education through technology.\n\n"
            "Fund: NEA | HQ: Mountain View, CA | NYSE: COUR"
        ),
        "founders": [
            {"name": "Andrew Ng", "title": "Co-Founder & Chairman", "linkedin": "https://linkedin.com/in/andrewyng"},
            {"name": "Daphne Koller", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Remote, US",
                "salary_min": 6000,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing a degree in Computer Science, Software Engineering, or related field",
                    "Strong programming skills and interest in education technology",
                    "Experience with modern web frameworks and languages",
                    "Authorized to work in the United States",
                ],
                "description": (
                    "Software Engineer Intern at Coursera. Remote position available anywhere in the US. "
                    "Work on the platform that delivers online learning to 100+ million learners globally. "
                    "Build features that shape the future of education. ~$36.66/hr.\n\n"
                    "Source: https://nodesk.co/remote-jobs/coursera-software-engineer-intern/"
                ),
            },
        ],
    },

    # ── 7. Tempus AI ──
    {
        "company_name": "Tempus AI",
        "email": "careers@tempus.com",
        "name": "Eric Lefkofsky",
        "industry": "Healthcare / AI / Precision Medicine",
        "company_size": "enterprise",
        "website": "https://www.tempus.com",
        "slug": "tempus-ai",
        "description": (
            "Tempus AI is a technology company advancing precision medicine through AI and data science. "
            "Founded after CEO Eric Lefkofsky's wife was diagnosed with breast cancer, Tempus uses AI "
            "to help doctors deliver personalized cancer treatment.\n\n"
            "Fund: NEA | HQ: Chicago, IL | NASDAQ: TEM"
        ),
        "founders": [
            {"name": "Eric Lefkofsky", "title": "Founder & CEO", "linkedin": "https://linkedin.com/in/ericlefkofsky"},
        ],
        "jobs": [
            {
                "title": "Software Engineering Summer Analyst (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 5000,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing a degree in Computer Science, Software Engineering, or related field",
                    "Strong programming fundamentals in Python, Java, or similar",
                    "Interest in healthcare technology and precision medicine",
                    "Available for 8-10 weeks, hybrid 3 days/week in Chicago office",
                ],
                "description": (
                    "Software Engineering Summer Analyst at Tempus AI. Join the AI Platform (Air) team "
                    "building platform systems for scientists and engineers to deliver smarter medical "
                    "tests. Competitive hourly wage plus relocation bonus. Hybrid onsite 3 days/week.\n\n"
                    "Source: https://www.builtinchicago.org/job/software-engineering-summer-analystassociate/3788636"
                ),
            },
            {
                "title": "Machine Learning Summer Associate (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.ML_ENGINEER,
                "location": "Chicago, IL",
                "salary_min": 5500,
                "salary_max": 6500,
                "requirements": [
                    "Pursuing a Master's or Ph.D. in Computer Science, Data Science, Bioinformatics, or related field",
                    "Experience with machine learning frameworks (PyTorch, TensorFlow)",
                    "Strong foundation in statistics and mathematical modeling",
                    "Interest in applying AI to healthcare and precision medicine",
                ],
                "description": (
                    "Machine Learning Summer Associate at Tempus AI (Applied AI & Research). "
                    "Work on cutting-edge ML models for genomics, clinical data analysis, and "
                    "precision medicine. Collaborate with research scientists on real-world healthcare problems.\n\n"
                    "Source: https://www.purpose.jobs/discover/companies/tempus/jobs/45454854-machine-learning-summer-associate-applied-ai-research"
                ),
            },
            {
                "title": "Generative AI Summer Analyst (Summer 2026)",
                "vertical": Vertical.DATA,
                "role_type": RoleType.DATA_SCIENTIST,
                "location": "Chicago, IL",
                "salary_min": 5000,
                "salary_max": 6000,
                "requirements": [
                    "Pursuing a degree in biological sciences, biotechnology, or related field",
                    "Strong interest in AI/ML and data science in healthcare",
                    "Experience with Python and data analysis libraries",
                    "Interest in pursuing an MD/PhD program leveraging technology in healthcare",
                ],
                "description": (
                    "Generative AI Summer Analyst at Tempus AI. Work at the intersection of generative AI "
                    "and precision medicine. Help develop AI-powered tools for clinical decision-making "
                    "and genomic analysis.\n\n"
                    "Source: https://jobs.revolution.com/companies/tempus/jobs/44638013-generative-ai-summer-analyst"
                ),
            },
        ],
    },

    # ── 8. Patreon ──
    {
        "company_name": "Patreon",
        "email": "careers@patreon.com",
        "name": "Jack Conte",
        "industry": "Creator Economy / Social Platform",
        "company_size": "startup",
        "website": "https://www.patreon.com",
        "slug": "patreon",
        "description": (
            "Patreon is a membership platform that makes it easy for creators to get paid for their work. "
            "Over 250,000 creators use Patreon to run a membership business, offering exclusive content "
            "and community to millions of paying patrons.\n\n"
            "Fund: NEA | HQ: San Francisco, CA"
        ),
        "founders": [
            {"name": "Jack Conte", "title": "CEO & Co-Founder", "linkedin": "https://linkedin.com/in/jack-conte-a15a3686"},
            {"name": "Sam Yam", "title": "Co-Founder", "linkedin": ""},
        ],
        "jobs": [
            {
                "title": "Software Engineering Intern (Summer 2026) - SF",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "San Francisco, CA",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a Bachelor's or Master's degree in Computer Science, Software Engineering, or related technical field",
                    "Strong foundation in CS fundamentals and data structures",
                    "Proficiency in Python, Swift, Kotlin, or TypeScript",
                    "Able to be in-office 3 days per week (hybrid)",
                ],
                "description": (
                    "Software Engineering Intern at Patreon (San Francisco). Work with an experienced "
                    "engineer mentor to tackle technical challenges. Join an intern cohort and participate "
                    "in professional development opportunities. Competitive salary, equity, and benefits. "
                    "$55/hr.\n\n"
                    "Source: https://startup.jobs/software-engineering-intern-patreon-3740294"
                ),
            },
            {
                "title": "Software Engineering Intern (Summer 2026) - NYC",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "New York, NY",
                "salary_min": 9000,
                "salary_max": 10000,
                "requirements": [
                    "Pursuing a Bachelor's or Master's degree in Computer Science, Software Engineering, or related technical field",
                    "Strong foundation in CS fundamentals and data structures",
                    "Proficiency in Python, Swift, Kotlin, or TypeScript",
                    "Able to be in-office 3 days per week (hybrid)",
                ],
                "description": (
                    "Software Engineering Intern at Patreon (New York). Build features for the creator "
                    "economy platform used by millions. Hands-on experience with mentorship and professional "
                    "development opportunities. $55/hr with equity and benefits.\n\n"
                    "Source: https://www.builtinnyc.com/job/software-engineering-intern/7334282"
                ),
            },
        ],
    },

    # ── 9. GoodLeap ──
    {
        "company_name": "GoodLeap",
        "email": "careers@goodleap.com",
        "name": "Hayes Barnard",
        "industry": "Fintech / Sustainability / Clean Energy",
        "company_size": "startup",
        "website": "https://www.goodleap.com",
        "slug": "goodleap",
        "description": (
            "GoodLeap is the largest financial technology company in the US focused on sustainability. "
            "The platform delivers best-in-class financing for solar panels, batteries, and energy-efficient "
            "home solutions, with $50B+ in loan volume since inception.\n\n"
            "Fund: NEA | HQ: Roseville, CA"
        ),
        "founders": [
            {"name": "Hayes Barnard", "title": "Founder, Chairman & CEO", "linkedin": "https://linkedin.com/in/hayesbarnard"},
        ],
        "jobs": [
            {
                "title": "Software Engineer Intern (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.BACKEND_ENGINEER,
                "location": "Remote, US",
                "salary_min": 5500,
                "salary_max": 7000,
                "requirements": [
                    "Pursuing a degree in Computer Science or related field",
                    "Interest in backend development using Node.js or Python",
                    "Familiarity with event-driven architectures and APIs",
                    "Available for a 12-week internship",
                ],
                "description": (
                    "Software Engineer Intern at GoodLeap. Build event-driven backend services, "
                    "developing microservices that process real-time Kafka events and integrate with "
                    "internal APIs to support business-critical workflows. Work with Node.js or Python.\n\n"
                    "Source: https://www.goodleap.com/careers/286f7562-212b-4c37-9265-c8555577c1fc"
                ),
            },
        ],
    },
]


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ADDITIONAL JOBS — New jobs for companies that ALREADY exist in DB
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

ADDITIONAL_JOBS = [
    {
        "company_name": "Databricks",
        "jobs": [
            {
                "title": "Software Engineering Intern - Bellevue (Summer 2026)",
                "vertical": Vertical.SOFTWARE_ENGINEERING,
                "role_type": RoleType.SOFTWARE_ENGINEER,
                "location": "Bellevue, WA",
                "salary_min": 10000,
                "salary_max": 10500,
                "requirements": [
                    "Pursuing a degree in Computer Science, Engineering, or related field (graduating Fall 2026 or Spring 2027)",
                    "Implementation skills with Python, Java, or C++",
                    "Good knowledge of algorithms, data structures, and OOP principles",
                    "Available for 12-week or 16-week summer program",
                ],
                "description": (
                    "Software Engineering Intern at Databricks Bellevue office. Work alongside experienced "
                    "engineers on cloud infrastructure, data platform, and analytics products. "
                    "Options include winter 16-week co-op, summer 16-week co-op, or summer 12-week internship.\n\n"
                    "Source: https://www.databricks.com/company/careers/university-recruiting/software-engineering-intern-2026-6866534002"
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
