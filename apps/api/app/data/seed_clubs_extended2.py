"""
Extended seed data for university clubs at 29 additional universities (batch 2).
Schools: USC, Duke, Northwestern, Rice, NYU, UC Davis, UC Irvine, Ohio State,
Penn State, Virginia Tech, UVA, Brown, Yale, Johns Hopkins, NC State, UNC,
UMN, Stony Brook, Rutgers, ASU, UF, Northeastern, CU Boulder, Indiana,
UMass, TAMU, Rochester, Dartmouth, WashU.
"""

from typing import Dict, List


def _club(uid, short_id, name, short_name, cat, tier, score, **kw):
    """Helper to create a club dict with defaults."""
    return {
        "id": f"{uid}_{short_id}",
        "university_id": uid,
        "name": name,
        "short_name": short_name,
        "category": cat,
        "prestige_tier": tier,
        "prestige_score": score,
        "is_selective": kw.get("is_selective", tier >= 3),
        "acceptance_rate": kw.get("acceptance_rate"),
        "is_technical": kw.get("is_technical", True),
        "is_professional": kw.get("is_professional", False),
        "has_projects": kw.get("has_projects", False),
        "has_competitions": kw.get("has_competitions", False),
        "is_honor_society": kw.get("is_honor_society", False),
        "relevant_to": kw.get("relevant_to", ["software_engineering"]),
        "description": kw.get("description", name),
    }


def _standard_clubs(uid, school_short):
    """Generate standard club set for a university."""
    return [
        _club(uid, "acm", f"ACM@{school_short}", "ACM", "engineering", 2, 6.0,
              is_selective=False, has_projects=True,
              relevant_to=["software_engineering", "data_science"],
              description=f"ACM student chapter at {school_short}. General CS community, workshops, and tech talks."),
        _club(uid, "upe", f"Upsilon Pi Epsilon ({school_short})", "UPE", "professional", 4, 8.5,
              is_selective=True, acceptance_rate=0.15, is_professional=True, is_honor_society=True,
              relevant_to=["software_engineering", "data_science"],
              description="CS Honor Society. Top students by GPA. Strong industry connections."),
        _club(uid, "wics", f"Women in CS ({school_short})", "WiCS", "professional", 2, 5.5,
              is_selective=False, is_professional=True,
              relevant_to=["software_engineering", "data_science"],
              description="Supporting women in computer science through mentorship and events."),
        _club(uid, "ds_club", f"{school_short} Data Science Club", "DSC", "engineering", 2, 5.5,
              is_selective=False, has_projects=True,
              relevant_to=["data_science", "machine_learning"],
              description="Data science projects, workshops, and competitions."),
        _club(uid, "hack", f"Hack{school_short}", f"Hack{school_short}", "engineering", 3, 7.0,
              is_selective=True, acceptance_rate=0.25, has_competitions=True, has_projects=True,
              relevant_to=["software_engineering"],
              description=f"Student-run hackathon organization at {school_short}."),
        _club(uid, "ai_club", f"{school_short} AI Club", "AI Club", "engineering", 3, 6.5,
              is_selective=True, has_projects=True,
              relevant_to=["machine_learning", "data_science"],
              description="AI/ML research projects and reading groups."),
        _club(uid, "robotics", f"{school_short} Robotics Club", "Robotics", "engineering", 3, 6.5,
              is_selective=True, has_projects=True, has_competitions=True,
              relevant_to=["software_engineering", "hardware_engineering"],
              description="Robotics projects and competitions."),
        _club(uid, "consulting", f"{school_short} Tech Consulting", "Tech Consulting", "professional", 3, 7.0,
              is_selective=True, acceptance_rate=0.20, is_professional=True, has_projects=True,
              is_technical=False,
              relevant_to=["software_engineering", "product_management"],
              description="Pro-bono tech consulting for local organizations."),
        _club(uid, "swe", f"Society of Women Engineers ({school_short})", "SWE", "professional", 2, 5.5,
              is_selective=False, is_professional=True,
              relevant_to=["software_engineering", "hardware_engineering"],
              description="Professional development and networking for women in engineering."),
        _club(uid, "ieee", f"IEEE Student Branch ({school_short})", "IEEE", "professional", 2, 5.5,
              is_selective=False, is_professional=True,
              relevant_to=["software_engineering", "hardware_engineering"],
              description="IEEE student branch. Technical workshops and networking."),
    ]


# ============= UCSC CLUBS =============
UCSC_CLUBS: List[Dict] = _standard_clubs("ucsc", "UCSC") + [
    _club("ucsc", "acm_w", "ACM-W@UCSC", "ACM-W", "professional", 2, 5.5,
          is_selective=False, is_professional=True,
          description="ACM Women's chapter at UCSC. Mentorship and events for women in CS."),
    _club("ucsc", "slugbotics", "Slugbotics", "Slugbotics", "engineering", 3, 6.5,
          has_projects=True, has_competitions=True,
          description="UCSC robotics team. Competition robots and research projects."),
]

