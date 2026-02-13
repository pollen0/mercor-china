#!/usr/bin/env python3
"""
Seed intern jobs from a scraped Getro JSON file into the Pathway database.

Usage:
  cd apps/api && source venv/bin/activate

  # Preview what will be inserted
  python -m scripts.seed_from_json --input scripts/data/khosla.json --firm "Khosla Ventures" --dry-run

  # Insert into DB
  python -m scripts.seed_from_json --input scripts/data/khosla.json --firm "Khosla Ventures"
"""
import sys
import os
import json
import re
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import uuid
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.database import Base
from app.models.employer import (
    Employer, Job, Organization, OrganizationMember,
    Vertical, RoleType, OrganizationRole,
)
from app.utils.auth import get_password_hash
from app.config import settings


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Helpers
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def generate_cuid(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}"


def slugify(name: str) -> str:
    """Convert company name to URL-safe slug."""
    slug = name.lower().strip()
    slug = re.sub(r'[^a-z0-9\s-]', '', slug)
    slug = re.sub(r'[\s-]+', '-', slug)
    return slug.strip('-')


def domain_from_company(company: str) -> str:
    """Guess domain from company name for email generation."""
    clean = re.sub(r'[^a-z0-9]', '', company.lower())
    return f"{clean}.com"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Title → Vertical / RoleType mapping
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# More specific patterns first, fallback at end
VERTICAL_PATTERNS = [
    # Design
    (r'(ux|ui|product\s*design|design)', Vertical.DESIGN),
    # Data
    (r'(machine\s*learning|ml\b|data\s*scien|data\s*analy|data\s*engineer|ai\s*research)', Vertical.DATA),
    # Product
    (r'(product\s*manag|program\s*manag|\bpm\b|product\s*ops)', Vertical.PRODUCT),
    # Finance
    (r'(financ|account|invest|analyst(?!.*data))', Vertical.FINANCE),
    # Software Engineering (broadest — fallback)
    (r'(software|engineer|developer|swe|frontend|backend|fullstack|full\s*stack|devops|embedded|mobile|ios|android|platform|infrastructure|security|qa|quality|sre|cloud|web\s*dev)', Vertical.SOFTWARE_ENGINEERING),
]

ROLE_TYPE_PATTERNS = [
    # Data
    (r'(machine\s*learning|ml\b)', RoleType.ML_ENGINEER),
    (r'data\s*scien', RoleType.DATA_SCIENTIST),
    (r'data\s*analy', RoleType.DATA_ANALYST),
    (r'data\s*engineer', RoleType.DATA_ENGINEER),
    # Design
    (r'ux', RoleType.UX_DESIGNER),
    (r'ui', RoleType.UI_DESIGNER),
    (r'product\s*design', RoleType.PRODUCT_DESIGNER),
    # Product
    (r'(product\s*manag|associate\s*pm|\bapm\b)', RoleType.ASSOCIATE_PM),
    (r'(program\s*manag|\bpm\b|product\s*ops)', RoleType.PRODUCT_MANAGER),
    # Finance
    (r'(investment\s*bank|ib\s*analyst)', RoleType.IB_ANALYST),
    (r'(financ|account)', RoleType.FINANCE_ANALYST),
    (r'(equity|research)', RoleType.EQUITY_RESEARCH),
    # Engineering (specific)
    (r'front\s*end|frontend', RoleType.FRONTEND_ENGINEER),
    (r'back\s*end|backend', RoleType.BACKEND_ENGINEER),
    (r'embedded', RoleType.EMBEDDED_ENGINEER),
    (r'(qa|quality)', RoleType.QA_ENGINEER),
    (r'(mobile|ios|android)', RoleType.SOFTWARE_ENGINEER),
    # Engineering (fallback)
    (r'(software|engineer|developer|swe|devops|platform|infrastructure|security|sre|cloud|web\s*dev)', RoleType.SOFTWARE_ENGINEER),
]


