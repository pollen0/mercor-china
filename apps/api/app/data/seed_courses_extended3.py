"""
Extended seed data for courses at 49 additional universities (batch 3).
Schools ranked ~50-100 in CS.
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


# ============= VANDERBILT COURSES =============
VANDERBILT_COURSES: List[Dict] = [
    _cs("vanderbilt", "101", "Programming and Problem Solving", 2, 4.0, 3.3, "core", is_weeder=True),
    _cs("vanderbilt", "201", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("vanderbilt", "231", "Computer Organization", 3, 6.0, 3.1, "core"),
    _cs("vanderbilt", "251", "Intermediate Software Design", 3, 6.5, 3.0, "core", has_heavy_projects=True),
    _cs("vanderbilt", "270", "Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("vanderbilt", "281", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("vanderbilt", "378", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= NOTRE DAME COURSES =============
NOTRE_DAME_COURSES: List[Dict] = [
    _cs("notre_dame", "10001", "Principles of Computing", 2, 4.0, 3.3, "core", dept="CSE", is_weeder=True),
    _cs("notre_dame", "20312", "Data Structures", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("notre_dame", "20232", "Computer Architecture", 3, 6.0, 3.1, "core", dept="CSE"),
    _cs("notre_dame", "30331", "Theory of Computing", 4, 7.5, 2.9, "core", dept="CSE", is_proof_based=True),
    _cs("notre_dame", "30341", "Operating System Principles", 4, 7.0, 2.9, "core", dept="CSE", has_heavy_projects=True),
    _cs("notre_dame", "30246", "Database Concepts", 3, 6.0, 3.1, "elective", dept="CSE", relevant_to=["software_engineer", "data_engineer"]),
    _cs("notre_dame", "40537", "Deep Learning", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= BU COURSES =============
BU_COURSES: List[Dict] = [
    _cs("bu", "111", "Introduction to Computer Science", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("bu", "112", "Data Structures", 3, 6.5, 3.0, "core", units=4),
    _cs("bu", "210", "Computer Systems", 3, 6.5, 3.0, "core"),
    _cs("bu", "330", "Analysis of Algorithms", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("bu", "350", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("bu", "460", "Introduction to Database Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("bu", "542", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= TUFTS COURSES =============
TUFTS_COURSES: List[Dict] = [
    _cs("tufts", "11", "Introduction to Computer Science", 2, 4.0, 3.3, "core", dept="COMP", is_weeder=True),
    _cs("tufts", "15", "Data Structures", 3, 6.5, 3.0, "core", dept="COMP"),
    _cs("tufts", "40", "Machine Structure and Assembly Language", 3, 6.5, 3.0, "core", dept="COMP"),
    _cs("tufts", "170", "Theory of Computation", 4, 7.5, 2.9, "core", dept="COMP", is_proof_based=True),
    _cs("tufts", "111", "Operating Systems", 4, 7.0, 2.9, "core", dept="COMP", has_heavy_projects=True),
    _cs("tufts", "116", "Introduction to Computer Networks", 3, 6.0, 3.1, "elective", dept="COMP", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("tufts", "135", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="COMP", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= RPI COURSES =============
RPI_COURSES: List[Dict] = [
    _cs("rpi", "1100", "Computer Science I", 2, 4.0, 3.2, "core", dept="CSCI", units=4, is_weeder=True),
    _cs("rpi", "1200", "Data Structures", 3, 6.5, 3.0, "core", dept="CSCI", units=4),
    _cs("rpi", "2500", "Computer Organization", 3, 6.0, 3.1, "core", dept="CSCI"),
    _cs("rpi", "2300", "Introduction to Algorithms", 4, 7.5, 2.8, "core", dept="CSCI", is_proof_based=True),
    _cs("rpi", "4210", "Operating Systems", 4, 7.0, 2.9, "core", dept="CSCI", has_heavy_projects=True),
    _cs("rpi", "4380", "Database Systems", 3, 6.0, 3.1, "elective", dept="CSCI", relevant_to=["software_engineer", "data_engineer"]),
    _cs("rpi", "4100", "Machine Learning from Data", 4, 7.0, 3.0, "elective", dept="CSCI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= CASE WESTERN COURSES =============
CASE_WESTERN_COURSES: List[Dict] = [
    _cs("case_western", "132", "Introduction to Programming in Java", 2, 4.0, 3.2, "core", dept="EECS", is_weeder=True),
    _cs("case_western", "233", "Introduction to Data Structures", 3, 6.5, 3.0, "core", dept="EECS"),
    _cs("case_western", "281", "Logic Design and Computer Organization", 3, 6.0, 3.1, "core", dept="EECS"),
    _cs("case_western", "340", "Algorithms and Data Structures", 4, 7.5, 2.9, "core", dept="EECS", is_proof_based=True),
    _cs("case_western", "338", "Operating Systems and Concurrent Programming", 4, 7.0, 2.9, "core", dept="EECS", has_heavy_projects=True),
    _cs("case_western", "341", "Introduction to Database Systems", 3, 6.0, 3.1, "elective", dept="EECS", relevant_to=["software_engineer", "data_engineer"]),
    _cs("case_western", "391", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="EECS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= PITT COURSES =============
PITT_COURSES: List[Dict] = [
    _cs("pitt", "401", "Intermediate Programming", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("pitt", "445", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("pitt", "447", "Computer Organization and Assembly Language", 3, 6.5, 3.0, "core"),
    _cs("pitt", "1501", "Algorithm Implementation", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("pitt", "1550", "Introduction to Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("pitt", "1555", "Introduction to Database Management Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("pitt", "1675", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UTAH COURSES =============
UTAH_COURSES: List[Dict] = [
    _cs("utah", "1410", "Introduction to Object-Oriented Programming", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("utah", "2420", "Introduction to Algorithms and Data Structures", 3, 6.5, 3.0, "core"),
    _cs("utah", "3810", "Computer Organization", 3, 6.0, 3.1, "core"),
    _cs("utah", "4150", "Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("utah", "4400", "Computer Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("utah", "4480", "Computer Networks", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("utah", "5350", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= IOWA STATE COURSES =============
IOWA_STATE_COURSES: List[Dict] = [
    _cs("iowa_state", "227", "Introduction to Object-Oriented Programming", 2, 4.0, 3.2, "core", dept="COMS", units=4, is_weeder=True),
    _cs("iowa_state", "228", "Introduction to Data Structures", 3, 6.5, 3.0, "core", dept="COMS"),
    _cs("iowa_state", "321", "Computer Architecture and Machine-Level Programming", 3, 6.0, 3.1, "core", dept="COMS"),
    _cs("iowa_state", "311", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="COMS", is_proof_based=True),
    _cs("iowa_state", "352", "Introduction to Operating Systems", 4, 7.0, 2.9, "core", dept="COMS", has_heavy_projects=True),
    _cs("iowa_state", "363", "Introduction to Database Management Systems", 3, 6.0, 3.1, "elective", dept="COMS", relevant_to=["software_engineer", "data_engineer"]),
    _cs("iowa_state", "474", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="COMS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= MICHIGAN STATE COURSES =============
MICHIGAN_STATE_COURSES: List[Dict] = [
    _cs("michigan_state", "231", "Introduction to Programming I", 2, 4.0, 3.2, "core", dept="CSE", units=4, is_weeder=True),
    _cs("michigan_state", "331", "Algorithms and Data Structures", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("michigan_state", "320", "Computer Organization and Architecture", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("michigan_state", "360", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSE", is_proof_based=True),
    _cs("michigan_state", "410", "Operating Systems", 4, 7.0, 2.9, "core", dept="CSE", has_heavy_projects=True),
    _cs("michigan_state", "480", "Database Systems", 3, 6.5, 3.1, "elective", dept="CSE", relevant_to=["software_engineer", "data_engineer"]),
    _cs("michigan_state", "404", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UCF COURSES =============
UCF_COURSES: List[Dict] = [
    _cs("ucf", "1010", "Introduction to Programming", 2, 4.0, 3.2, "core", dept="COP", units=4, is_weeder=True),
    _cs("ucf", "3502", "Computer Science II", 3, 6.5, 3.0, "core", dept="COP"),
    _cs("ucf", "3223", "Computer Architecture", 3, 6.0, 3.1, "core", dept="CDA"),
    _cs("ucf", "3530", "Design and Analysis of Algorithms", 4, 7.5, 2.8, "core", dept="COT", is_proof_based=True),
    _cs("ucf", "4600", "Operating Systems", 4, 7.0, 2.9, "core", dept="COP", has_heavy_projects=True),
    _cs("ucf", "4710", "Computer Networking", 3, 6.0, 3.1, "elective", dept="CNT", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("ucf", "4630", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CAP", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= GMU COURSES =============
GMU_COURSES: List[Dict] = [
    _cs("gmu", "112", "Introduction to Computer Programming", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("gmu", "211", "Object-Oriented Programming", 3, 6.0, 3.0, "core"),
    _cs("gmu", "262", "Introduction to Low-Level Programming", 3, 6.5, 3.0, "core"),
    _cs("gmu", "310", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("gmu", "330", "Formal Methods and Models", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("gmu", "471", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("gmu", "484", "Data Mining", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UCR COURSES =============
UCR_COURSES: List[Dict] = [
    _cs("ucr", "10", "Introduction to Computer Science I", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("ucr", "14", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", units=4),
    _cs("ucr", "61", "Machine Organization and Assembly Language", 3, 6.0, 3.1, "core"),
    _cs("ucr", "141", "Intermediate Data Structures and Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("ucr", "153", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("ucr", "166", "Database Management Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("ucr", "171", "Introduction to Machine Learning and Data Mining", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= RIT COURSES =============
RIT_COURSES: List[Dict] = [
    _cs("rit", "141", "Computer Science I", 2, 4.0, 3.2, "core", dept="CSCI", units=4, is_weeder=True),
    _cs("rit", "242", "Computer Science II", 3, 6.5, 3.0, "core", dept="CSCI", units=4),
    _cs("rit", "250", "Concepts of Computer Systems", 3, 6.0, 3.1, "core", dept="CSCI"),
    _cs("rit", "261", "Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSCI", is_proof_based=True),
    _cs("rit", "243", "Mechanics of Programming", 4, 7.0, 2.9, "core", dept="CSCI", has_heavy_projects=True),
    _cs("rit", "320", "Introduction to Networking", 3, 6.0, 3.1, "elective", dept="CSCI", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("rit", "431", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CSCI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= WPI COURSES =============
WPI_COURSES: List[Dict] = [
    _cs("wpi", "1101", "Introduction to Program Design", 2, 4.0, 3.3, "core", units=4, is_weeder=True),
    _cs("wpi", "2102", "Object-Oriented Design Concepts", 3, 6.0, 3.0, "core"),
    _cs("wpi", "2303", "Systems Programming Concepts", 3, 6.5, 3.0, "core"),
    _cs("wpi", "2223", "Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("wpi", "3013", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("wpi", "3431", "Database Systems I", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("wpi", "4342", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= DREXEL COURSES =============
DREXEL_COURSES: List[Dict] = [
    _cs("drexel", "164", "Introduction to Computer Science", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("drexel", "260", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("drexel", "281", "Systems Architecture", 3, 6.0, 3.1, "core"),
    _cs("drexel", "350", "Design and Analysis of Algorithms", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("drexel", "361", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("drexel", "380", "Computer Networks", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("drexel", "461", "Artificial Intelligence", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= STEVENS COURSES =============
STEVENS_COURSES: List[Dict] = [
    _cs("stevens", "115", "Introduction to Computer Science", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("stevens", "284", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("stevens", "382", "Computer Architecture and Organization", 3, 6.5, 3.0, "core"),
    _cs("stevens", "385", "Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("stevens", "492", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("stevens", "516", "Database Management Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("stevens", "559", "Machine Learning: Fundamentals and Applications", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= NJIT COURSES =============
NJIT_COURSES: List[Dict] = [
    _cs("njit", "114", "Introduction to Computer Science II", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("njit", "241", "Data Structures and Algorithms", 3, 6.5, 3.0, "core"),
    _cs("njit", "252", "Computer Organization and Architecture", 3, 6.0, 3.1, "core"),
    _cs("njit", "435", "Advanced Data Structures and Algorithm Design", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("njit", "332", "Principles of Operating Systems", 4, 7.0, 3.0, "core", has_heavy_projects=True),
    _cs("njit", "370", "Introduction to Distributed Computing", 3, 6.5, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("njit", "482", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= OREGON STATE COURSES =============
OREGON_STATE_COURSES: List[Dict] = [
    _cs("oregon_state", "161", "Introduction to Computer Science I", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("oregon_state", "261", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("oregon_state", "271", "Computer Architecture and Assembly Language", 3, 6.0, 3.1, "core"),
    _cs("oregon_state", "325", "Analysis of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("oregon_state", "344", "Operating Systems I", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("oregon_state", "340", "Introduction to Databases", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("oregon_state", "434", "Machine Learning and Data Mining", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= BUFFALO COURSES =============
BUFFALO_COURSES: List[Dict] = [
    _cs("buffalo", "115", "Introduction to Computer Science I", 2, 4.0, 3.2, "core", dept="CSE", units=4, is_weeder=True),
    _cs("buffalo", "116", "Introduction to Computer Science II", 3, 6.0, 3.0, "core", dept="CSE", units=4),
    _cs("buffalo", "220", "Data Structures", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("buffalo", "331", "Algorithms and Complexity", 4, 7.5, 2.9, "core", dept="CSE", is_proof_based=True),
    _cs("buffalo", "421", "Operating Systems", 4, 7.0, 2.9, "core", dept="CSE", has_heavy_projects=True),
    _cs("buffalo", "474", "Introduction to Computer Networks", 3, 6.0, 3.1, "elective", dept="CSE", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("buffalo", "574", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UTD COURSES =============
UTD_COURSES: List[Dict] = [
    _cs("utd", "1336", "Programming Fundamentals", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("utd", "2336", "Computer Science II", 3, 6.0, 3.0, "core"),
    _cs("utd", "3340", "Computer Architecture", 3, 6.5, 3.0, "core"),
    _cs("utd", "3345", "Data Structures and Algorithms", 3, 6.5, 3.0, "core"),
    _cs("utd", "4349", "Advanced Algorithm Design and Analysis", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("utd", "4348", "Operating Systems Concepts", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("utd", "4375", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UIC COURSES =============
UIC_COURSES: List[Dict] = [
    _cs("uic", "141", "Program Design I", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("uic", "151", "Mathematical Foundations of Computing", 3, 6.0, 3.0, "core", is_proof_based=True, has_coding=False),
    _cs("uic", "251", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("uic", "261", "Machine Organization", 3, 6.0, 3.1, "core"),
    _cs("uic", "401", "Computer Algorithms I", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("uic", "385", "Operating Systems Design", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("uic", "421", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= CLEMSON COURSES =============
CLEMSON_COURSES: List[Dict] = [
    _cs("clemson", "1010", "Introduction to Computing", 2, 4.0, 3.2, "core", dept="CPSC", units=4, is_weeder=True),
    _cs("clemson", "2120", "Introduction to Algorithms and Data Structures", 3, 6.5, 3.0, "core", dept="CPSC"),
    _cs("clemson", "2310", "Computer Organization", 3, 6.0, 3.1, "core", dept="CPSC"),
    _cs("clemson", "3110", "Algorithms and Data Structures", 4, 7.5, 2.9, "core", dept="CPSC", is_proof_based=True),
    _cs("clemson", "3220", "Operating Systems", 4, 7.0, 2.9, "core", dept="CPSC", has_heavy_projects=True),
    _cs("clemson", "4620", "Introduction to Database Management Systems", 3, 6.0, 3.1, "elective", dept="CPSC", relevant_to=["software_engineer", "data_engineer"]),
    _cs("clemson", "4430", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CPSC", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= SYRACUSE COURSES =============
SYRACUSE_COURSES: List[Dict] = [
    _cs("syracuse", "181", "Introduction to Computer Programming", 2, 4.0, 3.3, "core", dept="CIS", units=4, is_weeder=True),
    _cs("syracuse", "351", "Data Structures", 3, 6.5, 3.0, "core", dept="CIS"),
    _cs("syracuse", "375", "Computer Organization and Architecture", 3, 6.0, 3.1, "core", dept="CIS"),
    _cs("syracuse", "352", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CIS", is_proof_based=True),
    _cs("syracuse", "451", "Operating Systems", 4, 7.0, 2.9, "core", dept="CIS", has_heavy_projects=True),
    _cs("syracuse", "453", "Database Management Systems", 3, 6.5, 3.1, "elective", dept="CIS", relevant_to=["software_engineer", "data_engineer"]),
    _cs("syracuse", "479", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CIS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= LEHIGH COURSES =============
LEHIGH_COURSES: List[Dict] = [
    _cs("lehigh", "2", "Introduction to Programming", 2, 4.0, 3.3, "core", dept="CSE", is_weeder=True),
    _cs("lehigh", "17", "Data Structures", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("lehigh", "12", "Computer Architecture and Organization", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("lehigh", "340", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSE", is_proof_based=True),
    _cs("lehigh", "303", "Operating System Design", 4, 7.0, 2.9, "core", dept="CSE", has_heavy_projects=True),
    _cs("lehigh", "341", "Computer Networks", 3, 6.0, 3.1, "elective", dept="CSE", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("lehigh", "347", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= BRANDEIS COURSES =============
BRANDEIS_COURSES: List[Dict] = [
    _cs("brandeis", "11A", "Introduction to Computer Science", 2, 4.0, 3.3, "core", dept="COSI", is_weeder=True),
    _cs("brandeis", "21A", "Data Structures and the Fundamentals of Computing", 3, 6.5, 3.0, "core", dept="COSI"),
    _cs("brandeis", "131A", "Computer Organization and Architecture", 3, 6.0, 3.1, "core", dept="COSI"),
    _cs("brandeis", "121B", "Algorithms", 4, 7.5, 2.9, "core", dept="COSI", is_proof_based=True),
    _cs("brandeis", "103A", "Operating Systems", 4, 7.0, 2.9, "core", dept="COSI", has_heavy_projects=True),
    _cs("brandeis", "127B", "Database Management Systems", 3, 6.0, 3.1, "elective", dept="COSI", relevant_to=["software_engineer", "data_engineer"]),
    _cs("brandeis", "101A", "Machine Learning", 4, 7.0, 3.0, "elective", dept="COSI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UCONN COURSES =============
UCONN_COURSES: List[Dict] = [
    _cs("uconn", "1173", "Introduction to Computer Programming", 2, 4.0, 3.2, "core", dept="CSE", units=4, is_weeder=True),
    _cs("uconn", "2050", "Data Structures and Object-Oriented Programming", 3, 6.5, 3.0, "core", dept="CSE"),
    _cs("uconn", "2300", "Computer Architecture", 3, 6.0, 3.1, "core", dept="CSE"),
    _cs("uconn", "3500", "Algorithms and Complexity", 4, 7.5, 2.8, "core", dept="CSE", is_proof_based=True),
    _cs("uconn", "4300", "Operating Systems", 4, 7.0, 2.9, "core", dept="CSE", has_heavy_projects=True),
    _cs("uconn", "4701", "Computer Networks", 3, 6.0, 3.1, "elective", dept="CSE", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("uconn", "4502", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CSE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= IOWA COURSES =============
IOWA_COURSES: List[Dict] = [
    _cs("iowa", "1210", "Computer Science I: Fundamentals", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("iowa", "2210", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("iowa", "2230", "Computer Organization", 3, 6.0, 3.1, "core"),
    _cs("iowa", "3330", "Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("iowa", "3620", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("iowa", "4350", "Database Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("iowa", "4740", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= USF COURSES =============
USF_COURSES: List[Dict] = [
    _cs("usf", "1050", "Introduction to Computer Science and Programming", 2, 4.0, 3.2, "core", dept="COP", units=4, is_weeder=True),
    _cs("usf", "2510", "Programming Concepts", 3, 6.0, 3.0, "core", dept="COP"),
    _cs("usf", "3514", "Data Structures", 3, 6.5, 3.0, "core", dept="COP"),
    _cs("usf", "4531", "Design and Analysis of Algorithms", 4, 7.5, 2.8, "core", dept="COT", is_proof_based=True),
    _cs("usf", "4600", "Operating Systems", 4, 7.0, 3.0, "core", dept="COP", has_heavy_projects=True),
    _cs("usf", "4710", "Computer Networks", 3, 6.0, 3.1, "elective", dept="CNT", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("usf", "4770", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CAP", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= TEMPLE COURSES =============
TEMPLE_COURSES: List[Dict] = [
    _cs("temple", "1068", "Program Design and Abstraction", 2, 4.0, 3.2, "core", dept="CIS", units=4, is_weeder=True),
    _cs("temple", "2168", "Data Structures", 3, 6.5, 3.0, "core", dept="CIS"),
    _cs("temple", "2107", "Computer Organization and Architecture", 3, 6.0, 3.1, "core", dept="CIS"),
    _cs("temple", "3223", "Algorithm Design and Analysis", 4, 7.5, 2.9, "core", dept="CIS", is_proof_based=True),
    _cs("temple", "3207", "Operating Systems", 4, 7.0, 2.9, "core", dept="CIS", has_heavy_projects=True),
    _cs("temple", "3309", "Database Systems", 3, 6.0, 3.1, "elective", dept="CIS", relevant_to=["software_engineer", "data_engineer"]),
    _cs("temple", "4526", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CIS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= GWU COURSES =============
GWU_COURSES: List[Dict] = [
    _cs("gwu", "1111", "Introduction to Software Development", 2, 4.0, 3.3, "core", units=4, is_weeder=True),
    _cs("gwu", "1112", "Algorithms and Data Structures", 3, 6.5, 3.0, "core"),
    _cs("gwu", "2461", "Computer Architecture", 3, 6.0, 3.1, "core"),
    _cs("gwu", "3212", "Design of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("gwu", "3411", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("gwu", "3510", "Computer Networks", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("gwu", "4364", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= TULANE COURSES =============
TULANE_COURSES: List[Dict] = [
    _cs("tulane", "1010", "Introduction to Computer Science I", 2, 4.0, 3.3, "core", dept="CMPS", is_weeder=True),
    _cs("tulane", "1600", "Data Structures", 3, 6.5, 3.0, "core", dept="CMPS"),
    _cs("tulane", "2200", "Computer Organization", 3, 6.0, 3.1, "core", dept="CMPS"),
    _cs("tulane", "2170", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CMPS", is_proof_based=True),
    _cs("tulane", "3120", "Operating Systems", 4, 7.0, 3.0, "core", dept="CMPS", has_heavy_projects=True),
    _cs("tulane", "3160", "Introduction to Database Systems", 3, 6.0, 3.1, "elective", dept="CMPS", relevant_to=["software_engineer", "data_engineer"]),
    _cs("tulane", "4150", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CMPS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= GEORGETOWN COURSES =============
GEORGETOWN_COURSES: List[Dict] = [
    _cs("georgetown", "1111", "Introduction to Computer Science", 2, 4.0, 3.3, "core", dept="COSC", is_weeder=True),
    _cs("georgetown", "2113", "Data Structures", 3, 6.5, 3.0, "core", dept="COSC"),
    _cs("georgetown", "2210", "Computer Architecture", 3, 6.0, 3.1, "core", dept="COSC"),
    _cs("georgetown", "3320", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="COSC", is_proof_based=True),
    _cs("georgetown", "3250", "Operating Systems", 4, 7.0, 2.9, "core", dept="COSC", has_heavy_projects=True),
    _cs("georgetown", "3362", "Distributed Systems", 3, 6.5, 3.1, "elective", dept="COSC", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("georgetown", "4771", "Machine Learning", 4, 7.0, 3.0, "elective", dept="COSC", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= SANTA CLARA COURSES =============
SANTA_CLARA_COURSES: List[Dict] = [
    _cs("santa_clara", "12", "Introduction to Programming", 2, 4.0, 3.3, "core", dept="CSEN", is_weeder=True),
    _cs("santa_clara", "20", "Data Structures", 3, 6.5, 3.0, "core", dept="CSEN"),
    _cs("santa_clara", "122", "Computer Architecture", 3, 6.0, 3.1, "core", dept="CSEN"),
    _cs("santa_clara", "146", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSEN", is_proof_based=True),
    _cs("santa_clara", "142", "Operating Systems", 4, 7.0, 3.0, "core", dept="CSEN", has_heavy_projects=True),
    _cs("santa_clara", "174", "Database Systems", 3, 6.0, 3.1, "elective", dept="CSEN", relevant_to=["software_engineer", "data_engineer"]),
    _cs("santa_clara", "183", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CSEN", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= MISSOURI COURSES =============
MISSOURI_COURSES: List[Dict] = [
    _cs("missouri", "1050", "Algorithm Design and Programming I", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("missouri", "2050", "Algorithm Design and Programming II", 3, 6.0, 3.0, "core"),
    _cs("missouri", "3050", "Data Structures and Algorithms", 3, 6.5, 3.0, "core"),
    _cs("missouri", "3380", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("missouri", "4320", "Operating Systems I", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("missouri", "4610", "Computer Networks", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("missouri", "4720", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= TENNESSEE COURSES =============
TENNESSEE_COURSES: List[Dict] = [
    _cs("tennessee", "102", "Introduction to Computer Science", 2, 4.0, 3.2, "core", dept="COSC", units=4, is_weeder=True),
    _cs("tennessee", "202", "Data Structures and Algorithms I", 3, 6.5, 3.0, "core", dept="COSC"),
    _cs("tennessee", "230", "Computer Organization", 3, 6.0, 3.1, "core", dept="COSC"),
    _cs("tennessee", "302", "Data Structures and Algorithms II", 4, 7.5, 2.8, "core", dept="COSC", is_proof_based=True),
    _cs("tennessee", "360", "Operating Systems", 4, 7.0, 2.9, "core", dept="COSC", has_heavy_projects=True),
    _cs("tennessee", "365", "Introduction to Database Systems", 3, 6.0, 3.1, "elective", dept="COSC", relevant_to=["software_engineer", "data_engineer"]),
    _cs("tennessee", "425", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="COSC", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= NEBRASKA COURSES =============
NEBRASKA_COURSES: List[Dict] = [
    _cs("nebraska", "155", "Computer Science I", 2, 4.0, 3.2, "core", dept="CSCE", units=4, is_weeder=True),
    _cs("nebraska", "156", "Computer Science II", 3, 6.0, 3.0, "core", dept="CSCE"),
    _cs("nebraska", "230", "Computer Organization", 3, 6.0, 3.1, "core", dept="CSCE"),
    _cs("nebraska", "310", "Data Structures and Algorithms", 3, 6.5, 3.0, "core", dept="CSCE"),
    _cs("nebraska", "340", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CSCE", is_proof_based=True),
    _cs("nebraska", "451", "Operating Systems Principles", 4, 7.0, 2.9, "core", dept="CSCE", has_heavy_projects=True),
    _cs("nebraska", "478", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CSCE", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= AUBURN COURSES =============
AUBURN_COURSES: List[Dict] = [
    _cs("auburn", "1210", "Introduction to Computing I", 2, 4.0, 3.2, "core", dept="COMP", units=4, is_weeder=True),
    _cs("auburn", "2210", "Fundamentals of Computing II", 3, 6.0, 3.0, "core", dept="COMP"),
    _cs("auburn", "3270", "Data Structures", 3, 6.5, 3.0, "core", dept="COMP"),
    _cs("auburn", "3350", "Computer Organization and Assembly Language", 3, 6.0, 3.1, "core", dept="COMP"),
    _cs("auburn", "3240", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="COMP", is_proof_based=True),
    _cs("auburn", "3500", "Operating Systems", 4, 7.0, 2.9, "core", dept="COMP", has_heavy_projects=True),
    _cs("auburn", "4270", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="COMP", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= SMU COURSES =============
SMU_COURSES: List[Dict] = [
    _cs("smu", "1341", "Principles of Computer Science I", 2, 4.0, 3.3, "core", units=4, is_weeder=True),
    _cs("smu", "1342", "Principles of Computer Science II", 3, 6.0, 3.0, "core"),
    _cs("smu", "2341", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("smu", "3353", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("smu", "3310", "Computer Organization and Architecture", 3, 6.0, 3.1, "core"),
    _cs("smu", "4381", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("smu", "4390", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= COLORADO STATE COURSES =============
COLORADO_STATE_COURSES: List[Dict] = [
    _cs("colorado_state", "150", "Introduction to Programming", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("colorado_state", "200", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("colorado_state", "270", "Computer Organization", 3, 6.0, 3.1, "core"),
    _cs("colorado_state", "320", "Algorithms - Theory and Practice", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("colorado_state", "370", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("colorado_state", "457", "Computer Networks and the Internet", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("colorado_state", "440", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UOREGON COURSES =============
UOREGON_COURSES: List[Dict] = [
    _cs("uoregon", "210", "Computer Science I", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("uoregon", "211", "Computer Science II", 3, 6.0, 3.0, "core", units=4),
    _cs("uoregon", "212", "Computer Science III", 3, 6.5, 3.0, "core"),
    _cs("uoregon", "313", "Intermediate Data Structures", 3, 6.5, 3.0, "core"),
    _cs("uoregon", "315", "Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("uoregon", "415", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("uoregon", "471", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= KANSAS COURSES =============
KANSAS_COURSES: List[Dict] = [
    _cs("kansas", "140", "Introduction to Programming I", 2, 4.0, 3.2, "core", dept="EECS", units=4, is_weeder=True),
    _cs("kansas", "168", "Introduction to Programming II", 3, 6.0, 3.0, "core", dept="EECS"),
    _cs("kansas", "268", "Data Structures", 3, 6.5, 3.0, "core", dept="EECS"),
    _cs("kansas", "560", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="EECS", is_proof_based=True),
    _cs("kansas", "678", "Operating Systems", 4, 7.0, 2.9, "core", dept="EECS", has_heavy_projects=True),
    _cs("kansas", "648", "Database Systems", 3, 6.0, 3.1, "elective", dept="EECS", relevant_to=["software_engineer", "data_engineer"]),
    _cs("kansas", "690", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="EECS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= BINGHAMTON COURSES =============
BINGHAMTON_COURSES: List[Dict] = [
    _cs("binghamton", "110", "Programming and Computation", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("binghamton", "140", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("binghamton", "220", "Computer Organization", 3, 6.0, 3.1, "core"),
    _cs("binghamton", "311", "Algorithm Design and Analysis", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("binghamton", "350", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("binghamton", "360", "Computer Networks", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("binghamton", "435", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= DELAWARE COURSES =============
DELAWARE_COURSES: List[Dict] = [
    _cs("delaware", "180", "Introduction to Computer Science I", 2, 4.0, 3.2, "core", dept="CISC", units=4, is_weeder=True),
    _cs("delaware", "220", "Data Structures", 3, 6.5, 3.0, "core", dept="CISC"),
    _cs("delaware", "260", "Machine Organization and Assembly Language", 3, 6.0, 3.1, "core", dept="CISC"),
    _cs("delaware", "320", "Introduction to Algorithms", 4, 7.5, 2.9, "core", dept="CISC", is_proof_based=True),
    _cs("delaware", "361", "Operating Systems", 4, 7.0, 2.9, "core", dept="CISC", has_heavy_projects=True),
    _cs("delaware", "437", "Database Systems", 3, 6.0, 3.1, "elective", dept="CISC", relevant_to=["software_engineer", "data_engineer"]),
    _cs("delaware", "484", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", dept="CISC", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= MIAMI COURSES =============
MIAMI_COURSES: List[Dict] = [
    _cs("miami", "110", "Introduction to Computer Science", 2, 4.0, 3.3, "core", dept="CIS", units=4, is_weeder=True),
    _cs("miami", "220", "Data Structures", 3, 6.5, 3.0, "core", dept="CIS"),
    _cs("miami", "310", "Computer Architecture", 3, 6.0, 3.1, "core", dept="CIS"),
    _cs("miami", "313", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", dept="CIS", is_proof_based=True),
    _cs("miami", "321", "Operating Systems", 4, 7.0, 3.0, "core", dept="CIS", has_heavy_projects=True),
    _cs("miami", "411", "Distributed Systems", 3, 6.5, 3.1, "elective", dept="CIS", relevant_to=["software_engineer", "devops_engineer"]),
    _cs("miami", "472", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CIS", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= ALABAMA COURSES =============
ALABAMA_COURSES: List[Dict] = [
    _cs("alabama", "100", "Introduction to Computer Science", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("alabama", "201", "Data Structures and Algorithms", 3, 6.5, 3.0, "core"),
    _cs("alabama", "250", "Computer Organization and Assembly", 3, 6.0, 3.1, "core"),
    _cs("alabama", "370", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("alabama", "300", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("alabama", "457", "Database Management Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("alabama", "470", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= UKY COURSES =============
UKY_COURSES: List[Dict] = [
    _cs("uky", "215", "Introduction to Program Design", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("uky", "315", "Data Structures", 3, 6.5, 3.0, "core"),
    _cs("uky", "281", "Computer Organization", 3, 6.0, 3.1, "core"),
    _cs("uky", "405", "Design and Analysis of Algorithms", 4, 7.5, 2.9, "core", is_proof_based=True),
    _cs("uky", "470", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("uky", "460", "Database Systems", 3, 6.0, 3.1, "elective", relevant_to=["software_engineer", "data_engineer"]),
    _cs("uky", "475", "Introduction to Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= WM COURSES =============
WM_COURSES: List[Dict] = [
    _cs("wm", "141", "Computational Problem Solving", 2, 4.0, 3.3, "core", dept="CSCI", is_weeder=True),
    _cs("wm", "241", "Data Structures", 3, 6.5, 3.0, "core", dept="CSCI"),
    _cs("wm", "304", "Computer Organization", 3, 6.0, 3.1, "core", dept="CSCI"),
    _cs("wm", "303", "Algorithms", 4, 7.5, 2.9, "core", dept="CSCI", is_proof_based=True),
    _cs("wm", "444", "Operating Systems", 4, 7.0, 2.9, "core", dept="CSCI", has_heavy_projects=True),
    _cs("wm", "344", "Databases", 3, 6.0, 3.1, "elective", dept="CSCI", relevant_to=["software_engineer", "data_engineer"]),
    _cs("wm", "424", "Machine Learning", 4, 7.0, 3.0, "elective", dept="CSCI", relevant_to=["ml_engineer", "data_scientist"]),
]

# ============= LSU COURSES =============
LSU_COURSES: List[Dict] = [
    _cs("lsu", "1350", "Introduction to Computer Science", 2, 4.0, 3.2, "core", units=4, is_weeder=True),
    _cs("lsu", "1351", "Computer Science II", 3, 6.0, 3.0, "core"),
    _cs("lsu", "2259", "Data Structures and Algorithm Analysis", 3, 6.5, 3.0, "core"),
    _cs("lsu", "2262", "Computer Organization and Design", 3, 6.0, 3.1, "core"),
    _cs("lsu", "4103", "Design and Analysis of Algorithms", 4, 7.5, 2.8, "core", is_proof_based=True),
    _cs("lsu", "4740", "Operating Systems", 4, 7.0, 2.9, "core", has_heavy_projects=True),
    _cs("lsu", "4633", "Machine Learning", 4, 7.0, 3.0, "elective", relevant_to=["ml_engineer", "data_scientist"]),
]


def get_extended_courses3() -> List[Dict]:
    """Get all courses from the third batch of extended universities."""
    return (
        VANDERBILT_COURSES + NOTRE_DAME_COURSES + BU_COURSES + TUFTS_COURSES + RPI_COURSES
        + CASE_WESTERN_COURSES + PITT_COURSES + UTAH_COURSES + IOWA_STATE_COURSES
        + MICHIGAN_STATE_COURSES + UCF_COURSES + GMU_COURSES + UCR_COURSES + RIT_COURSES
        + WPI_COURSES + DREXEL_COURSES + STEVENS_COURSES + NJIT_COURSES
        + OREGON_STATE_COURSES + BUFFALO_COURSES + UTD_COURSES + UIC_COURSES
        + CLEMSON_COURSES + SYRACUSE_COURSES + LEHIGH_COURSES + BRANDEIS_COURSES
        + UCONN_COURSES + IOWA_COURSES + USF_COURSES + TEMPLE_COURSES
        + GWU_COURSES + TULANE_COURSES + GEORGETOWN_COURSES + SANTA_CLARA_COURSES
        + MISSOURI_COURSES + TENNESSEE_COURSES + NEBRASKA_COURSES + AUBURN_COURSES
        + SMU_COURSES + COLORADO_STATE_COURSES + UOREGON_COURSES + KANSAS_COURSES
        + BINGHAMTON_COURSES + DELAWARE_COURSES + MIAMI_COURSES + ALABAMA_COURSES
        + UKY_COURSES + WM_COURSES + LSU_COURSES
    )
