"""
Seed data for majors table.
Contains average GPA data and rigor ratings for common majors at top universities.

Sources:
- Berkeley: berkeleytime.com
- Stanford: Stanford grade reports
- MIT: MIT registrar
- Others: Estimated based on department type and school reputation
"""

from typing import List, Dict

# Major rigor tiers:
# 5 = Hardest (EECS at top schools)
# 4 = Very Hard (CS, EE, Physics at most schools)
# 3 = Challenging (Other engineering, math, sciences)
# 2 = Moderate (Business, economics, social sciences)
# 1 = Standard (Humanities, arts)

MAJORS: List[Dict] = [
    # ============= UC BERKELEY =============
    {
        "id": "berkeley_eecs",
        "university_id": "berkeley",
        "name": "Electrical Engineering and Computer Sciences",
        "short_name": "EECS",
        "department": "EECS",
        "rigor_tier": 5,
        "rigor_score": 9.5,
        "average_gpa": 3.20,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "aliases": ["EE/CS", "Electrical Engineering & Computer Science"],
        "source": "berkeleytime",
        "source_url": "https://berkeleytime.com/grades"
    },
    {
        "id": "berkeley_cs_ls",
        "university_id": "berkeley",
        "name": "Computer Science (L&S)",
        "short_name": "CS",
        "department": "CS",
        "rigor_tier": 5,
        "rigor_score": 9.0,
        "average_gpa": 3.25,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "aliases": ["L&S CS", "Letters & Science CS"],
        "source": "berkeleytime"
    },
    {
        "id": "berkeley_data_science",
        "university_id": "berkeley",
        "name": "Data Science",
        "short_name": "Data Sci",
        "department": "Data Science",
        "rigor_tier": 4,
        "rigor_score": 8.0,
        "average_gpa": 3.35,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["data", "software_engineering"],
        "source": "berkeleytime"
    },
    {
        "id": "berkeley_haas",
        "university_id": "berkeley",
        "name": "Business Administration",
        "short_name": "Haas",
        "department": "Haas",
        "rigor_tier": 3,
        "rigor_score": 6.5,
        "average_gpa": 3.50,
        "is_stem": False,
        "is_technical": False,
        "field_category": "business",
        "relevant_to": ["product", "business"],
        "source": "berkeleytime"
    },
    {
        "id": "berkeley_economics",
        "university_id": "berkeley",
        "name": "Economics",
        "short_name": "Econ",
        "department": "Economics",
        "rigor_tier": 3,
        "rigor_score": 6.0,
        "average_gpa": 3.30,
        "is_stem": False,
        "is_technical": False,
        "field_category": "social_science",
        "relevant_to": ["business", "product"],
        "source": "berkeleytime"
    },
    {
        "id": "berkeley_math",
        "university_id": "berkeley",
        "name": "Mathematics",
        "short_name": "Math",
        "department": "Math",
        "rigor_tier": 4,
        "rigor_score": 7.5,
        "average_gpa": 3.15,
        "is_stem": True,
        "is_technical": True,
        "field_category": "science",
        "relevant_to": ["data", "software_engineering"],
        "source": "berkeleytime"
    },
    {
        "id": "berkeley_stats",
        "university_id": "berkeley",
        "name": "Statistics",
        "short_name": "Stats",
        "department": "Statistics",
        "rigor_tier": 4,
        "rigor_score": 7.5,
        "average_gpa": 3.30,
        "is_stem": True,
        "is_technical": True,
        "field_category": "science",
        "relevant_to": ["data"],
        "source": "berkeleytime"
    },
    {
        "id": "berkeley_me",
        "university_id": "berkeley",
        "name": "Mechanical Engineering",
        "short_name": "ME",
        "department": "ME",
        "rigor_tier": 4,
        "rigor_score": 8.0,
        "average_gpa": 3.25,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "source": "berkeleytime"
    },

    # ============= STANFORD =============
    {
        "id": "stanford_cs",
        "university_id": "stanford",
        "name": "Computer Science",
        "short_name": "CS",
        "department": "CS",
        "rigor_tier": 5,
        "rigor_score": 9.5,
        "average_gpa": 3.50,  # Stanford has grade inflation
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "source": "stanford_registrar"
    },
    {
        "id": "stanford_ee",
        "university_id": "stanford",
        "name": "Electrical Engineering",
        "short_name": "EE",
        "department": "EE",
        "rigor_tier": 5,
        "rigor_score": 9.0,
        "average_gpa": 3.45,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering"],
        "source": "stanford_registrar"
    },
    {
        "id": "stanford_ms_e",
        "university_id": "stanford",
        "name": "Management Science & Engineering",
        "short_name": "MS&E",
        "department": "MS&E",
        "rigor_tier": 4,
        "rigor_score": 7.5,
        "average_gpa": 3.55,
        "is_stem": True,
        "is_technical": False,
        "field_category": "engineering",
        "relevant_to": ["product", "business"],
        "source": "stanford_registrar"
    },

    # ============= MIT =============
    {
        "id": "mit_eecs",
        "university_id": "mit",
        "name": "Electrical Engineering and Computer Science",
        "short_name": "Course 6",
        "department": "EECS",
        "rigor_tier": 5,
        "rigor_score": 9.5,
        "average_gpa": 4.0,  # MIT uses 5.0 scale, normalized
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "aliases": ["6-1", "6-2", "6-3"],
        "source": "mit_registrar"
    },
    {
        "id": "mit_math",
        "university_id": "mit",
        "name": "Mathematics",
        "short_name": "Course 18",
        "department": "Math",
        "rigor_tier": 5,
        "rigor_score": 9.0,
        "average_gpa": 4.1,
        "is_stem": True,
        "is_technical": True,
        "field_category": "science",
        "relevant_to": ["data", "software_engineering"],
        "source": "mit_registrar"
    },

    # ============= CMU =============
    {
        "id": "cmu_scs",
        "university_id": "cmu",
        "name": "Computer Science",
        "short_name": "SCS",
        "department": "SCS",
        "rigor_tier": 5,
        "rigor_score": 9.5,
        "average_gpa": 3.30,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "source": "cmu_registrar"
    },
    {
        "id": "cmu_ece",
        "university_id": "cmu",
        "name": "Electrical and Computer Engineering",
        "short_name": "ECE",
        "department": "ECE",
        "rigor_tier": 5,
        "rigor_score": 9.0,
        "average_gpa": 3.25,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering"],
        "source": "cmu_registrar"
    },

    # ============= UIUC =============
    {
        "id": "uiuc_cs",
        "university_id": "uiuc",
        "name": "Computer Science",
        "short_name": "CS",
        "department": "CS",
        "rigor_tier": 5,
        "rigor_score": 9.0,
        "average_gpa": 3.20,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "source": "estimated"
    },
    {
        "id": "uiuc_ce",
        "university_id": "uiuc",
        "name": "Computer Engineering",
        "short_name": "CompE",
        "department": "ECE",
        "rigor_tier": 5,
        "rigor_score": 8.5,
        "average_gpa": 3.15,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering"],
        "source": "estimated"
    },

    # ============= GEORGIA TECH =============
    {
        "id": "georgia_tech_cs",
        "university_id": "georgia_tech",
        "name": "Computer Science",
        "short_name": "CS",
        "department": "CS",
        "rigor_tier": 5,
        "rigor_score": 9.0,
        "average_gpa": 3.15,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "source": "estimated"
    },

    # ============= UCLA =============
    {
        "id": "ucla_cs",
        "university_id": "ucla",
        "name": "Computer Science",
        "short_name": "CS",
        "department": "CS",
        "rigor_tier": 5,
        "rigor_score": 8.5,
        "average_gpa": 3.25,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "source": "estimated"
    },
    {
        "id": "ucla_cse",
        "university_id": "ucla",
        "name": "Computer Science and Engineering",
        "short_name": "CSE",
        "department": "CSE",
        "rigor_tier": 5,
        "rigor_score": 8.5,
        "average_gpa": 3.20,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering"],
        "source": "estimated"
    },

    # ============= GENERIC MAJORS (for unmatched universities) =============
    {
        "id": "generic_cs",
        "university_id": None,  # Generic for any school
        "name": "Computer Science",
        "short_name": "CS",
        "department": "CS",
        "rigor_tier": 4,
        "rigor_score": 8.0,
        "average_gpa": None,  # Use raw GPA
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering", "data"],
        "source": "generic"
    },
    {
        "id": "generic_eecs",
        "university_id": None,
        "name": "Electrical Engineering and Computer Science",
        "short_name": "EECS",
        "department": "EECS",
        "rigor_tier": 5,
        "rigor_score": 8.5,
        "average_gpa": None,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering"],
        "source": "generic"
    },
    {
        "id": "generic_data_science",
        "university_id": None,
        "name": "Data Science",
        "short_name": "DS",
        "department": "Data Science",
        "rigor_tier": 4,
        "rigor_score": 7.5,
        "average_gpa": None,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["data", "software_engineering"],
        "source": "generic"
    },
    {
        "id": "generic_business",
        "university_id": None,
        "name": "Business Administration",
        "short_name": "Business",
        "department": "Business",
        "rigor_tier": 2,
        "rigor_score": 5.5,
        "average_gpa": None,
        "is_stem": False,
        "is_technical": False,
        "field_category": "business",
        "relevant_to": ["product", "business"],
        "source": "generic"
    },
    {
        "id": "generic_economics",
        "university_id": None,
        "name": "Economics",
        "short_name": "Econ",
        "department": "Economics",
        "rigor_tier": 3,
        "rigor_score": 6.0,
        "average_gpa": None,
        "is_stem": False,
        "is_technical": False,
        "field_category": "social_science",
        "relevant_to": ["business", "product"],
        "source": "generic"
    },
    {
        "id": "generic_math",
        "university_id": None,
        "name": "Mathematics",
        "short_name": "Math",
        "department": "Math",
        "rigor_tier": 4,
        "rigor_score": 7.5,
        "average_gpa": None,
        "is_stem": True,
        "is_technical": True,
        "field_category": "science",
        "relevant_to": ["data"],
        "source": "generic"
    },
    {
        "id": "generic_statistics",
        "university_id": None,
        "name": "Statistics",
        "short_name": "Stats",
        "department": "Statistics",
        "rigor_tier": 4,
        "rigor_score": 7.0,
        "average_gpa": None,
        "is_stem": True,
        "is_technical": True,
        "field_category": "science",
        "relevant_to": ["data"],
        "source": "generic"
    },
    {
        "id": "generic_ee",
        "university_id": None,
        "name": "Electrical Engineering",
        "short_name": "EE",
        "department": "EE",
        "rigor_tier": 4,
        "rigor_score": 8.0,
        "average_gpa": None,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "relevant_to": ["software_engineering"],
        "source": "generic"
    },
    {
        "id": "generic_me",
        "university_id": None,
        "name": "Mechanical Engineering",
        "short_name": "ME",
        "department": "ME",
        "rigor_tier": 4,
        "rigor_score": 7.5,
        "average_gpa": None,
        "is_stem": True,
        "is_technical": True,
        "field_category": "engineering",
        "source": "generic"
    },
    {
        "id": "generic_physics",
        "university_id": None,
        "name": "Physics",
        "short_name": "Physics",
        "department": "Physics",
        "rigor_tier": 4,
        "rigor_score": 7.5,
        "average_gpa": None,
        "is_stem": True,
        "is_technical": True,
        "field_category": "science",
        "relevant_to": ["data"],
        "source": "generic"
    },
]


def get_majors_for_seeding() -> List[Dict]:
    """Return the list of majors for database seeding."""
    return MAJORS