# ============= USC CLUBS =============
USC_CLUBS: List[Dict] = _standard_clubs("usc", "USC") + [
    _club("usc", "sce", "Society of Computer Engineers", "SCE", "engineering", 3, 6.5,
          has_projects=True, description="USC's main CS student org. Workshops, mentoring, career events."),
    _club("usc", "bits", "Bytes of Innovation", "BITS", "engineering", 3, 7.0,
          is_selective=True, has_projects=True, description="Selective product development club building real apps."),
]

# ============= DUKE CLUBS =============
DUKE_CLUBS: List[Dict] = _standard_clubs("duke", "Duke") + [
    _club("duke", "dtech", "Duke Technology", "DTech", "engineering", 4, 8.0,
          is_selective=True, acceptance_rate=0.12, has_projects=True,
          description="Selective tech club. Builds products for Duke and Durham community."),
    _club("duke", "hackduke", "HackDuke", "HackDuke", "engineering", 4, 7.5,
          is_selective=True, has_competitions=True, description="Duke's premier hackathon. Social good focus."),
]

# ============= NORTHWESTERN CLUBS =============
NORTHWESTERN_CLUBS: List[Dict] = _standard_clubs("northwestern", "NU") + [
    _club("northwestern", "dtr", "Develop and Innovate for Social Change", "DISC", "engineering", 3, 7.0,
          is_selective=True, has_projects=True, description="Tech for social good. Builds apps for nonprofits."),
]

# ============= RICE CLUBS =============
RICE_CLUBS: List[Dict] = _standard_clubs("rice", "Rice") + [
    _club("rice", "rds", "Rice Data Science", "RDS", "engineering", 3, 7.0,
          is_selective=True, has_projects=True, relevant_to=["data_science", "machine_learning"],
          description="Data science projects and competitions."),
]

# ============= NYU CLUBS =============
NYU_CLUBS: List[Dict] = _standard_clubs("nyu", "NYU") + [
    _club("nyu", "bugs", "BUGS Open Source", "BUGS", "engineering", 3, 6.5,
          has_projects=True, description="NYU's open-source software development club."),
    _club("nyu", "techatnyu", "Tech@NYU", "Tech@NYU", "engineering", 3, 7.0,
          is_selective=True, has_projects=True, description="NYU's main tech community. Events, hackathons, mentorship."),
]

# ============= UC DAVIS CLUBS =============
UC_DAVIS_CLUBS: List[Dict] = _standard_clubs("uc_davis", "Davis") + [
    _club("uc_davis", "codelab", "CodeLab", "CodeLab", "engineering", 4, 7.5,
          is_selective=True, acceptance_rate=0.15, has_projects=True,
          description="Selective software development team building real products."),
]

# ============= UC IRVINE CLUBS =============
UC_IRVINE_CLUBS: List[Dict] = _standard_clubs("uc_irvine", "UCI") + [
    _club("uc_irvine", "icssc", "ICS Student Council", "ICSSC", "professional", 3, 6.5,
          is_professional=True, description="Student government for ICS. Career events and advocacy."),
    _club("uc_irvine", "hack_uci", "Hack at UCI", "HackUCI", "engineering", 3, 7.0,
          has_competitions=True, description="UCI's largest hackathon organization."),
]

# ============= OHIO STATE CLUBS =============
OHIO_STATE_CLUBS: List[Dict] = _standard_clubs("ohio_state", "OSU") + [
    _club("ohio_state", "osuapp", "OSU App Development Club", "App Club", "engineering", 2, 6.0,
          has_projects=True, is_selective=False, description="Mobile and web app development projects."),
]

# ============= PENN STATE CLUBS =============
PENN_STATE_CLUBS: List[Dict] = _standard_clubs("penn_state", "PSU") + [
    _club("penn_state", "coda", "Code Alliance", "CODA", "engineering", 3, 6.5,
          has_projects=True, description="Collaborative software projects for social impact."),
]

# ============= VIRGINIA TECH CLUBS =============
VIRGINIA_TECH_CLUBS: List[Dict] = _standard_clubs("virginia_tech", "VT") + [
    _club("virginia_tech", "vtcyber", "VT Cyber Security Club", "CyberSec", "engineering", 3, 7.0,
          has_competitions=True, description="Cybersecurity competitions and CTF events."),
    _club("virginia_tech", "gdsc_vt", "Google Developer Student Club VT", "GDSC", "engineering", 2, 6.0,
          is_selective=False, has_projects=True, description="Google-sponsored tech community."),
]