def classify_vertical(title: str) -> Vertical:
    lower = title.lower()
    for pattern, vertical in VERTICAL_PATTERNS:
        if re.search(pattern, lower):
            return vertical
    return Vertical.SOFTWARE_ENGINEERING


def classify_role_type(title: str) -> RoleType:
    lower = title.lower()
    for pattern, role_type in ROLE_TYPE_PATTERNS:
        if re.search(pattern, lower):
            return role_type
    return RoleType.SOFTWARE_ENGINEER


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Salary estimation
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

# Monthly salary estimates by vertical (US intern market)
SALARY_ESTIMATES = {
    Vertical.SOFTWARE_ENGINEERING: (7000, 10000),
    Vertical.DATA: (6500, 9500),
    Vertical.PRODUCT: (6000, 8500),
    Vertical.DESIGN: (5500, 8000),
    Vertical.FINANCE: (6000, 9000),
}


def parse_salary(salary_text: str | None) -> tuple[int | None, int | None]:
    """
    Parse salary text into monthly min/max.
    Handles: $55/hr, $55-65/hr, $5000/month, $60,000/year, etc.
    """
    if not salary_text:
        return None, None

    # Clean up
    text = salary_text.lower().replace(",", "").replace(" ", "")

    # Hourly rate: $XX/hr → monthly (assuming ~168 hrs/month)
    hourly_match = re.search(r'\$(\d+(?:\.\d+)?)\s*(?:/\s*h|per\s*h|hourly)', text)
    if hourly_match:
        rate = float(hourly_match.group(1))
        monthly = int(rate * 168)
        return monthly, monthly + 1000

    # Hourly range: $XX-$YY/hr
    hourly_range = re.search(r'\$(\d+)\s*-\s*\$?(\d+)\s*(?:/\s*h|per\s*h|hourly)', text)
    if hourly_range:
        low = int(hourly_range.group(1)) * 168
        high = int(hourly_range.group(2)) * 168
        return low, high

    # Annual: $XX,000/year → monthly
    annual_match = re.search(r'\$(\d+(?:,?\d+)?)\s*(?:/\s*y|per\s*y|annual|yearly)', text)
    if annual_match:
        annual = int(annual_match.group(1).replace(",", ""))
        if annual > 1000:  # Likely annual
            return annual // 12, annual // 12 + 500

    # Monthly: $XXXX/month
    monthly_match = re.search(r'\$(\d+(?:,?\d+)?)\s*(?:/\s*m|per\s*m|month)', text)
    if monthly_match:
        monthly = int(monthly_match.group(1).replace(",", ""))
        return monthly, monthly + 1000

    return None, None


def estimate_salary(vertical: Vertical, location: str | None = None) -> tuple[int, int]:
    """Estimate salary based on vertical and location."""
    base_min, base_max = SALARY_ESTIMATES.get(vertical, (6000, 8500))

    # Adjust for high-cost-of-living areas
    if location:
        loc_lower = location.lower()
        hcol_cities = ["san francisco", "new york", "palo alto", "menlo park",
                       "mountain view", "sunnyvale", "cupertino", "seattle"]
        if any(city in loc_lower for city in hcol_cities):
            base_min = int(base_min * 1.15)
            base_max = int(base_max * 1.15)

    return base_min, base_max


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Industry inference
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

