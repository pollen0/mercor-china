"""
Extended seed data for courses at 29 additional universities (batch 2).
Schools: USC, Duke, Northwestern, Rice, NYU, UC Davis, UC Irvine, Ohio State,
Penn State, Virginia Tech, UVA, Brown, Yale, Johns Hopkins, NC State, UNC,
UMN, Stony Brook, Rutgers, ASU, UF, Northeastern, CU Boulder, Indiana,
UMass, TAMU, Rochester, Dartmouth, WashU.
"""

from typing import List, Dict


def _cs(uid, num, name, diff_tier, diff_score, gpa, ctype="core", **kw):
    """Helper to create a course dict with defaults."""
    c = {
        "id": f"{uid}_cs{num}",
        "university_id": uid,
        "department": kw.pop("dept", "CS"),
        "number": str(num),
        "name": name,
        "aliases": [f"CS {num}", f"CS{num}"],
        "difficulty_tier": diff_tier,
        "difficulty_score": diff_score,
        "typical_gpa": gpa,
        "is_curved": kw.pop("is_curved", True),
        "course_type": ctype,
        "is_technical": True,
        "has_coding": kw.pop("has_coding", True),
        "units": kw.pop("units", 3),
        "relevant_to": kw.pop("relevant_to", ["software_engineer"]),
        "description": kw.pop("description", name),
        "confidence": 0.85,
        "source": "research",
    }
    c.update(kw)
    return c