# ============= UVA CLUBS =============
UVA_CLUBS: List[Dict] = _standard_clubs("uva", "UVA") + [
    _club("uva", "thecourseforum", "The Course Forum", "TCF", "engineering", 3, 7.0,
          has_projects=True, description="Student-built course review platform used by all UVA students."),
]

# ============= BROWN CLUBS =============
BROWN_CLUBS: List[Dict] = _standard_clubs("brown", "Brown") + [
    _club("brown", "fsab", "Full Stack at Brown", "FSAB", "engineering", 4, 8.0,
          is_selective=True, acceptance_rate=0.10, has_projects=True,
          description="Highly selective. Builds real software products for campus and community."),
    _club("brown", "bdr", "Brown Data Science", "BDS", "engineering", 3, 7.0,
          has_projects=True, relevant_to=["data_science", "machine_learning"],
          description="Data science research projects and datathons."),
]

# ============= YALE CLUBS =============
YALE_CLUBS: List[Dict] = _standard_clubs("yale", "Yale") + [
    _club("yale", "ycs", "Yale Computer Society", "YCS", "engineering", 3, 7.0,
          has_projects=True, description="Yale's main CS community. Hackathons and tech talks."),
    _club("yale", "yhack", "YHack", "YHack", "engineering", 4, 7.5,
          has_competitions=True, description="Yale's annual intercollegiate hackathon."),
]

# ============= JOHNS HOPKINS CLUBS =============
JOHNS_HOPKINS_CLUBS: List[Dict] = _standard_clubs("johns_hopkins", "JHU") + [
    _club("johns_hopkins", "hop", "Hopkins Organization for Programming", "HOP", "engineering", 3, 6.5,
          has_projects=True, has_competitions=True, description="Competitive programming and algorithm practice."),
]

# ============= NC STATE CLUBS =============
NC_STATE_CLUBS: List[Dict] = _standard_clubs("nc_state", "NCSU") + [
    _club("nc_state", "lug", "Linux Users Group", "LUG", "engineering", 2, 5.5,
          is_selective=False, has_projects=True, description="Open source and Linux advocacy."),
]

# ============= UNC CLUBS =============
UNC_CLUBS: List[Dict] = _standard_clubs("unc", "UNC") + [
    _club("unc", "cssg", "CS+Social Good", "CS+SG", "engineering", 3, 7.0,
          has_projects=True, description="Tech projects for social impact organizations."),
    _club("unc", "appteam", "App Team Carolina", "ATC", "engineering", 3, 7.0,
          is_selective=True, has_projects=True, description="iOS/Android development team."),
]

# ============= UMN CLUBS =============
UMN_CLUBS: List[Dict] = _standard_clubs("umn", "UMN") + [
    _club("umn", "gopherh", "GopherHacks", "GopherHacks", "engineering", 3, 6.5,
          has_competitions=True, description="UMN's student-run hackathon."),
]

# ============= STONY BROOK CLUBS =============
STONY_BROOK_CLUBS: List[Dict] = _standard_clubs("stony_brook", "SBU") + [
    _club("stony_brook", "sbuhacks", "SBUHacks", "SBUHacks", "engineering", 3, 6.5,
          has_competitions=True, description="Stony Brook's hackathon organization."),
]

# ============= RUTGERS CLUBS =============
RUTGERS_CLUBS: List[Dict] = _standard_clubs("rutgers", "Rutgers") + [
    _club("rutgers", "usacs", "Undergraduate Student Alliance of CS", "USACS", "professional", 3, 7.0,
          is_professional=True, description="Rutgers CS student government. Events, career fairs."),
    _club("rutgers", "hackru", "HackRU", "HackRU", "engineering", 3, 7.0,
          has_competitions=True, description="Rutgers' flagship hackathon."),
]

# ============= ASU CLUBS =============
ASU_CLUBS: List[Dict] = _standard_clubs("asu", "ASU") + [
    _club("asu", "softdev", "Software Developers Association", "SoDA", "engineering", 3, 7.0,
          has_projects=True, description="ASU's largest CS club. Projects, workshops, career events."),
]

# ============= UF CLUBS =============
UF_CLUBS: List[Dict] = _standard_clubs("uf", "UF") + [
    _club("uf", "swamphacks", "SwampHacks", "SwampHacks", "engineering", 3, 7.0,
          has_competitions=True, description="UF's annual hackathon. 500+ participants."),
    _club("uf", "osclub", "UF Open Source Club", "OSC", "engineering", 2, 6.0,
          is_selective=False, has_projects=True, description="Open source projects and workshops."),
]