INDUSTRY_PATTERNS = [
    (r'(health|medical|bio|pharma|clinic|patient)', 'Healthcare / AI'),
    (r'(fintech|payment|banking|lending|credit|insur)', 'Fintech'),
    (r'(security|cyber|threat|fraud)', 'Cybersecurity'),
    (r'(devtool|developer\s*tool|sdk|api\s*platform|infrastructure)', 'AI / Developer Tools'),
    (r'(education|edtech|learn|teach|tutor)', 'Education / AI'),
    (r'(climate|energy|solar|battery|ev\b|clean)', 'Climate / Energy'),
    (r'(robot|autonomous|self.driv|drone)', 'Robotics / AI'),
    (r'(legal|law\b|compliance)', 'Legal Tech'),
    (r'(real\s*estate|proptech|housing)', 'Real Estate / PropTech'),
    (r'(logistics|supply\s*chain|shipping|delivery)', 'Logistics'),
    (r'(retail|ecommerce|e-commerce|commerce)', 'Retail / E-Commerce'),
    (r'(media|content|video|stream|entertainment)', 'Media / Entertainment'),
    (r'(ai\b|artificial\s*intelligence|machine\s*learn|deep\s*learn|llm|genai)', 'AI / Infrastructure'),
    (r'(saas|software|cloud|data\s*platform|analytics)', 'SaaS / Data'),
]


def infer_industry(title: str, tags: list[str], description: str | None = None) -> str:
    """Infer industry from job metadata."""
    combined = f"{title} {' '.join(tags)} {description or ''}".lower()
    for pattern, industry in INDUSTRY_PATTERNS:
        if re.search(pattern, combined):
            return industry
    return "Technology"


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# DB operations (reused from seed_template.py)
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

    slug = company_data.get("slug", slugify(company_name))
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


def add_jobs_to_existing(session, company_name, jobs_data):
    """
    Add new jobs to a company that already exists in the DB.
    Deduplicates by job title. Returns number of jobs added.
    """
    employer = session.query(Employer).filter(
        Employer.company_name == company_name
    ).first()

    if not employer:
        print(f"  NOT FOUND: {company_name} — will create as new company")
        return -1  # Signal to caller to create as new

    existing_titles = {
        j.title
        for j in session.query(Job).filter(Job.employer_id == employer.id).all()
    }

    job_count = 0
    for job_data in jobs_data:
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


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Transform scraped JSON to seed format
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def transform_jobs(scraped_data: dict, firm_name: str) -> dict[str, dict]:
    """
    Group scraped jobs by company and transform into seed-ready format.
    Returns dict of { company_name: { company_data with jobs } }.
    """
    board_url = scraped_data["metadata"]["boardUrl"]
    companies: dict[str, dict] = {}

    for job in scraped_data["jobs"]:
        company = job.get("company", "").strip()
        if not company:
            company = "Unknown Company"

        title = job.get("title", "").strip()
        if not title:
            continue

        location = job.get("location", "").strip()
        tags = job.get("tags", [])
        description_text = job.get("description", "")
        requirements = job.get("requirements", [])
        salary_text = job.get("salary")
        detail_url = job.get("detailUrl", "")

        # Classify
        vertical = classify_vertical(title)
        role_type = classify_role_type(title)

        # Salary
        salary_min, salary_max = parse_salary(salary_text)
        if salary_min is None or salary_max is None:
            est_min, est_max = estimate_salary(vertical, location)
            salary_min = salary_min or est_min
            salary_max = salary_max or est_max

        # Build description
        desc_parts = []
        if description_text:
            # Truncate long descriptions
            desc_parts.append(description_text[:2000])
        else:
            desc_parts.append(f"{title} at {company}")
        desc_parts.append(f"\nFund: {firm_name} | Source: {detail_url or board_url}")
        full_description = "\n".join(desc_parts)

        # Build requirements if not scraped
        if not requirements:
            requirements = _default_requirements(vertical, title)

        # Build job entry
        job_entry = {
            "title": title,
            "vertical": vertical,
            "role_type": role_type,
            "location": location or "Remote, US",
            "salary_min": salary_min,
            "salary_max": salary_max,
            "requirements": requirements[:5],
            "description": full_description,
        }

        # Initialize company entry if needed
        if company not in companies:
            industry = infer_industry(title, tags, description_text)
            domain = domain_from_company(company)
            companies[company] = {
                "company_name": company,
                "email": f"careers@{domain}",
                "name": f"{company} Team",
                "industry": industry,
                "company_size": "startup",
                "website": f"https://{domain}",
                "slug": slugify(company),
                "description": f"{company} — {firm_name} portfolio company.\n\nFund: {firm_name} | Source: {board_url}",
                "founders": [],
                "jobs": [],
            }

        companies[company]["jobs"].append(job_entry)

    return companies