# ============= UCSC COURSES =============
UCSC_COURSES: List[Dict] = [
    _cs("ucsc", "12A", "Introduction to Programming", 2, 4.0, 3.2, "core", dept="CSE", units=5, is_weeder=True),
    _cs("ucsc", "12B", "Data Structures", 3, 6.0, 3.0, "core", dept="CSE", units=5),
    _cs("ucsc", "101", "Algorithms and Abstract Data Types", 4, 7.5, 2.9, "core", dept="CSE"),
    _cs("ucsc", "120", "Computer Architecture", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("ucsc", "111", "Operating Systems", 4, 7.0, 3.0, "core", dept="CSE", has_heavy_projects=True),
    _cs("ucsc", "115", "Introduction to Computer Networks", 3, 6.0, 3.1, "elective", dept="CSE", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("ucsc", "142", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= USC COURSES =============
USC_COURSES: List[Dict] = [
    _cs("usc", "104", "Fundamentals of Computer Programming", 2, 4.5, 3.2, "core", is_weeder=True, units=4, relevant_to=["software_engineer", "data_scientist"]),
    _cs("usc", "170", "Discrete Methods in Computer Science", 3, 6.0, 3.0, "core", is_proof_based=True, has_coding=False),
    _cs("usc", "201", "Principles of Software Development", 3, 6.5, 3.1, "core", has_heavy_projects=True, units=4),
    _cs("usc", "270", "Introduction to Algorithms and Theory of Computing", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("usc", "310", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", units=4),
    _cs("usc", "356", "Introduction to Computer Networks", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("usc", "467", "Introduction to Machine Learning", 4, 7.5, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= DUKE COURSES =============
DUKE_COURSES: List[Dict] = [
    _cs("duke", "101", "Introduction to Computer Science", 2, 4.0, 3.3, "core", dept="COMPSCI", units=4, is_weeder=True),
    _cs("duke", "201", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", dept="COMPSCI", units=4),
    _cs("duke", "210", "Introduction to Computer Architecture", 3, 6.0, 3.1, "core", dept="COMPSCI"),
    _cs("duke", "250", "Computer Architecture", 3, 6.5, 3.0, "core", dept="COMPSCI"),
    _cs("duke", "310", "Introduction to Operating Systems", 4, 7.5, 2.9, "core", dept="COMPSCI", has_heavy_projects=True),
    _cs("duke", "316", "Introduction to Database Systems", 3, 6.0, 3.1, "elective", dept="COMPSCI", relevant_to=["software_engineer", "data_engineer"]),
    _cs("duke", "371", "Elements of Machine Learning", 4, 7.0, 3.0, "elective", dept="COMPSCI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= NORTHWESTERN COURSES =============
NORTHWESTERN_COURSES: List[Dict] = [
    _cs("northwestern", "111", "Fundamentals of Computer Programming I", 2, 4.0, 3.3, "core", units=4),
    _cs("northwestern", "211", "Fundamentals of Computer Programming II", 3, 6.0, 3.1, "core", units=4),
    _cs("northwestern", "213", "Intro to Computer Systems", 4, 7.0, 2.9, "core"),
    _cs("northwestern", "214", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("northwestern", "321", "Programming Languages", 3, 6.5, 3.1, "elective"),
    _cs("northwestern", "340", "Introduction to Networking", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("northwestern", "349", "Machine Learning", 4, 7.5, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= RICE COURSES =============
RICE_COURSES: List[Dict] = [
    _cs("rice", "140", "Computational Thinking", 2, 4.0, 3.3, "core", dept="COMP", units=4),
    _cs("rice", "182", "Algorithmic Thinking", 3, 6.0, 3.1, "core", dept="COMP"),
    _cs("rice", "215", "Introduction to Program Design", 3, 6.5, 3.0, "core", dept="COMP", units=4),
    _cs("rice", "310", "Advanced Object-Oriented Programming", 3, 6.5, 3.0, "core", dept="COMP", has_heavy_projects=True),
    _cs("rice", "382", "Introduction to Algorithms", 4, 7.5, 2.9, "core", dept="COMP", is_proof_based=True),
    _cs("rice", "412", "Cloud Computing", 3, 6.5, 3.1, "elective", dept="COMP", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("rice", "435", "Machine Learning", 4, 7.0, 3.0, "elective", dept="COMP", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= NYU COURSES =============
NYU_COURSES: List[Dict] = [
    _cs("nyu", "101", "Introduction to Computer Science", 2, 4.0, 3.3, "core", dept="CSCI-UA", units=4, is_weeder=True),
    _cs("nyu", "102", "Data Structures", 3, 6.5, 3.0, "core", dept="CSCI-UA", units=4),
    _cs("nyu", "201", "Computer Systems Organization", 3, 6.5, 3.0, "core", dept="CSCI-UA"),
    _cs("nyu", "202", "Operating Systems", 4, 7.5, 2.9, "core", dept="CSCI-UA", has_heavy_projects=True),
    _cs("nyu", "310", "Basic Algorithms", 4, 7.5, 2.8, "core", dept="CSCI-UA", is_proof_based=True),
    _cs("nyu", "473", "Fundamentals of Machine Learning", 4, 7.0, 3.0, "elective", dept="CSCI-UA", relevant_to=["ml_engineer", "data_scientist"]),
    _cs("nyu", "480", "Parallel Computing", 4, 7.0, 3.0, "elective", dept="CSCI-UA"),
]

# ============= UC DAVIS COURSES =============
UC_DAVIS_COURSES: List[Dict] = [
    _cs("uc_davis", "36A", "Programming & Problem Solving", 2, 4.0, 3.2, "core", dept="ECS", units=4, is_weeder=True),
    _cs("uc_davis", "36B", "Software Development & OOP", 3, 5.5, 3.1, "core", dept="ECS", units=4),
    _cs("uc_davis", "36C", "Data Structures", 3, 6.5, 3.0, "core", dept="ECS", units=4),
    _cs("uc_davis", "122A", "Algorithm Design and Analysis", 4, 7.5, 2.9, "core", dept="ECS"),
    _cs("uc_davis", "150", "Operating Systems", 4, 7.0, 3.0, "core", dept="ECS", has_heavy_projects=True),
    _cs("uc_davis", "170", "Computer Architecture", 3, 6.5, 3.0, "core", dept="ECS"),
    _cs("uc_davis", "171", "Machine Learning", 4, 7.0, 3.0, "elective", dept="ECS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UC IRVINE COURSES =============
UC_IRVINE_COURSES: List[Dict] = [
    _cs("uc_irvine", "45C", "Programming in C/C++", 2, 5.0, 3.1, "core", dept="ICS", units=4),
    _cs("uc_irvine", "46", "Data Structure Implementation", 3, 6.5, 3.0, "core", dept="ICS", units=4),
    _cs("uc_irvine", "51", "Introductory Computer Organization", 3, 6.0, 3.0, "core", dept="ICS"),
    _cs("uc_irvine", "53", "Principles in System Design", 3, 6.5, 3.0, "core", dept="ICS"),
    _cs("uc_irvine", "161", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="ICS", is_proof_based=True),
    _cs("uc_irvine", "143A", "Operating Systems", 4, 7.0, 3.0, "core", dept="ICS", has_heavy_projects=True),
    _cs("uc_irvine", "175", "Project in AI", 4, 7.0, 3.1, "elective", dept="ICS", relevant_to=["ml_engineer", "data_scientist"], has_heavy_projects=True),
]

# ============= OHIO STATE COURSES =============
OHIO_STATE_COURSES: List[Dict] = [
    _cs("ohio_state", "2221", "Software Development and Design", 2, 5.0, 3.1, "core", dept="CSE", units=4, is_weeder=True),
    _cs("ohio_state", "2231", "Software II: Development and Design", 3, 6.5, 3.0, "core", dept="CSE", units=4),
    _cs("ohio_state", "2321", "Discrete Structures", 3, 6.0, 3.0, "core", dept="CSE", is_proof_based=True, has_coding=False),
    _cs("ohio_state", "2421", "Systems I: Low-Level Programming", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("ohio_state", "3341", "Principles of Programming Languages", 3, 6.0, 3.1, "core", dept="CSE"),
    _cs("ohio_state", "3430", "Overview of Computer Systems", 4, 7.0, 2.9, "core", dept="CSE"),
    _cs("ohio_state", "5523", "Machine Learning and Statistical Pattern Recognition", 4, 7.5, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= PENN STATE COURSES =============
PENN_STATE_COURSES: List[Dict] = [
    _cs("penn_state", "121", "Introduction to Programming", 2, 4.0, 3.2, "core", dept="CMPSC", units=4, is_weeder=True),
    _cs("penn_state", "122", "Intermediate Programming", 3, 5.5, 3.1, "core", dept="CMPSC"),
    _cs("penn_state", "221", "Object Oriented Programming with Web", 3, 6.0, 3.1, "core", dept="CMPSC"),
    _cs("penn_state", "360", "Programming Language Concepts", 3, 6.5, 3.0, "core", dept="CMPSC"),
    _cs("penn_state", "311", "Algorithms and Data Structures", 4, 7.0, 2.9, "core", dept="CMPSC"),
    _cs("penn_state", "431", "Operating Systems", 4, 7.0, 3.0, "core", dept="CMPSC", has_heavy_projects=True),
    _cs("penn_state", "448", "Machine Learning and AI", 4, 7.0, 3.0, "elective", dept="CMPSC", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= VIRGINIA TECH COURSES =============
VIRGINIA_TECH_COURSES: List[Dict] = [
    _cs("virginia_tech", "1114", "Introduction to Software Design", 2, 4.5, 3.2, "core", units=4, is_weeder=True),
    _cs("virginia_tech", "2114", "Software Design and Data Structures", 3, 6.5, 3.0, "core", units=4),
    _cs("virginia_tech", "2505", "Introduction to Computer Organization", 3, 6.0, 3.0, "core"),
    _cs("virginia_tech", "3114", "Data Structures and Algorithms", 3, 6.5, 3.0, "core"),
    _cs("virginia_tech", "3214", "Computer Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("virginia_tech", "4104", "Data and Algorithm Analysis", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("virginia_tech", "4804", "Introduction to Artificial Intelligence", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UVA COURSES =============
UVA_COURSES: List[Dict] = [
    _cs("uva", "1110", "Introduction to Programming", 2, 4.0, 3.3, "core", units=4, is_weeder=True),
    _cs("uva", "2100", "Data Structures and Algorithms 1", 3, 6.0, 3.0, "core", units=4),
    _cs("uva", "2130", "Computer Systems and Organization 1", 3, 6.5, 3.0, "core"),
    _cs("uva", "3100", "Data Structures and Algorithms 2", 4, 7.0, 2.9, "core", is_proof_based=True),
    _cs("uva", "3130", "Computer Systems and Organization 2", 4, 7.0, 3.0, "core", has_heavy_projects=True),
    _cs("uva", "3240", "Advanced Software Development", 3, 6.5, 3.1, "elective", has_heavy_projects=True),
    _cs("uva", "4774", "Machine Learning", 4, 7.5, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= BROWN COURSES =============
BROWN_COURSES: List[Dict] = [
    _cs("brown", "15", "Introduction to Object-Oriented Programming", 2, 4.5, 3.3, "core", units=4),
    _cs("brown", "18", "Introduction to Discrete Structures", 3, 6.0, 3.1, "core", is_proof_based=True, has_coding=False),
    _cs("brown", "33", "Introduction to Computer Systems", 4, 7.5, 2.9, "core", has_heavy_projects=True),
    _cs("brown", "200", "Data Structures and Algorithms", 3, 6.5, 3.0, "core"),
    _cs("brown", "1410", "Artificial Intelligence", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer"]),
    _cs("brown", "1420", "Machine Learning", 4, 7.5, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
    _cs("brown", "1680", "Systems Design", 4, 7.0, 3.0, "elective", has_heavy_projects=True),
]

# ============= YALE COURSES =============
YALE_COURSES: List[Dict] = [
    _cs("yale", "201", "Introduction to Computer Science", 2, 4.5, 3.3, "core", dept="CPSC", units=4, is_weeder=True),
    _cs("yale", "202", "Mathematical Tools for Computer Science", 3, 6.0, 3.0, "core", dept="CPSC", is_proof_based=True),
    _cs("yale", "223", "Data Structures and Programming Techniques", 3, 6.5, 3.0, "core", dept="CPSC"),
    _cs("yale", "323", "Introduction to Systems Programming", 4, 7.5, 2.9, "core", dept="CPSC", has_heavy_projects=True),
    _cs("yale", "365", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CPSC", is_proof_based=True),
    _cs("yale", "470", "Artificial Intelligence", 4, 7.0, 3.0, "elective", dept="CPSC", relevant_to=["ml_engineer"]),
    _cs("yale", "474", "Computational Intelligence for Games", 3, 6.0, 3.2, "elective", dept="CPSC"),
]

# ============= JOHNS HOPKINS COURSES =============
JOHNS_HOPKINS_COURSES: List[Dict] = [
    _cs("johns_hopkins", "120", "Intermediate Programming", 2, 5.0, 3.1, "core", units=4, is_weeder=True),
    _cs("johns_hopkins", "220", "Data Structures", 3, 6.5, 3.0, "core", units=4),
    _cs("johns_hopkins", "226", "Data Structures (Honors)", 4, 8.0, 2.8, "core"),
    _cs("johns_hopkins", "229", "Computer System Fundamentals", 4, 7.5, 2.9, "core"),
    _cs("johns_hopkins", "601.226", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("johns_hopkins", "433", "Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("johns_hopkins", "475", "Machine Learning", 4, 7.5, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= NC STATE COURSES =============
NC_STATE_COURSES: List[Dict] = [
    _cs("nc_state", "116", "Introduction to Computing - Java", 2, 4.0, 3.2, "core", dept="CSC", units=4, is_weeder=True),
    _cs("nc_state", "216", "Programming Concepts - Java", 3, 5.5, 3.1, "core", dept="CSC"),
    _cs("nc_state", "230", "Data Structures", 3, 6.5, 3.0, "core", dept="CSC"),
    _cs("nc_state", "316", "Software Engineering", 3, 6.0, 3.1, "core", dept="CSC", has_heavy_projects=True),
    _cs("nc_state", "333", "Algorithms and Data Structures", 4, 7.0, 2.9, "core", dept="CSC"),
    _cs("nc_state", "246", "Operating Systems", 4, 7.0, 3.0, "core", dept="CSC"),
    _cs("nc_state", "422", "Automated Learning and Data Analysis", 4, 7.0, 3.0, "elective", dept="CSC", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UNC COURSES =============
UNC_COURSES: List[Dict] = [
    _cs("unc", "110", "Introduction to Programming", 2, 4.0, 3.3, "core", dept="COMP", units=4),
    _cs("unc", "210", "Data Structures and Analysis", 3, 6.0, 3.0, "core", dept="COMP", units=4),
    _cs("unc", "211", "Systems Fundamentals", 3, 6.5, 3.0, "core", dept="COMP"),
    _cs("unc", "283", "Discrete Structures", 3, 6.0, 3.0, "core", dept="COMP", is_proof_based=True, has_coding=False),
    _cs("unc", "311", "Algorithms", 4, 7.5, 2.9, "core", dept="COMP", is_proof_based=True),
    _cs("unc", "431", "Internet Services and Protocols", 3, 6.0, 3.1, "elective", dept="COMP"),
    _cs("unc", "562", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="COMP", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UMN COURSES =============
UMN_COURSES: List[Dict] = [
    _cs("umn", "1133", "Introduction to Computing", 2, 4.0, 3.2, "core", dept="CSCI", units=4),
    _cs("umn", "2011", "Discrete Structures", 3, 6.0, 3.0, "core", dept="CSCI", is_proof_based=True),
    _cs("umn", "2021", "Machine Architecture", 3, 6.5, 3.0, "core", dept="CSCI"),
    _cs("umn", "2041", "Advanced Programming Principles", 3, 6.5, 3.0, "core", dept="CSCI"),
    _cs("umn", "4041", "Algorithms and Data Structures", 4, 7.0, 2.9, "core", dept="CSCI"),
    _cs("umn", "4061", "Introduction to Operating Systems", 4, 7.0, 3.0, "core", dept="CSCI", has_heavy_projects=True),
    _cs("umn", "5521", "Introduction to Machine Learning", 4, 7.5, 3.0, "elective", dept="CSCI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= STONY BROOK COURSES =============
STONY_BROOK_COURSES: List[Dict] = [
    _cs("stony_brook", "114", "Computer Science I", 2, 4.0, 3.2, "core", dept="CSE", units=4, is_weeder=True),
    _cs("stony_brook", "214", "Computer Science II", 3, 6.0, 3.0, "core", dept="CSE", units=4),
    _cs("stony_brook", "220", "Data Structures", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("stony_brook", "320", "Systems Fundamentals I", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("stony_brook", "373", "Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSE", is_proof_based=True),
    _cs("stony_brook", "356", "Operating Systems", 4, 7.0, 3.0, "core", dept="CSE", has_heavy_projects=True),
    _cs("stony_brook", "512", "Machine Learning", 4, 7.5, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= RUTGERS COURSES =============
RUTGERS_COURSES: List[Dict] = [
    _cs("rutgers", "111", "Introduction to Computer Science", 2, 4.5, 3.1, "core", units=4, is_weeder=True),
    _cs("rutgers", "112", "Data Structures", 3, 6.5, 3.0, "core", units=4),
    _cs("rutgers", "205", "Introduction to Discrete Structures I", 3, 6.0, 3.0, "core", is_proof_based=True),
    _cs("rutgers", "211", "Computer Architecture", 3, 6.5, 3.0, "core"),
    _cs("rutgers", "344", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("rutgers", "416", "Operating Systems Design", 4, 7.0, 3.0, "core", has_heavy_projects=True),
    _cs("rutgers", "461", "Machine Learning Principles", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= ASU COURSES =============
ASU_COURSES: List[Dict] = [
    _cs("asu", "110", "Principles of Programming", 2, 4.0, 3.2, "core", dept="CSE", units=4),
    _cs("asu", "205", "Object-Oriented Programming and Data Structures", 3, 6.0, 3.0, "core", dept="CSE", units=4),
    _cs("asu", "230", "Computer Organization", 3, 6.0, 3.0, "core", dept="CSE"),
    _cs("asu", "310", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("asu", "340", "Operating Systems", 4, 7.0, 3.0, "core", dept="CSE", has_heavy_projects=True),
    _cs("asu", "355", "Introduction to Theoretical Computer Science", 4, 7.5, 2.9, "core", dept="CSE", is_proof_based=True),
    _cs("asu", "471", "Introduction to Artificial Intelligence", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer"]),
]

# ============= UF COURSES =============
UF_COURSES: List[Dict] = [
    _cs("uf", "3", "Introduction to Programming Fundamentals 2", 2, 4.5, 3.1, "core", dept="COP", units=4, is_weeder=True),
    _cs("uf", "3503", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", dept="COP"),
    _cs("uf", "3530", "Discrete Structures", 3, 6.0, 3.0, "core", dept="COT", is_proof_based=True, has_coding=False),
    _cs("uf", "4020", "Programming Language Concepts", 3, 6.0, 3.1, "core", dept="COP"),
    _cs("uf", "4600", "Operating Systems", 4, 7.0, 3.0, "core", dept="COP", has_heavy_projects=True),
    _cs("uf", "4531", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="COT", is_proof_based=True),
    _cs("uf", "4770", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CAP", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= NORTHEASTERN COURSES =============
NORTHEASTERN_COURSES: List[Dict] = [
    _cs("northeastern", "2500", "Fundamentals of Computer Science 1", 2, 4.5, 3.2, "core", units=4, is_weeder=True),
    _cs("northeastern", "2510", "Fundamentals of Computer Science 2", 3, 6.0, 3.0, "core", units=4),
    _cs("northeastern", "3000", "Algorithms and Data", 4, 7.0, 2.9, "core"),
    _cs("northeastern", "3500", "Object-Oriented Design", 3, 6.5, 3.0, "core", has_heavy_projects=True),
    _cs("northeastern", "3650", "Computer Systems", 4, 7.0, 3.0, "core"),
    _cs("northeastern", "3700", "Networks and Distributed Systems", 3, 6.5, 3.0, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("northeastern", "4100", "Artificial Intelligence", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer"]),
]

# ============= CU BOULDER COURSES =============
CU_BOULDER_COURSES: List[Dict] = [
    _cs("cu_boulder", "1300", "Computer Science 1: Starting Computing", 2, 4.0, 3.2, "core", dept="CSCI", units=4),
    _cs("cu_boulder", "2270", "Computer Science 2: Data Structures", 3, 6.5, 3.0, "core", dept="CSCI", units=4),
    _cs("cu_boulder", "2400", "Computer Systems", 3, 6.5, 3.0, "core", dept="CSCI"),
    _cs("cu_boulder", "3104", "Algorithms", 4, 7.5, 2.9, "core", dept="CSCI", is_proof_based=True),
    _cs("cu_boulder", "3155", "Principles of Programming Languages", 3, 6.5, 3.0, "core", dept="CSCI"),
    _cs("cu_boulder", "3753", "Operating Systems", 4, 7.0, 3.0, "core", dept="CSCI", has_heavy_projects=True),
    _cs("cu_boulder", "4622", "Machine Learning", 4, 7.5, 3.0, "elective", dept="CSCI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= INDIANA COURSES =============
INDIANA_COURSES: List[Dict] = [
    _cs("indiana", "C200", "Introduction to Computers and Programming", 2, 4.0, 3.2, "core", dept="CSCI"),
    _cs("indiana", "C241", "Discrete Structures for Computer Science", 3, 6.0, 3.0, "core", dept="CSCI", is_proof_based=True),
    _cs("indiana", "C343", "Data Structures", 3, 6.5, 3.0, "core", dept="CSCI"),
    _cs("indiana", "B461", "Database Concepts", 3, 6.0, 3.1, "elective", dept="CSCI", relevant_to=["software_engineer", "data_engineer"]),
    _cs("indiana", "C311", "Programming Languages", 3, 6.5, 3.0, "core", dept="CSCI"),
    _cs("indiana", "P436", "Introduction to Operating Systems", 4, 7.0, 3.0, "core", dept="CSCI", has_heavy_projects=True),
    _cs("indiana", "B551", "Elements of Artificial Intelligence", 4, 7.0, 3.0, "elective", dept="CSCI", relevant_to=["ml_engineer"]),
]

# ============= UMASS COURSES =============
UMASS_COURSES: List[Dict] = [
    _cs("umass", "121", "Introduction to Problem Solving with Computers", 2, 4.0, 3.2, "core", dept="COMPSCI", units=4, is_weeder=True),
    _cs("umass", "187", "Programming with Data Structures", 3, 6.0, 3.0, "core", dept="COMPSCI", units=4),
    _cs("umass", "220", "Programming Methodology", 3, 6.5, 3.0, "core", dept="COMPSCI"),
    _cs("umass", "230", "Computer Systems Principles", 3, 6.5, 3.0, "core", dept="COMPSCI"),
    _cs("umass", "311", "Introduction to Algorithms", 4, 7.5, 2.9, "core", dept="COMPSCI", is_proof_based=True),
    _cs("umass", "377", "Operating Systems", 4, 7.0, 3.0, "core", dept="COMPSCI", has_heavy_projects=True),
    _cs("umass", "589", "Machine Learning", 4, 7.5, 3.0, "elective", dept="COMPSCI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= TAMU COURSES =============
TAMU_COURSES: List[Dict] = [
    _cs("tamu", "121", "Introduction to Program Design and Concepts", 2, 4.0, 3.2, "core", dept="CSCE", units=4, is_weeder=True),
    _cs("tamu", "221", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", dept="CSCE", units=4),
    _cs("tamu", "222", "Discrete Structures for Computing", 3, 6.0, 3.0, "core", dept="CSCE", is_proof_based=True),
    _cs("tamu", "313", "Introduction to Computer Systems", 3, 6.5, 3.0, "core", dept="CSCE"),
    _cs("tamu", "411", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSCE", is_proof_based=True),
    _cs("tamu", "410", "Operating Systems", 4, 7.0, 3.0, "core", dept="CSCE", has_heavy_projects=True),
    _cs("tamu", "421", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CSCE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= ROCHESTER COURSES =============
ROCHESTER_COURSES: List[Dict] = [
    _cs("rochester", "171", "Introduction to Computer Science", 2, 4.0, 3.2, "core", units=4),
    _cs("rochester", "172", "Introduction to Data Structures", 3, 6.0, 3.0, "core", units=4),
    _cs("rochester", "252", "Computer Organization", 3, 6.5, 3.0, "core"),
    _cs("rochester", "261", "Database Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("rochester", "282", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("rochester", "256", "Operating Systems", 4, 7.0, 3.0, "core", has_heavy_projects=True),
    _cs("rochester", "446", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= DARTMOUTH COURSES =============
DARTMOUTH_COURSES: List[Dict] = [
    _cs("dartmouth", "1", "Introduction to Programming and Computation", 2, 4.0, 3.3, "core", dept="COSC"),
    _cs("dartmouth", "10", "Problem Solving via Object-Oriented Programming", 3, 5.5, 3.1, "core", dept="COSC"),
    _cs("dartmouth", "30", "Discrete Mathematics in Computer Science", 3, 6.0, 3.0, "core", dept="COSC", is_proof_based=True),
    _cs("dartmouth", "31", "Algorithms", 4, 7.5, 2.9, "core", dept="COSC", is_proof_based=True),
    _cs("dartmouth", "50", "Software Design and Implementation", 3, 6.5, 3.0, "core", dept="COSC", has_heavy_projects=True),
    _cs("dartmouth", "56", "Digital Electronics", 3, 6.0, 3.1, "core", dept="COSC", has_coding=False),
    _cs("dartmouth", "74", "Machine Learning and Statistical Data Analysis", 4, 7.0, 3.0, "elective", dept="COSC", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= WASHU COURSES =============
WASHU_COURSES: List[Dict] = [
    _cs("washu", "131", "Introduction to Computer Science", 2, 4.0, 3.3, "core", dept="CSE", units=4),
    _cs("washu", "247", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", dept="CSE", units=4),
    _cs("washu", "332", "Object-Oriented Software Development", 3, 6.5, 3.0, "core", dept="CSE", has_heavy_projects=True),
    _cs("washu", "361", "Introduction to Systems Software", 4, 7.0, 3.0, "core", dept="CSE"),
    _cs("washu", "347", "Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSE", is_proof_based=True),
    _cs("washu", "417", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
    _cs("washu", "422", "Introduction to Operating Systems", 4, 7.0, 3.0, "core", dept="CSE", has_heavy_projects=True),
]


def get_extended_courses2() -> List[Dict]:
    """Get all courses from the second batch of extended universities."""
    return (
        UCSC_COURSES + USC_COURSES + DUKE_COURSES + NORTHWESTERN_COURSES + RICE_COURSES
        + NYU_COURSES + UC_DAVIS_COURSES + UC_IRVINE_COURSES
        + OHIO_STATE_COURSES + PENN_STATE_COURSES + VIRGINIA_TECH_COURSES
        + UVA_COURSES + BROWN_COURSES + YALE_COURSES + JOHNS_HOPKINS_COURSES
        + NC_STATE_COURSES + UNC_COURSES + UMN_COURSES + STONY_BROOK_COURSES
        + RUTGERS_COURSES + ASU_COURSES + UF_COURSES + NORTHEASTERN_COURSES
        + CU_BOULDER_COURSES + INDIANA_COURSES + UMASS_COURSES + TAMU_COURSES
        + ROCHESTER_COURSES + DARTMOUTH_COURSES + WASHU_COURSES
    )