# ============= NORTHEASTERN CLUBS =============
NORTHEASTERN_CLUBS: List[Dict] = _standard_clubs("northeastern", "NEU") + [
    _club("northeastern", "oasis", "Oasis", "Oasis", "engineering", 4, 7.5,
          is_selective=True, acceptance_rate=0.15, has_projects=True,
          description="Selective software development club. Builds products for the NEU community."),
    _club("northeastern", "sandboxnu", "Sandbox", "Sandbox", "engineering", 4, 8.0,
          is_selective=True, acceptance_rate=0.10, has_projects=True,
          description="NEU's most selective tech club. Full-stack product teams."),
]

# ============= CU BOULDER CLUBS =============
CU_BOULDER_CLUBS: List[Dict] = _standard_clubs("cu_boulder", "CU") + [
    _club("cu_boulder", "hackcu", "HackCU", "HackCU", "engineering", 3, 6.5,
          has_competitions=True, description="CU Boulder's annual hackathon."),
]

# ============= INDIANA CLUBS =============
INDIANA_CLUBS: List[Dict] = _standard_clubs("indiana", "IU") + [
    _club("indiana", "luddy", "Luddy Student Council", "LSC", "professional", 2, 5.5,
          is_selective=False, is_professional=True, is_technical=False,
          description="Student government for Luddy School of Informatics."),
]

# ============= UMASS CLUBS =============
UMASS_CLUBS: List[Dict] = _standard_clubs("umass", "UMass") + [
    _club("umass", "hackumass", "HackUMass", "HackUMass", "engineering", 3, 7.0,
          has_competitions=True, description="UMass's annual hackathon. 800+ participants."),
    _club("umass", "builds", "BUILD UMass", "BUILD", "engineering", 3, 7.0,
          is_selective=True, has_projects=True, description="Semester-long software projects for organizations."),
]

# ============= TAMU CLUBS =============
TAMU_CLUBS: List[Dict] = _standard_clubs("tamu", "TAMU") + [
    _club("tamu", "tamuhack", "TAMUhack", "TAMUhack", "engineering", 3, 7.0,
          has_competitions=True, description="Texas A&M's premier hackathon."),
    _club("tamu", "aggie_coding", "Aggie Coding Club", "ACC", "engineering", 2, 6.0,
          is_selective=False, has_competitions=True, description="Competitive programming and algorithm practice."),
]

# ============= ROCHESTER CLUBS =============
ROCHESTER_CLUBS: List[Dict] = _standard_clubs("rochester", "UR") + [
    _club("rochester", "dandelion", "Dandelion", "Dandelion", "engineering", 3, 6.5,
          has_projects=True, description="Rochester's student-run tech projects club."),
]

# ============= DARTMOUTH CLUBS =============
DARTMOUTH_CLUBS: List[Dict] = _standard_clubs("dartmouth", "Dartmouth") + [
    _club("dartmouth", "dali", "DALI Lab", "DALI", "engineering", 5, 9.5,
          is_selective=True, acceptance_rate=0.08, has_projects=True,
          relevant_to=["software_engineering", "product_management", "product_design"],
          description="Dartmouth's premier digital arts/tech lab. Extremely selective. Builds real products."),
    _club("dartmouth", "dalidata", "Dartmouth Data Science", "DDS", "engineering", 3, 6.5,
          has_projects=True, relevant_to=["data_science", "machine_learning"],
          description="Data science projects and competitions."),
]

# ============= WASHU CLUBS =============
WASHU_CLUBS: List[Dict] = _standard_clubs("washu", "WashU") + [
    _club("washu", "wuct", "WashU Cyber Team", "CyberTeam", "engineering", 3, 7.0,
          has_competitions=True, description="Cybersecurity competitions and CTF events."),
    _club("washu", "appdev", "WashU App Dev", "AppDev", "engineering", 3, 7.0,
          is_selective=True, has_projects=True, description="iOS/Android app development team."),
]


def get_extended_clubs2() -> List[Dict]:
    """Get all clubs from the second batch of extended universities."""
    return (
        UCSC_CLUBS + USC_CLUBS + DUKE_CLUBS + NORTHWESTERN_CLUBS + RICE_CLUBS
        + NYU_CLUBS + UC_DAVIS_CLUBS + UC_IRVINE_CLUBS
        + OHIO_STATE_CLUBS + PENN_STATE_CLUBS + VIRGINIA_TECH_CLUBS
        + UVA_CLUBS + BROWN_CLUBS + YALE_CLUBS + JOHNS_HOPKINS_CLUBS
        + NC_STATE_CLUBS + UNC_CLUBS + UMN_CLUBS + STONY_BROOK_CLUBS
        + RUTGERS_CLUBS + ASU_CLUBS + UF_CLUBS + NORTHEASTERN_CLUBS
        + CU_BOULDER_CLUBS + INDIANA_CLUBS + UMASS_CLUBS + TAMU_CLUBS
        + ROCHESTER_CLUBS + DARTMOUTH_CLUBS + WASHU_CLUBS
    )