def _default_requirements(vertical: Vertical, title: str) -> list[str]:
    """Generate default requirements based on vertical."""
    base = ["Currently enrolled in a US university", "Available for Summer 2026"]

    if vertical == Vertical.SOFTWARE_ENGINEERING:
        return base + ["Proficiency in at least one programming language (Python, Java, TypeScript, etc.)"]
    elif vertical == Vertical.DATA:
        return base + ["Experience with Python, SQL, and data analysis tools"]
    elif vertical == Vertical.PRODUCT:
        return base + ["Strong analytical and communication skills"]
    elif vertical == Vertical.DESIGN:
        return base + ["Portfolio demonstrating UX/UI design skills"]
    elif vertical == Vertical.FINANCE:
        return base + ["Strong quantitative and analytical skills"]
    return base


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Main
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

def main():
    parser = argparse.ArgumentParser(description="Seed jobs from scraped Getro JSON")
    parser.add_argument("--input", required=True, help="Path to scraped JSON file")
    parser.add_argument("--firm", required=True, help="VC firm name (e.g., 'Khosla Ventures')")
    parser.add_argument("--dry-run", action="store_true", help="Preview without inserting")
    args = parser.parse_args()

    # Load JSON
    if not os.path.exists(args.input):
        print(f"ERROR: File not found: {args.input}")
        sys.exit(1)

    with open(args.input, "r") as f:
        scraped_data = json.load(f)

    metadata = scraped_data.get("metadata", {})
    print("=" * 60)
    print(f"Seed from JSON — {args.firm}")
    print(f"  Source:       {metadata.get('boardUrl', 'unknown')}")
    print(f"  Scraped at:   {metadata.get('scrapedAt', 'unknown')}")
    print(f"  Total on board: {metadata.get('totalJobsOnBoard', '?')}")
    print(f"  US intern jobs: {metadata.get('usInternJobs', '?')}")
    print(f"  Dry run:      {args.dry_run}")
    print("=" * 60)

    # Transform
    companies = transform_jobs(scraped_data, args.firm)

    print(f"\nGrouped into {len(companies)} companies:")
    for name, data in sorted(companies.items()):
        job_count = len(data["jobs"])
        verticals = set(j["vertical"].value for j in data["jobs"])
        print(f"  {name}: {job_count} job(s) — {', '.join(verticals)}")

    if args.dry_run:
        total_jobs = sum(len(c["jobs"]) for c in companies.values())
        print(f"\n{'=' * 60}")
        print(f"DRY RUN — would insert:")
        print(f"  Companies: {len(companies)}")
        print(f"  Jobs:      {total_jobs}")
        print(f"{'=' * 60}")
        return

    # Connect to DB
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)

    total_companies = 0
    total_jobs = 0
    errors = []

    print(f"\n--- Inserting {len(companies)} companies ---")

    for company_name, company_data in sorted(companies.items()):
        session = Session()
        try:
            print(f"\n[{company_name}]")

            # Check if company already exists — if so, just add new jobs
            existing = session.query(Employer).filter(
                Employer.company_name == company_name
            ).first()

            if existing:
                jobs_added = add_jobs_to_existing(
                    session, company_name, company_data["jobs"]
                )
                if jobs_added == -1:
                    # Shouldn't happen since we just found it, but handle gracefully
                    jobs_added = 0
            else:
                jobs_added = seed_new_company(session, company_data)
                if jobs_added > 0:
                    total_companies += 1

            session.commit()
            total_jobs += max(jobs_added, 0)
            print(f"  OK: {max(jobs_added, 0)} job(s)")

        except Exception as e:
            session.rollback()
            error_msg = f"{company_name}: {e}"
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
    print(f"{args.firm} seed complete:")
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
