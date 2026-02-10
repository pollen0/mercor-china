"""
Extended seed data for university clubs at 49 additional universities (batch 3).
Schools ranked ~50-100 in CS.
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


# ============= VANDERBILT CLUBS =============
VANDERBILT_CLUBS: List[Dict] = _standard_clubs("vanderbilt", "Vanderbilt") + [
    _club("vanderbilt", "change_plus_plus", "Change++", "Change++", "engineering", 4, 8.0,
          is_selective=True, acceptance_rate=0.15, has_projects=True,
          description="Selective software development for nonprofits. Real-world projects."),
    _club("vanderbilt", "vandyapps", "VandyApps", "VandyApps", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          description="Mobile and web app development club. Ships real apps to the App Store."),
]

# ============= NOTRE DAME CLUBS =============
NOTRE_DAME_CLUBS: List[Dict] = _standard_clubs("notre_dame", "Notre Dame") + [
    _club("notre_dame", "irish_coders", "Irish Coders", "Irish Coders", "engineering", 3, 6.5,
          is_selective=True, has_projects=True,
          description="Collaborative coding projects and open-source contributions at Notre Dame."),
    _club("notre_dame", "nd_cyber", "Notre Dame Cyber Security Club", "CyberND", "engineering", 3, 7.0,
          has_competitions=True,
          description="Cybersecurity competitions, CTF events, and security research."),
]

# ============= BU CLUBS =============
BU_CLUBS: List[Dict] = _standard_clubs("bu", "BU") + [
    _club("bu", "spark", "BU Spark!", "Spark!", "engineering", 4, 7.5,
          is_selective=True, acceptance_rate=0.20, has_projects=True,
          description="BU's innovation and technology incubator. Real client projects for students."),
    _club("bu", "bu_blockchain", "BU Blockchain Club", "Blockchain", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "data_science"],
          description="Blockchain development, smart contracts, and Web3 workshops."),
]

# ============= TUFTS CLUBS =============
TUFTS_CLUBS: List[Dict] = _standard_clubs("tufts", "Tufts") + [
    _club("tufts", "jumbocode", "JumboCode", "JumboCode", "engineering", 4, 8.0,
          is_selective=True, acceptance_rate=0.15, has_projects=True,
          description="Selective software development for nonprofits. Semester-long team projects."),
    _club("tufts", "polyhack", "PolyHack", "PolyHack", "engineering", 3, 6.5,
          has_competitions=True,
          description="Tufts hackathon organization. Hosts annual events with 300+ participants."),
]

# ============= RPI CLUBS =============
RPI_CLUBS: List[Dict] = _standard_clubs("rpi", "RPI") + [
    _club("rpi", "rcos", "Rensselaer Center for Open Source", "RCOS", "engineering", 4, 8.0,
          is_selective=False, has_projects=True,
          description="RPI's flagship open-source development program. Students contribute to real projects for course credit."),
    _club("rpi", "rpi_sec", "RPISEC", "RPISEC", "engineering", 4, 7.5,
          is_selective=True, has_competitions=True,
          description="Competitive cybersecurity team. Top CTF performers nationally."),
]

# ============= CASE WESTERN CLUBS =============
CASE_WESTERN_CLUBS: List[Dict] = _standard_clubs("case_western", "Case Western") + [
    _club("case_western", "hacsoc", "Hacker Society", "HacSoc", "engineering", 3, 7.0,
          is_selective=False, has_projects=True, has_competitions=True,
          description="Case Western's hacker culture hub. Workshops, hackathons, and project nights."),
    _club("case_western", "cwru_vr", "CWRU VR Club", "VR Club", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Virtual and augmented reality development. Unity and Unreal Engine projects."),
]

# ============= PITT CLUBS =============
PITT_CLUBS: List[Dict] = _standard_clubs("pitt", "Pitt") + [
    _club("pitt", "csg", "Computer Science Club at Pitt", "CSC", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Pitt's main CS community. Workshops, study sessions, and career events."),
    _club("pitt", "steelhacks", "SteelHacks", "SteelHacks", "engineering", 3, 7.0,
          has_competitions=True,
          description="Pitt's annual hackathon. Pittsburgh-themed, beginner-friendly."),
]

# ============= UTAH CLUBS =============
UTAH_CLUBS: List[Dict] = _standard_clubs("utah", "Utah") + [
    _club("utah", "utah_gamedev", "Utah Game Dev Club", "GameDev", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Game development using Unity and Unreal. Annual game jams."),
    _club("utah", "uofu_app", "App Club Utah", "App Club", "engineering", 3, 6.5,
          has_projects=True, is_selective=True,
          description="iOS and Android app development. Ships apps each semester."),
]

# ============= IOWA STATE CLUBS =============
IOWA_STATE_CLUBS: List[Dict] = _standard_clubs("iowa_state", "Iowa State") + [
    _club("iowa_state", "cyber_defense", "Iowa State Cyber Defense Competition Team", "CDC", "engineering", 3, 7.0,
          is_selective=True, has_competitions=True,
          description="Competitive cybersecurity team. Competes in CCDC regionals and nationals."),
    _club("iowa_state", "digital_women", "Digital Women", "DigiWomen", "professional", 2, 5.5,
          is_selective=False, is_professional=True, is_technical=False,
          description="Empowering women in technology through networking and professional development."),
]

# ============= MICHIGAN STATE CLUBS =============
MICHIGAN_STATE_CLUBS: List[Dict] = _standard_clubs("michigan_state", "MSU") + [
    _club("michigan_state", "spartahack", "SpartaHack", "SpartaHack", "engineering", 3, 7.0,
          has_competitions=True,
          description="MSU's flagship hackathon. 600+ participants from across the Midwest."),
    _club("michigan_state", "msu_cloud", "MSU Cloud Computing Club", "Cloud Club", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "data_science"],
          description="AWS, GCP, and Azure workshops. Cloud architecture projects."),
]

# ============= UCF CLUBS =============
UCF_CLUBS: List[Dict] = _standard_clubs("ucf", "UCF") + [
    _club("ucf", "knighthacks", "KnightHacks", "KnightHacks", "engineering", 3, 7.0,
          has_competitions=True,
          description="UCF's premier hackathon organization. Largest in central Florida."),
    _club("ucf", "ucf_progteam", "UCF Programming Team", "ProgTeam", "engineering", 4, 8.0,
          is_selective=True, acceptance_rate=0.15, has_competitions=True,
          description="Competitive programming team. Strong ICPC performance nationally."),
]

# ============= GMU CLUBS =============
GMU_CLUBS: List[Dict] = _standard_clubs("gmu", "GMU") + [
    _club("gmu", "srct", "Student-Run Computing and Technology", "SRCT", "engineering", 3, 7.0,
          has_projects=True,
          description="Builds and maintains software tools used across the GMU campus."),
    _club("gmu", "gmu_cyber", "GMU Cybersecurity Club", "CyberGMU", "engineering", 3, 6.5,
          has_competitions=True,
          description="Cybersecurity workshops and CTF competitions. Close ties to DC industry."),
]

# ============= UCR CLUBS =============
UCR_CLUBS: List[Dict] = _standard_clubs("ucr", "UCR") + [
    _club("ucr", "acm_ucr", "ACM@UCR Projects Division", "ACM Projects", "engineering", 3, 6.5,
          has_projects=True,
          description="Hands-on project division of ACM. Team-based software development."),
    _club("ucr", "citrus_hack", "Citrus Hack", "CitrusHack", "engineering", 3, 6.5,
          has_competitions=True,
          description="UCR's annual beginner-friendly hackathon."),
]

# ============= RIT CLUBS =============
RIT_CLUBS: List[Dict] = _standard_clubs("rit", "RIT") + [
    _club("rit", "sse", "Society of Software Engineers", "SSE", "engineering", 3, 7.0,
          has_projects=True, is_selective=False,
          description="RIT's largest CS club. Mentorship, projects, and career development."),
    _club("rit", "ritsec", "RITSEC", "RITSEC", "engineering", 4, 7.5,
          has_competitions=True, is_selective=True,
          description="RIT's cybersecurity club. Top-ranked CTF team nationally."),
]

# ============= WPI CLUBS =============
WPI_CLUBS: List[Dict] = _standard_clubs("wpi", "WPI") + [
    _club("wpi", "gdsc_wpi", "Google Developer Student Club WPI", "GDSC", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Google-sponsored student tech community at WPI."),
    _club("wpi", "wpi_gamedev", "WPI Game Development Club", "GameDev", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Game development projects using custom engines and Unity. Strong project culture."),
]

# ============= DREXEL CLUBS =============
DREXEL_CLUBS: List[Dict] = _standard_clubs("drexel", "Drexel") + [
    _club("drexel", "dragonhacks", "DragonHacks", "DragonHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="Drexel's annual hackathon. Co-op focused networking opportunities."),
    _club("drexel", "drexel_oss", "Drexel Open Source", "OSS", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Open-source software development and contributions."),
]

# ============= STEVENS CLUBS =============
STEVENS_CLUBS: List[Dict] = _standard_clubs("stevens", "Stevens") + [
    _club("stevens", "sit_cybersec", "Stevens Cybersecurity Club", "CyberSec", "engineering", 3, 7.0,
          has_competitions=True,
          description="Cybersecurity research and CTF competitions."),
    _club("stevens", "ducktype", "DuckType", "DuckType", "engineering", 3, 6.5,
          has_projects=True,
          description="Stevens web and mobile development club. Full-stack project teams."),
]

# ============= NJIT CLUBS =============
NJIT_CLUBS: List[Dict] = _standard_clubs("njit", "NJIT") + [
    _club("njit", "njit_webdev", "NJIT Web Dev Club", "WebDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Web development workshops and collaborative projects."),
    _club("njit", "hacknjit", "HackNJIT", "HackNJIT", "engineering", 3, 6.5,
          has_competitions=True,
          description="NJIT's annual hackathon. Brings together students from the tri-state area."),
]

# ============= OREGON STATE CLUBS =============
OREGON_STATE_CLUBS: List[Dict] = _standard_clubs("oregon_state", "Oregon State") + [
    _club("oregon_state", "osuosc", "OSU Open Source Club", "OSC", "engineering", 3, 6.5,
          has_projects=True, is_selective=False,
          description="Open-source development and Linux advocacy at Oregon State."),
    _club("oregon_state", "beaverhacks", "BeaverHacks", "BeaverHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="Oregon State's student hackathon. Quarterly themed events."),
]

# ============= BUFFALO CLUBS =============
BUFFALO_CLUBS: List[Dict] = _standard_clubs("buffalo", "UB") + [
    _club("buffalo", "ubhacking", "UBhacking", "UBhacking", "engineering", 3, 6.5,
          has_competitions=True,
          description="UB's annual hackathon event attracting 400+ students."),
    _club("buffalo", "ub_acm_cp", "UB Competitive Programming", "CompProg", "engineering", 3, 7.0,
          is_selective=True, has_competitions=True,
          description="Competitive programming training and ICPC preparation."),
]

# ============= UTD CLUBS =============
UTD_CLUBS: List[Dict] = _standard_clubs("utd", "UTD") + [
    _club("utd", "acm_utd_projects", "ACM Projects UTD", "ACM Projects", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          description="Selective project division of ACM UTD. Semester-long team projects."),
    _club("utd", "artificial_intelligence_society", "Artificial Intelligence Society", "AIS", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          relevant_to=["machine_learning", "data_science", "software_engineering"],
          description="UTD's AI/ML club. Research projects, workshops, and industry talks."),
]

# ============= UIC CLUBS =============
UIC_CLUBS: List[Dict] = _standard_clubs("uic", "UIC") + [
    _club("uic", "uic_gamedev", "UIC Game Developers", "GameDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Game development using Unity and Godot. Semester game jams."),
    _club("uic", "sparkshack", "SparksHack", "SparksHack", "engineering", 3, 6.5,
          has_competitions=True,
          description="UIC's student-run hackathon focused on Chicago community impact."),
]

# ============= CLEMSON CLUBS =============
CLEMSON_CLUBS: List[Dict] = _standard_clubs("clemson", "Clemson") + [
    _club("clemson", "cucoders", "CU Coders", "CU Coders", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Clemson's coding community. Weekly coding challenges and project showcases."),
    _club("clemson", "clemson_cyber", "Clemson Cyber Security", "CyberTigers", "engineering", 3, 7.0,
          has_competitions=True,
          description="Cybersecurity competitions and capture-the-flag events."),
]

# ============= SYRACUSE CLUBS =============
SYRACUSE_CLUBS: List[Dict] = _standard_clubs("syracuse", "Syracuse") + [
    _club("syracuse", "cuse_hacks", "CuseHacks", "CuseHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="Syracuse University's annual hackathon. 300+ participants."),
    _club("syracuse", "orangeapps", "OrangeApps", "OrangeApps", "engineering", 3, 6.5,
          is_selective=True, has_projects=True,
          description="Mobile app development club. Ships iOS and Android apps for the Syracuse community."),
]

# ============= LEHIGH CLUBS =============
LEHIGH_CLUBS: List[Dict] = _standard_clubs("lehigh", "Lehigh") + [
    _club("lehigh", "lehigh_blockchain", "Lehigh Blockchain Club", "Blockchain", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "data_science"],
          description="Blockchain development, DeFi research, and smart contract workshops."),
    _club("lehigh", "lehigh_design_tech", "Design & Tech Lab", "DTL", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Intersection of design and technology. UX research and prototyping."),
]

# ============= BRANDEIS CLUBS =============
BRANDEIS_CLUBS: List[Dict] = _standard_clubs("brandeis", "Brandeis") + [
    _club("brandeis", "deis_hacks", "DeisHacks", "DeisHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="Brandeis's annual hackathon with a social justice focus."),
    _club("brandeis", "brandeis_webdev", "Brandeis Web Development Club", "WebDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Web development workshops and collaborative site-building projects."),
]

# ============= UCONN CLUBS =============
UCONN_CLUBS: List[Dict] = _standard_clubs("uconn", "UConn") + [
    _club("uconn", "hackuconn", "HackUConn", "HackUConn", "engineering", 3, 6.5,
          has_competitions=True,
          description="UConn's annual hackathon. 500+ participants from the Northeast."),
    _club("uconn", "uconn_cyber", "UConn Cybersecurity Club", "CyberHuskies", "engineering", 3, 7.0,
          has_competitions=True,
          description="Cybersecurity competitions and digital forensics workshops."),
]

# ============= IOWA CLUBS =============
IOWA_CLUBS: List[Dict] = _standard_clubs("iowa", "Iowa") + [
    _club("iowa", "hackhawks", "HackHawks", "HackHawks", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Iowa's student hackathon organization."),
    _club("iowa", "iowa_gamedev", "Iowa Game Dev Club", "GameDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Game development workshops and game jams using Unity and Godot."),
]

# ============= USF CLUBS =============
USF_CLUBS: List[Dict] = _standard_clubs("usf", "USF") + [
    _club("usf", "bullshacks", "BullsHacks", "BullsHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="USF's annual hackathon. Tampa Bay's largest student hack event."),
    _club("usf", "usf_ossd", "USF Open Source Development", "OSSD", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Open-source contributions and collaborative coding projects."),
]

# ============= TEMPLE CLUBS =============
TEMPLE_CLUBS: List[Dict] = _standard_clubs("temple", "Temple") + [
    _club("temple", "tudev", "TUDev", "TUDev", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          description="Temple's student developer community. Builds apps and tools for the campus."),
    _club("temple", "owlhacks", "OwlHacks", "OwlHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="Temple's annual hackathon. Philadelphia-area students and sponsors."),
]

# ============= GWU CLUBS =============
GWU_CLUBS: List[Dict] = _standard_clubs("gwu", "GWU") + [
    _club("gwu", "gwu_appdev", "GW App Development", "GW AppDev", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          description="Mobile and web app development. Ships products each semester."),
    _club("gwu", "gwu_cyber", "GW Cyber Security Club", "CyberGW", "engineering", 3, 7.0,
          has_competitions=True,
          description="Cybersecurity competitions and policy workshops. Leverages DC location."),
]

# ============= TULANE CLUBS =============
TULANE_CLUBS: List[Dict] = _standard_clubs("tulane", "Tulane") + [
    _club("tulane", "greenwave_code", "Green Wave Code", "GW Code", "engineering", 3, 6.5,
          is_selective=True, has_projects=True,
          description="Software development for New Orleans community nonprofits."),
    _club("tulane", "tulane_datasci", "Tulane Data Science Society", "TDSS", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["data_science", "machine_learning"],
          description="Data science projects and Kaggle competitions."),
]

# ============= GEORGETOWN CLUBS =============
GEORGETOWN_CLUBS: List[Dict] = _standard_clubs("georgetown", "Georgetown") + [
    _club("georgetown", "gtown_disrupt", "Georgetown Disruptive Tech", "GDisrupt", "engineering", 4, 7.5,
          is_selective=True, acceptance_rate=0.15, has_projects=True,
          relevant_to=["software_engineering", "product_management"],
          description="Selective tech innovation club. Builds products at the intersection of tech and policy."),
    _club("georgetown", "gtown_crypto", "Georgetown Blockchain Club", "Blockchain", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "data_science"],
          description="Blockchain and cryptocurrency research. Smart contract development."),
]

# ============= SANTA CLARA CLUBS =============
SANTA_CLARA_CLUBS: List[Dict] = _standard_clubs("santa_clara", "Santa Clara") + [
    _club("santa_clara", "acm_sc_dev", "ACM Dev Team SCU", "ACM Dev", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          description="ACM's project division at SCU. Builds apps with Silicon Valley mentors."),
    _club("santa_clara", "scu_frugal", "Frugal Innovation Hub", "Frugal Hub", "engineering", 4, 7.5,
          is_selective=True, acceptance_rate=0.20, has_projects=True,
          relevant_to=["software_engineering", "product_management"],
          description="Social impact tech lab. Develops affordable technology solutions for developing communities."),
]

# ============= MISSOURI CLUBS =============
MISSOURI_CLUBS: List[Dict] = _standard_clubs("missouri", "Mizzou") + [
    _club("missouri", "tigerhacks", "TigerHacks", "TigerHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="Mizzou's annual hackathon. Midwest-focused with strong sponsor support."),
    _club("missouri", "mizzou_webdev", "Mizzou Web Dev", "WebDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Web development workshops and collaborative projects."),
]

# ============= TENNESSEE CLUBS =============
TENNESSEE_CLUBS: List[Dict] = _standard_clubs("tennessee", "Tennessee") + [
    _club("tennessee", "volhacks", "VolHacks", "VolHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Tennessee's annual hackathon."),
    _club("tennessee", "utk_eecs_council", "EECS Student Council", "EECS Council", "professional", 2, 5.5,
          is_selective=False, is_professional=True, is_technical=False,
          description="Student government for EECS. Career fairs and networking events."),
]

# ============= NEBRASKA CLUBS =============
NEBRASKA_CLUBS: List[Dict] = _standard_clubs("nebraska", "Nebraska") + [
    _club("nebraska", "cornhacks", "CornHacks", "CornHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="Nebraska's annual hackathon. 24-hour build event."),
    _club("nebraska", "unl_raik", "RAIK Student Advisory Board", "RAIK", "professional", 3, 7.0,
          is_selective=True, is_professional=True, has_projects=True,
          relevant_to=["software_engineering", "product_management"],
          description="Jeffrey S. Raikes School advisory board. Entrepreneurship and tech leadership."),
]

# ============= AUBURN CLUBS =============
AUBURN_CLUBS: List[Dict] = _standard_clubs("auburn", "Auburn") + [
    _club("auburn", "auhack", "AUHack", "AUHack", "engineering", 3, 6.5,
          has_competitions=True,
          description="Auburn University's annual hackathon."),
    _club("auburn", "auburn_gamedev", "Auburn Game Dev", "GameDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Game design and development club. Unreal Engine and Unity projects."),
]

# ============= SMU CLUBS =============
SMU_CLUBS: List[Dict] = _standard_clubs("smu", "SMU") + [
    _club("smu", "hacking_smu", "HackSMU", "HackSMU", "engineering", 3, 7.0,
          has_competitions=True,
          description="SMU's annual hackathon. Dallas tech industry sponsors."),
    _club("smu", "smu_vr", "SMU VR/AR Club", "VR Club", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Virtual and augmented reality development and research."),
]

# ============= COLORADO STATE CLUBS =============
COLORADO_STATE_CLUBS: List[Dict] = _standard_clubs("colorado_state", "CSU") + [
    _club("colorado_state", "ramhacks", "RamHacks", "RamHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="CSU's student-run hackathon. 24-hour build-a-thon."),
    _club("colorado_state", "csu_linux", "CSU Linux Users Group", "LUG", "engineering", 2, 5.5,
          is_selective=False, has_projects=True,
          description="Open source advocacy and Linux system administration."),
]

# ============= UOREGON CLUBS =============
UOREGON_CLUBS: List[Dict] = _standard_clubs("uoregon", "Oregon") + [
    _club("uoregon", "uo_product", "Oregon Product Lab", "Product Lab", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          relevant_to=["software_engineering", "product_management", "product_design"],
          description="Product development lab. Design, build, and ship real products."),
    _club("uoregon", "quackhacks", "QuackHacks", "QuackHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Oregon's annual hackathon."),
]

# ============= KANSAS CLUBS =============
KANSAS_CLUBS: List[Dict] = _standard_clubs("kansas", "Kansas") + [
    _club("kansas", "hackku", "HackKU", "HackKU", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Kansas's annual hackathon."),
    _club("kansas", "ku_cloud", "KU Cloud Computing Club", "Cloud Club", "engineering", 3, 6.5,
          has_projects=True,
          relevant_to=["software_engineering", "data_science"],
          description="AWS and cloud architecture workshops. Certification study groups."),
]

# ============= BINGHAMTON CLUBS =============
BINGHAMTON_CLUBS: List[Dict] = _standard_clubs("binghamton", "Binghamton") + [
    _club("binghamton", "hackbu", "HackBU", "HackBU", "engineering", 3, 6.5,
          has_competitions=True,
          description="Binghamton's annual hackathon. 400+ participants."),
    _club("binghamton", "buosc", "Binghamton Open Source Club", "BOSC", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Open-source contributions and collaborative development."),
]

# ============= DELAWARE CLUBS =============
DELAWARE_CLUBS: List[Dict] = _standard_clubs("delaware", "Delaware") + [
    _club("delaware", "ud_gamedev", "Blue Hen Game Dev", "GameDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          relevant_to=["software_engineering", "product_design"],
          description="Game development club. Unity workshops and semester game jams."),
    _club("delaware", "henhacks", "HenHacks", "HenHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Delaware's annual hackathon."),
]

# ============= MIAMI CLUBS =============
MIAMI_CLUBS: List[Dict] = _standard_clubs("miami", "Miami") + [
    _club("miami", "hacktheU", "HackTheU", "HackTheU", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Miami's annual hackathon. South Florida's premier student hack event."),
    _club("miami", "miami_appdev", "Canes App Dev", "CanesApp", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          description="Mobile app development for the Miami community. Ships apps to iOS and Android."),
]

# ============= ALABAMA CLUBS =============
ALABAMA_CLUBS: List[Dict] = _standard_clubs("alabama", "Alabama") + [
    _club("alabama", "hackabama", "HackAlabama", "HackAlabama", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Alabama's annual hackathon."),
    _club("alabama", "bama_webdev", "Alabama Web Developers", "WebDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Web development projects and workshops. Full-stack focus."),
]

# ============= UKY CLUBS =============
UKY_CLUBS: List[Dict] = _standard_clubs("uky", "Kentucky") + [
    _club("uky", "wildcathacks", "WildcatHacks", "WildcatHacks", "engineering", 3, 6.5,
          has_competitions=True,
          description="University of Kentucky's annual hackathon."),
    _club("uky", "uky_appdev", "UK App Development Club", "AppDev", "engineering", 3, 6.5,
          is_selective=True, has_projects=True,
          description="iOS and Android app development. Builds tools for the UK campus."),
]

# ============= W&M CLUBS =============
WM_CLUBS: List[Dict] = _standard_clubs("wm", "W&M") + [
    _club("wm", "cypher", "Cypher", "Cypher", "engineering", 3, 7.0,
          is_selective=True, has_projects=True,
          description="W&M's selective CS project club. Full-stack team projects each semester."),
    _club("wm", "wm_cyber", "W&M Cybersecurity Club", "CyberW&M", "engineering", 3, 6.5,
          has_competitions=True,
          description="Cybersecurity competitions and CTF practice."),
]

# ============= LSU CLUBS =============
LSU_CLUBS: List[Dict] = _standard_clubs("lsu", "LSU") + [
    _club("lsu", "geauxhack", "GeauxHack", "GeauxHack", "engineering", 3, 6.5,
          has_competitions=True,
          description="LSU's annual hackathon. Louisiana's largest student hack event."),
    _club("lsu", "lsu_webdev", "LSU Web Dev Club", "WebDev", "engineering", 2, 6.0,
          is_selective=False, has_projects=True,
          description="Web development workshops and collaborative projects."),
]


def get_extended_clubs3() -> List[Dict]:
    """Get all clubs from the third batch of extended universities."""
    return (
        VANDERBILT_CLUBS + NOTRE_DAME_CLUBS + BU_CLUBS + TUFTS_CLUBS + RPI_CLUBS
        + CASE_WESTERN_CLUBS + PITT_CLUBS + UTAH_CLUBS + IOWA_STATE_CLUBS
        + MICHIGAN_STATE_CLUBS + UCF_CLUBS + GMU_CLUBS + UCR_CLUBS + RIT_CLUBS
        + WPI_CLUBS + DREXEL_CLUBS + STEVENS_CLUBS + NJIT_CLUBS
        + OREGON_STATE_CLUBS + BUFFALO_CLUBS + UTD_CLUBS + UIC_CLUBS
        + CLEMSON_CLUBS + SYRACUSE_CLUBS + LEHIGH_CLUBS + BRANDEIS_CLUBS
        + UCONN_CLUBS + IOWA_CLUBS + USF_CLUBS + TEMPLE_CLUBS
        + GWU_CLUBS + TULANE_CLUBS + GEORGETOWN_CLUBS + SANTA_CLARA_CLUBS
        + MISSOURI_CLUBS + TENNESSEE_CLUBS + NEBRASKA_CLUBS + AUBURN_CLUBS
        + SMU_CLUBS + COLORADO_STATE_CLUBS + UOREGON_CLUBS + KANSAS_CLUBS
        + BINGHAMTON_CLUBS + DELAWARE_CLUBS + MIAMI_CLUBS + ALABAMA_CLUBS
        + UKY_CLUBS + WM_CLUBS + LSU_CLUBS
    )
