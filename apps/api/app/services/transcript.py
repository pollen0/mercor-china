"""
Transcript parsing and scoring service.
Parses academic transcripts and calculates sophisticated scores based on:
- Course difficulty
- Grade performance
- Course load
- Trajectory (improvement over time)
- Exceptional achievements (freshman in senior classes, etc.)
"""

import io
import re
import json
import logging
import httpx
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime
from sqlalchemy.orm import Session

from ..config import settings
from ..models.course import Course, University, CandidateTranscript, CandidateCourseGrade

logger = logging.getLogger("pathway.transcript")


# ============= Data Classes =============

@dataclass
class ParsedCourse:
    """A single course parsed from transcript."""
    code: str  # "CS 61A"
    name: Optional[str] = None
    grade: Optional[str] = None
    units: int = 3
    semester: Optional[str] = None  # "Fall 2023"
    year: Optional[int] = None
    gpa_value: Optional[float] = None
    # Edge case tracking
    is_graduate: bool = False  # 200+ level graduate course
    is_pass_fail: bool = False  # P/NP, CR/NC, S/U grading
    is_transfer: bool = False  # Transfer credit from another institution
    is_ap: bool = False  # AP credit
    student_year: Optional[int] = None  # Year student took course (1-4)


@dataclass
class ParsedTranscript:
    """Complete parsed transcript data."""
    university: Optional[str] = None
    student_name: Optional[str] = None
    major: Optional[str] = None  # Primary major (backwards compat)
    majors: list[str] = field(default_factory=list)  # All majors for double/triple major
    minors: list[str] = field(default_factory=list)  # All minors
    graduation_year: Optional[int] = None
    cumulative_gpa: Optional[float] = None
    major_gpa: Optional[float] = None
    courses: list[ParsedCourse] = field(default_factory=list)
    semesters: dict = field(default_factory=dict)  # {"Fall 2023": [courses]}
    raw_text: Optional[str] = None
    # Transfer/AP tracking
    is_transfer: bool = False
    transfer_university: Optional[str] = None
    ap_credits: list[dict] = field(default_factory=list)  # [{exam, score, units}]


@dataclass
class TranscriptScore:
    """Comprehensive transcript scoring result."""
    # Overall score (0-100)
    overall_score: float

    # Component scores (0-100 each)
    course_rigor_score: float      # How difficult were the courses
    performance_score: float       # How well did they perform
    trajectory_score: float        # Are grades improving over time
    load_score: float              # Average units per semester
    achievement_score: float       # Exceptional achievements

    # Detailed breakdown
    breakdown: dict

    # Positive signals
    strengths: list[str]

    # Concerns or flags
    concerns: list[str]

    # Notable achievements
    achievements: list[str]

    # Raw data
    total_units: int
    technical_units: int
    avg_semester_units: float
    gpa: Optional[float]
    technical_gpa: Optional[float]


# ============= Grade Mappings =============

GRADE_TO_GPA = {
    # Standard 4.0 scale
    "A+": 4.0, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
    # Pass/Fail
    "P": None, "NP": None,
    "CR": None, "NC": None,
    "S": None, "U": None,
    # Other
    "W": None, "I": None, "IP": None,
}

# Some schools use 4.3 scale
GRADE_TO_GPA_4_3 = {
    "A+": 4.3, "A": 4.0, "A-": 3.7,
    "B+": 3.3, "B": 3.0, "B-": 2.7,
    "C+": 2.3, "C": 2.0, "C-": 1.7,
    "D+": 1.3, "D": 1.0, "D-": 0.7,
    "F": 0.0,
}


class TranscriptService:
    """Service for parsing and scoring academic transcripts."""

    def __init__(self):
        # Claude API (exclusive - all AI uses Claude Sonnet 4.5)
        self.api_key = settings.anthropic_api_key
        self.claude_model = settings.claude_model
        self.base_url = "https://api.anthropic.com/v1"

        if not self.api_key:
            logger.warning("ANTHROPIC_API_KEY not set - transcript AI features will not work")

    # ============= PDF Parsing =============

    def extract_text_from_pdf(self, file_bytes: bytes) -> str:
        """Extract text from PDF transcript."""
        try:
            import pdfplumber
        except ImportError:
            raise RuntimeError("pdfplumber not installed. Run: pip install pdfplumber")

        text_parts = []
        with pdfplumber.open(io.BytesIO(file_bytes)) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    text_parts.append(page_text)

        return "\n\n".join(text_parts)

    async def parse_transcript(self, raw_text: str) -> ParsedTranscript:
        """
        Parse raw transcript text using AI to extract structured data.
        """
        if not self.api_key:
            return ParsedTranscript(raw_text=raw_text)

        system_prompt = """You are an expert at parsing academic transcripts.
Extract structured course and grade information from the transcript text.
Be precise with course codes, grades, and semesters.
For Berkeley courses, common formats include: CS 61A, EECS 16A, DATA C100, MATH 54.
For UIUC courses: CS 225, ECE 391, MATH 241.

Respond in valid JSON format only."""

        user_prompt = f"""Parse this academic transcript and extract all courses with grades:

TRANSCRIPT TEXT:
{raw_text[:12000]}

Respond with JSON in this exact format:
{{
    "university": "University name (e.g., UC Berkeley, UIUC)",
    "student_name": "Student name or null",
    "majors": ["Computer Science", "Mathematics"],
    "minors": ["Data Science"],
    "graduation_year": 2026,
    "cumulative_gpa": 3.65,
    "major_gpa": 3.80,
    "is_transfer": false,
    "transfer_university": null,
    "ap_credits": [
        {{"exam": "AP Computer Science A", "score": 5, "units": 4, "equivalent_course": "CS 61A"}}
    ],
    "semesters": [
        {{
            "name": "Fall 2023",
            "year": 2023,
            "term": "fall",
            "student_year": 2,
            "courses": [
                {{
                    "code": "CS 61B",
                    "name": "Data Structures",
                    "grade": "A",
                    "units": 4,
                    "is_graduate": false,
                    "is_transfer": false,
                    "is_pass_fail": false
                }}
            ]
        }}
    ]
}}

Notes:
- Parse ALL courses visible in the transcript
- Use standard grade format (A+, A, A-, B+, B, P, NP, etc.)
- If units aren't shown, estimate based on course type (most are 3-4)
- student_year: 1=freshman, 2=sophomore, 3=junior, 4=senior
- Include AP/transfer credits if shown - mark them appropriately
- For double/triple majors, list ALL majors in the "majors" array
- Mark courses as is_graduate=true if they are 200+ level grad courses
- Mark courses as is_pass_fail=true if graded P/NP, CR/NC, or S/U
- Mark courses as is_transfer=true if transferred from another institution"""

        try:
            if not self.api_key:
                raise ValueError("ANTHROPIC_API_KEY not configured")

            async with httpx.AsyncClient(timeout=90.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.claude_model,
                        "max_tokens": 8000,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": user_prompt}
                        ]
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["content"][0]["text"]

                # Extract JSON from response (Claude may include markdown code blocks)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                parsed = json.loads(content.strip())

                # Convert to our data structures
                all_courses = []
                semesters_dict = {}

                for semester in parsed.get("semesters", []):
                    sem_name = semester.get("name", "Unknown")
                    sem_year = semester.get("year")
                    student_year = semester.get("student_year")

                    sem_courses = []
                    for course in semester.get("courses", []):
                        grade = course.get("grade")
                        is_pass_fail = course.get("is_pass_fail", False) or grade in ("P", "NP", "CR", "NC", "S", "U")
                        gpa_value = None if is_pass_fail else GRADE_TO_GPA.get(grade)

                        parsed_course = ParsedCourse(
                            code=course.get("code", "UNKNOWN"),
                            name=course.get("name"),
                            grade=grade,
                            units=course.get("units", 3),
                            semester=sem_name,
                            year=sem_year,
                            gpa_value=gpa_value,
                            is_graduate=course.get("is_graduate", False),
                            is_pass_fail=is_pass_fail,
                            is_transfer=course.get("is_transfer", False),
                            is_ap=False,  # AP credits handled separately
                            student_year=student_year
                        )
                        all_courses.append(parsed_course)
                        sem_courses.append(parsed_course)

                    semesters_dict[sem_name] = sem_courses

                # Handle majors (single or multiple)
                majors = parsed.get("majors", [])
                if not majors and parsed.get("major"):
                    majors = [parsed.get("major")]
                primary_major = majors[0] if majors else parsed.get("major")

                return ParsedTranscript(
                    university=parsed.get("university"),
                    student_name=parsed.get("student_name"),
                    major=primary_major,
                    majors=majors,
                    minors=parsed.get("minors", []),
                    graduation_year=parsed.get("graduation_year"),
                    cumulative_gpa=parsed.get("cumulative_gpa"),
                    major_gpa=parsed.get("major_gpa"),
                    courses=all_courses,
                    semesters=semesters_dict,
                    raw_text=raw_text,
                    is_transfer=parsed.get("is_transfer", False),
                    transfer_university=parsed.get("transfer_university"),
                    ap_credits=parsed.get("ap_credits", [])
                )

        except Exception as e:
            logger.error(f"Transcript parsing error: {e}")
            return ParsedTranscript(raw_text=raw_text)

    # ============= Course Difficulty Lookup =============

    def get_course_difficulty(
        self,
        course_code: str,
        university: str,
        db: Session
    ) -> tuple[Optional[Course], float]:
        """
        Look up course difficulty from database.
        Returns (Course or None, difficulty_score).
        If not found, returns estimated difficulty.
        """
        # Normalize course code
        normalized = self._normalize_course_code(course_code)
        dept, number = self._parse_course_code(normalized)

        if not dept or not number:
            return None, 5.0  # Default medium difficulty

        # Try to find exact match
        university_id = self._get_university_id(university)
        course_id = f"{university_id}_{dept.lower()}{number.lower()}"

        course = db.query(Course).filter(Course.id == course_id).first()
        if course:
            return course, course.difficulty_score

        # Try aliases
        course = db.query(Course).filter(
            Course.university_id == university_id,
            Course.aliases.contains([course_code])
        ).first()
        if course:
            return course, course.difficulty_score

        # Try department + number match
        course = db.query(Course).filter(
            Course.university_id == university_id,
            Course.department == dept,
            Course.number == number
        ).first()
        if course:
            return course, course.difficulty_score

        # Estimate difficulty based on course number and department
        estimated = self._estimate_course_difficulty(dept, number)
        return None, estimated

    def _normalize_course_code(self, code: str) -> str:
        """Normalize course code format."""
        # Remove extra spaces, standardize case
        code = re.sub(r'\s+', ' ', code.strip().upper())
        return code

    def _parse_course_code(self, code: str) -> tuple[Optional[str], Optional[str]]:
        """Parse course code into department and number."""
        # Match patterns like "CS 61A", "EECS16A", "DATA C100", "MATH 54"
        match = re.match(r'([A-Z]+)\s*([A-Z]?\d+[A-Z]?)', code)
        if match:
            return match.group(1), match.group(2)
        return None, None

    def _get_university_id(self, university: str) -> str:
        """Convert university name to ID."""
        uni_lower = university.lower() if university else ""
        if "berkeley" in uni_lower or "ucb" in uni_lower:
            return "berkeley"
        if "illinois" in uni_lower or "uiuc" in uni_lower:
            return "uiuc"
        if "stanford" in uni_lower:
            return "stanford"
        if "cmu" in uni_lower or "carnegie" in uni_lower:
            return "cmu"
        if "mit" in uni_lower:
            return "mit"
        return "unknown"

    def _estimate_course_difficulty(self, dept: str, number: str) -> float:
        """
        Estimate course difficulty based on department and number.
        Used when course is not in database.
        """
        # Extract numeric part
        num_match = re.search(r'\d+', number)
        num = int(num_match.group()) if num_match else 100

        # Base difficulty by course level
        if num < 50:
            base = 3.0  # Intro courses
        elif num < 100:
            base = 5.0  # Lower division
        elif num < 200:
            base = 6.5  # Upper division
        elif num < 300:
            base = 7.5  # Advanced undergrad / early grad
        else:
            base = 8.0  # Graduate level

        # Adjust by department
        hard_depts = {"CS", "EECS", "EE", "ECE", "MATH", "PHYSICS", "STAT"}
        medium_depts = {"DATA", "INFO", "IE", "IEOR"}

        if dept in hard_depts:
            base += 0.5
        elif dept not in medium_depts:
            base -= 0.5

        return min(10.0, max(1.0, base))

    # ============= Scoring Algorithm =============

    async def score_transcript(
        self,
        parsed: ParsedTranscript,
        db: Session
    ) -> TranscriptScore:
        """
        Comprehensive transcript scoring algorithm.

        Components:
        1. Course Rigor (30%): How difficult were the courses taken
        2. Performance (35%): Grades relative to course difficulty
        3. Trajectory (15%): Grade improvement over time
        4. Load (10%): Units per semester
        5. Achievement (10%): Exceptional patterns

        Edge cases handled:
        - Freshman in senior-level courses (bonus)
        - Heavy course loads (bonus)
        - Hard courses with high grades (amplified bonus)
        - Grade drops (penalty with context)
        - Retakes (contextual penalty)
        """
        if not parsed.courses:
            return TranscriptScore(
                overall_score=0,
                course_rigor_score=0,
                performance_score=0,
                trajectory_score=50,  # Neutral
                load_score=0,
                achievement_score=0,
                breakdown={},
                strengths=[],
                concerns=["No courses found in transcript"],
                achievements=[],
                total_units=0,
                technical_units=0,
                avg_semester_units=0,
                gpa=None,
                technical_gpa=None
            )

        # Enrich courses with difficulty data
        enriched_courses = []
        for course in parsed.courses:
            db_course, difficulty = self.get_course_difficulty(
                course.code,
                parsed.university or "",
                db
            )
            enriched_courses.append({
                "course": course,
                "db_course": db_course,
                "difficulty": difficulty,
                "is_technical": self._is_technical_course(course.code, db_course),
                "is_known": db_course is not None
            })

        # Calculate component scores
        rigor_score, rigor_details = self._calculate_rigor_score(enriched_courses)
        performance_score, perf_details = self._calculate_performance_score(enriched_courses)
        trajectory_score, traj_details = self._calculate_trajectory_score(
            enriched_courses, parsed.semesters
        )
        load_score, load_details = self._calculate_load_score(parsed.semesters)
        achievement_score, achievements = self._calculate_achievement_score(
            enriched_courses, parsed.semesters
        )

        # Calculate weighted overall
        overall = (
            rigor_score * 0.30 +
            performance_score * 0.35 +
            trajectory_score * 0.15 +
            load_score * 0.10 +
            achievement_score * 0.10
        )

        # Calculate GPAs
        total_units = sum(c["course"].units for c in enriched_courses)
        tech_courses = [c for c in enriched_courses if c["is_technical"]]
        technical_units = sum(c["course"].units for c in tech_courses)

        gpa = self._calculate_gpa(enriched_courses)
        tech_gpa = self._calculate_gpa(tech_courses) if tech_courses else None

        avg_units = total_units / len(parsed.semesters) if parsed.semesters else 0

        # Compile strengths and concerns
        strengths = []
        concerns = []

        if rigor_score >= 75:
            strengths.append(f"Takes challenging courses (rigor: {rigor_score:.0f}/100)")
        if performance_score >= 80:
            strengths.append(f"Strong academic performance ({gpa:.2f} GPA)" if gpa else "Strong grades")
        if trajectory_score >= 70:
            strengths.append("Shows consistent or improving performance")
        if load_score >= 70:
            strengths.append(f"Handles heavy course loads ({avg_units:.1f} units/semester)")

        if rigor_score < 40:
            concerns.append("Limited exposure to challenging courses")
        if performance_score < 50:
            concerns.append("Below average academic performance")
        if trajectory_score < 40:
            concerns.append("Declining grade trend")

        # Add specific achievements
        strengths.extend(achievements)

        return TranscriptScore(
            overall_score=round(overall, 1),
            course_rigor_score=round(rigor_score, 1),
            performance_score=round(performance_score, 1),
            trajectory_score=round(trajectory_score, 1),
            load_score=round(load_score, 1),
            achievement_score=round(achievement_score, 1),
            breakdown={
                "rigor": rigor_details,
                "performance": perf_details,
                "trajectory": traj_details,
                "load": load_details,
                "achievements": achievements
            },
            strengths=strengths,
            concerns=concerns,
            achievements=achievements,
            total_units=total_units,
            technical_units=technical_units,
            avg_semester_units=round(avg_units, 1),
            gpa=round(gpa, 2) if gpa else None,
            technical_gpa=round(tech_gpa, 2) if tech_gpa else None
        )

    def _is_technical_course(self, code: str, db_course: Optional[Course]) -> bool:
        """Determine if a course is technical/CS-related."""
        if db_course:
            return db_course.is_technical

        dept, _ = self._parse_course_code(code.upper())
        technical_depts = {
            "CS", "EECS", "EE", "ECE", "CE", "DATA", "STAT",
            "MATH", "PHYSICS", "INFO", "IEOR", "IE"
        }
        return dept in technical_depts if dept else False

    def _calculate_gpa(self, courses: list[dict]) -> Optional[float]:
        """Calculate GPA from courses with grades."""
        total_points = 0
        total_units = 0

        for c in courses:
            course = c["course"]
            if course.gpa_value is not None:
                total_points += course.gpa_value * course.units
                total_units += course.units

        return total_points / total_units if total_units > 0 else None

    def _calculate_rigor_score(self, courses: list[dict]) -> tuple[float, dict]:
        """
        Calculate course rigor score.
        Higher score = harder courses.

        Edge cases handled:
        - P/NP courses: Still count for rigor (student chose hard course, just P/NP)
        - Graduate courses: Extra credit if taken as undergrad
        - Transfer courses: Count but with lower weight (less context)
        - AP credits: Don't count for rigor (not taken in college)
        """
        if not courses:
            return 0, {}

        # Weight by units
        total_weighted_difficulty = 0
        total_units = 0

        difficulty_counts = {i: 0 for i in range(1, 6)}  # Tier 1-5
        grad_courses_as_undergrad = []
        pnp_hard_courses = []

        for c in courses:
            course = c["course"]

            # Skip AP credits for rigor calculation
            if course.is_ap:
                continue

            difficulty = c["difficulty"]
            units = course.units

            # Graduate courses taken as undergrad get difficulty boost
            if course.is_graduate and course.student_year and course.student_year <= 3:
                difficulty = min(10, difficulty + 1.5)
                grad_courses_as_undergrad.append({
                    "course": course.code,
                    "student_year": course.student_year
                })

            # Transfer courses: still count but with slightly lower weight
            weight_multiplier = 0.8 if course.is_transfer else 1.0

            # P/NP courses: track separately for bonus if hard
            if course.is_pass_fail and difficulty >= 7:
                pnp_hard_courses.append(course.code)

            total_weighted_difficulty += difficulty * units * weight_multiplier
            total_units += units * weight_multiplier

            # Count difficulty tiers
            tier = min(5, max(1, int(difficulty / 2) + 1))
            difficulty_counts[tier] += 1

        avg_difficulty = total_weighted_difficulty / total_units if total_units > 0 else 5

        # Convert to 0-100 scale (difficulty 1-10 -> score 0-100)
        base_score = (avg_difficulty / 10) * 100

        # Bonus for having multiple very hard courses
        elite_courses = sum(1 for c in courses if c["difficulty"] >= 8 and not c["course"].is_ap)
        very_hard_courses = sum(1 for c in courses if c["difficulty"] >= 7 and not c["course"].is_ap)

        bonus = min(15, elite_courses * 5 + very_hard_courses * 2)

        # Bonus for grad courses as undergrad
        grad_bonus = min(10, len(grad_courses_as_undergrad) * 5)

        # Bonus for P/NP in hard courses (shows willingness to take risks)
        pnp_bonus = min(5, len(pnp_hard_courses) * 2)

        return min(100, base_score + bonus + grad_bonus + pnp_bonus), {
            "avg_difficulty": round(avg_difficulty, 2),
            "difficulty_distribution": difficulty_counts,
            "elite_courses": elite_courses,
            "very_hard_courses": very_hard_courses,
            "grad_courses_as_undergrad": grad_courses_as_undergrad,
            "pnp_hard_courses": pnp_hard_courses,
            "bonus": bonus,
            "grad_bonus": grad_bonus,
            "pnp_bonus": pnp_bonus
        }

    def _calculate_performance_score(self, courses: list[dict]) -> tuple[float, dict]:
        """
        Calculate performance score.
        Considers grades relative to course difficulty.
        High grade in hard course = amplified credit.

        Edge cases handled:
        - P/NP courses: Pass in hard course = moderate credit (70 performance)
        - Graduate courses: Passing grad courses as undergrad = bonus
        - AP credits: Don't count for performance (college performance only)
        """
        if not courses:
            return 0, {}

        weighted_performance = 0
        total_weight = 0

        exceptional_performances = []  # A/A+ in difficulty >= 8
        pnp_passes = []  # P in hard courses

        grad_course_passes = []

        for c in courses:
            course = c["course"]
            difficulty = c["difficulty"]

            # Skip AP credits for college performance
            if course.is_ap:
                continue

            # Handle P/NP courses specially
            if course.is_pass_fail:
                if course.grade in ("P", "CR", "S"):  # Passed
                    # P in hard course = moderate credit (equivalent to ~B performance)
                    base_performance = 70 if difficulty >= 7 else 60
                    weight = course.units * 0.5  # Lower weight than graded courses
                    weighted_performance += base_performance * weight
                    total_weight += weight
                    if difficulty >= 7:
                        pnp_passes.append({
                            "course": course.code,
                            "difficulty": difficulty
                        })
                # NP/NC/U = no credit, skip
                continue

            if course.gpa_value is None:
                continue

            # Base performance: GPA value (0-4) -> (0-100)
            base_performance = (course.gpa_value / 4.0) * 100

            # Adjust for difficulty
            # Hard course with high grade = bonus
            # Easy course with low grade = bigger penalty
            difficulty_factor = difficulty / 5  # 1-10 -> 0.2-2.0

            if course.gpa_value >= 3.7:  # A-/A/A+
                # Bonus for A in hard course
                multiplier = 1 + (difficulty - 5) * 0.1  # Up to 1.5x for difficulty 10
            elif course.gpa_value >= 3.0:  # B range
                multiplier = 1.0
            else:
                # Penalty for low grade in easy course
                multiplier = 1 - (5 - difficulty) * 0.05  # Down to 0.75x for difficulty 1

            adjusted_performance = base_performance * multiplier

            # Grad course as undergrad: extra credit for passing
            if course.is_graduate and course.student_year and course.student_year <= 3:
                if course.gpa_value >= 3.0:
                    grad_course_passes.append({
                        "course": course.code,
                        "grade": course.grade,
                        "student_year": course.student_year
                    })
                    adjusted_performance *= 1.1  # 10% bonus

            # Weight by units and difficulty
            weight = course.units * (1 + difficulty_factor * 0.2)
            weighted_performance += adjusted_performance * weight
            total_weight += weight

            # Track exceptional performances
            if course.gpa_value >= 3.7 and difficulty >= 8:
                exceptional_performances.append({
                    "course": course.code,
                    "grade": course.grade,
                    "difficulty": difficulty
                })

        avg_performance = weighted_performance / total_weight if total_weight > 0 else 50

        # Bonus for exceptional performances
        exceptional_bonus = min(10, len(exceptional_performances) * 3)

        # Bonus for passing grad courses as undergrad
        grad_bonus = min(8, len(grad_course_passes) * 4)

        return min(100, avg_performance + exceptional_bonus + grad_bonus), {
            "base_score": round(avg_performance, 1),
            "exceptional_performances": exceptional_performances,
            "exceptional_bonus": exceptional_bonus,
            "pnp_passes": pnp_passes,
            "grad_course_passes": grad_course_passes,
            "grad_bonus": grad_bonus
        }

    def _calculate_trajectory_score(
        self,
        courses: list[dict],
        semesters: dict
    ) -> tuple[float, dict]:
        """
        Calculate trajectory score.
        Improving grades over time = bonus.
        Declining grades = penalty.
        """
        if len(semesters) < 2:
            return 50, {"note": "Insufficient semesters for trajectory analysis"}

        # Calculate GPA per semester
        semester_gpas = []
        sorted_semesters = self._sort_semesters(list(semesters.keys()))

        for sem_name in sorted_semesters:
            sem_courses = semesters.get(sem_name, [])
            if not sem_courses:
                continue

            total_points = 0
            total_units = 0

            for course in sem_courses:
                if course.gpa_value is not None:
                    total_points += course.gpa_value * course.units
                    total_units += course.units

            if total_units > 0:
                semester_gpas.append({
                    "semester": sem_name,
                    "gpa": total_points / total_units,
                    "units": total_units
                })

        if len(semester_gpas) < 2:
            return 50, {"note": "Insufficient graded semesters"}

        # Calculate trend
        first_half = semester_gpas[:len(semester_gpas)//2]
        second_half = semester_gpas[len(semester_gpas)//2:]

        first_avg = sum(s["gpa"] for s in first_half) / len(first_half)
        second_avg = sum(s["gpa"] for s in second_half) / len(second_half)

        # Linear trend
        trend = second_avg - first_avg

        # Convert trend to score
        # +0.5 GPA improvement = 75 score
        # -0.5 GPA decline = 25 score
        # Neutral = 50
        base_score = 50 + trend * 50

        # Bonus for consistent high performance
        if min(s["gpa"] for s in semester_gpas) >= 3.5:
            base_score += 10  # Always above 3.5

        # Penalty for any semester below 2.5
        low_semesters = sum(1 for s in semester_gpas if s["gpa"] < 2.5)
        penalty = low_semesters * 5

        return max(0, min(100, base_score - penalty)), {
            "first_half_avg": round(first_avg, 2),
            "second_half_avg": round(second_avg, 2),
            "trend": round(trend, 3),
            "semester_gpas": semester_gpas
        }

    def _calculate_load_score(self, semesters: dict) -> tuple[float, dict]:
        """
        Calculate course load score.
        Heavy loads handled well = bonus.
        """
        if not semesters:
            return 50, {}

        semester_units = []

        for sem_name, courses in semesters.items():
            total_units = sum(c.units for c in courses)
            semester_units.append({
                "semester": sem_name,
                "units": total_units
            })

        if not semester_units:
            return 50, {}

        avg_units = sum(s["units"] for s in semester_units) / len(semester_units)
        max_units = max(s["units"] for s in semester_units)

        # Score based on average units
        # 12 units = 50 (low), 15 = 65 (normal), 18 = 80 (heavy), 21+ = 95 (very heavy)
        if avg_units < 12:
            base_score = 30 + (avg_units / 12) * 20
        elif avg_units < 15:
            base_score = 50 + ((avg_units - 12) / 3) * 15
        elif avg_units < 18:
            base_score = 65 + ((avg_units - 15) / 3) * 15
        else:
            base_score = 80 + min(20, (avg_units - 18) * 5)

        # Bonus for semesters with 20+ units
        heavy_semesters = sum(1 for s in semester_units if s["units"] >= 20)
        bonus = min(10, heavy_semesters * 3)

        return min(100, base_score + bonus), {
            "avg_units": round(avg_units, 1),
            "max_units": max_units,
            "heavy_semesters": heavy_semesters,
            "semester_units": semester_units
        }

    def _calculate_achievement_score(
        self,
        courses: list[dict],
        semesters: dict
    ) -> tuple[float, list[str]]:
        """
        Calculate achievement score for exceptional patterns.

        Achievements:
        - Freshman taking senior-level courses with good grades
        - Taking multiple hard courses in one semester
        - Perfect grades in hard courses
        - Research/independent study
        """
        achievements = []
        score = 50  # Start neutral

        # Group by semester with student year
        for sem_name, sem_courses in semesters.items():
            # Try to determine student year from semester name
            student_year = self._estimate_student_year(sem_name, semesters)

            hard_courses_in_sem = []
            for course in sem_courses:
                # Find in enriched courses
                for ec in courses:
                    if ec["course"].code == course.code and ec["course"].semester == sem_name:
                        if ec["difficulty"] >= 7:
                            hard_courses_in_sem.append(ec)
                        break

            # Achievement: Multiple hard courses in one semester
            if len(hard_courses_in_sem) >= 3:
                achievements.append(
                    f"Took {len(hard_courses_in_sem)} difficult courses in {sem_name}"
                )
                score += 10

            # Achievement: Freshman/sophomore in hard courses
            if student_year and student_year <= 2:
                for ec in hard_courses_in_sem:
                    if ec["difficulty"] >= 8 and ec["course"].gpa_value and ec["course"].gpa_value >= 3.7:
                        achievements.append(
                            f"Earned {ec['course'].grade} in {ec['course'].code} as a {'freshman' if student_year == 1 else 'sophomore'}"
                        )
                        score += 15

        # Achievement: Perfect technical GPA
        tech_courses = [c for c in courses if c["is_technical"] and c["course"].gpa_value]
        if tech_courses:
            tech_gpa = sum(c["course"].gpa_value * c["course"].units for c in tech_courses) / \
                       sum(c["course"].units for c in tech_courses)
            if tech_gpa >= 3.9:
                achievements.append(f"Near-perfect technical GPA ({tech_gpa:.2f})")
                score += 15

        # Achievement: A+ in elite courses
        a_plus_elite = [c for c in courses if c["difficulty"] >= 9 and c["course"].grade == "A+"]
        for c in a_plus_elite[:3]:  # Cap at 3
            achievements.append(f"A+ in {c['course'].code} (elite difficulty)")
            score += 10

        # Achievement: Graduate courses as undergrad with good grades
        grad_courses = [c for c in courses if c["course"].is_graduate and c["course"].gpa_value and c["course"].gpa_value >= 3.0]
        if grad_courses:
            for gc in grad_courses[:3]:  # Cap at 3
                achievements.append(f"Completed graduate-level {gc['course'].code} with {gc['course'].grade}")
                score += 8

        # Achievement: Successfully P/NP'd hard courses (strategic risk-taking)
        pnp_hard = [c for c in courses if c["course"].is_pass_fail and c["course"].grade in ("P", "CR", "S") and c["difficulty"] >= 8]
        if len(pnp_hard) >= 2:
            achievements.append(f"Successfully completed {len(pnp_hard)} elite courses P/NP (strategic risk-taking)")
            score += 5

        # Achievement: Breadth across different technical areas
        tech_depts = set()
        for c in courses:
            if c["is_technical"]:
                dept, _ = self._parse_course_code(c["course"].code)
                if dept:
                    tech_depts.add(dept)
        if len(tech_depts) >= 4:
            achievements.append(f"Technical breadth across {len(tech_depts)} departments ({', '.join(sorted(tech_depts)[:4])})")
            score += 8

        return min(100, score), achievements

    def _sort_semesters(self, semesters: list[str]) -> list[str]:
        """Sort semesters chronologically."""
        def semester_key(sem: str):
            sem_lower = sem.lower()
            year_match = re.search(r'20\d{2}', sem)
            year = int(year_match.group()) if year_match else 2000

            if "spring" in sem_lower:
                term = 1
            elif "summer" in sem_lower:
                term = 2
            elif "fall" in sem_lower:
                term = 3
            else:
                term = 0

            return (year, term)

        return sorted(semesters, key=semester_key)

    def _estimate_student_year(self, semester: str, all_semesters: dict) -> Optional[int]:
        """Estimate student year based on semester position."""
        sorted_sems = self._sort_semesters(list(all_semesters.keys()))
        if semester not in sorted_sems:
            return None

        position = sorted_sems.index(semester)
        # Assuming 2 semesters per year
        return min(4, (position // 2) + 1)

    # ============= Unknown Course Research =============

    async def research_unknown_course(
        self,
        course_code: str,
        university: str
    ) -> dict:
        """
        Research an unknown course using web search + AI.
        Returns estimated difficulty and course info.
        """
        if not self.api_key:
            dept, number = self._parse_course_code(course_code.upper())
            return {
                "difficulty_score": self._estimate_course_difficulty(dept or "", number or ""),
                "confidence": 0.3,
                "source": "estimated"
            }

        system_prompt = """You are a research assistant helping to determine course difficulty.
Based on your knowledge of university courses and any context provided,
estimate the difficulty of this course.

Consider:
- Course level (intro, upper div, graduate)
- Department reputation for difficulty
- Prerequisites and workload
- Whether it's a "weeder" course

Respond in valid JSON format."""

        user_prompt = f"""Research this course and estimate its difficulty:

University: {university}
Course: {course_code}

Respond with JSON:
{{
    "course_name": "Full course name if known",
    "difficulty_score": <1-10 scale>,
    "difficulty_tier": <1-5 where 5 is hardest>,
    "is_technical": true/false,
    "is_weeder": true/false,
    "has_coding": true/false,
    "typical_gpa": <class average GPA if known, else null>,
    "prerequisites": ["list of prereqs if known"],
    "confidence": <0-1 how confident in this assessment>,
    "reasoning": "Brief explanation of difficulty assessment"
}}"""

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.base_url}/messages",
                    headers={
                        "x-api-key": self.api_key,
                        "anthropic-version": "2023-06-01",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.claude_model,
                        "max_tokens": 1000,
                        "system": system_prompt,
                        "messages": [
                            {"role": "user", "content": user_prompt}
                        ]
                    }
                )
                response.raise_for_status()
                result = response.json()
                content = result["content"][0]["text"]

                # Extract JSON from response (Claude may include markdown code blocks)
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0]
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0]

                return json.loads(content.strip())

        except Exception as e:
            logger.error(f"Course research error: {e}")
            dept, number = self._parse_course_code(course_code.upper())
            return {
                "difficulty_score": self._estimate_course_difficulty(dept or "", number or ""),
                "confidence": 0.2,
                "source": "fallback_estimated",
                "error": str(e)
            }


    # ============= Grade Inflation Calibration =============

    # Grade inflation factors by school (1.0 = neutral, <1.0 = inflate, >1.0 = deflate)
    # Based on published grade distributions and known difficulty
    GRADE_INFLATION_FACTORS = {
        # Schools with known grade inflation (discount grades slightly)
        "harvard": 0.92,
        "yale": 0.93,
        "brown": 0.90,  # Known for generous grading
        "stanford": 0.95,

        # Schools with known grade deflation (boost grades slightly)
        "mit": 1.06,
        "princeton": 1.04,
        "caltech": 1.08,
        "uchicago": 1.04,
        "berkeley": 1.02,
        "cmu": 1.03,
        "carnegie mellon": 1.03,
        "georgia tech": 1.03,
        "uiuc": 1.01,
        "purdue": 1.02,

        # Neutral (average calibration)
        "cornell": 1.00,
        "columbia": 0.98,
        "ucla": 0.99,
        "umich": 1.00,
        "michigan": 1.00,
    }

    # Course equivalency mappings for cross-school comparison
    COURSE_EQUIVALENCIES = {
        # Data structures courses
        "berkeley:cs61b": {"equivalent_level": 6.5, "equivalents": ["stanford:cs106b", "mit:6.006", "cmu:15-122"]},
        "mit:6.006": {"equivalent_level": 7.0, "equivalents": ["berkeley:cs61b", "stanford:cs161"]},
        "stanford:cs106b": {"equivalent_level": 6.0, "equivalents": ["berkeley:cs61a", "mit:6.009"]},

        # Algorithms courses
        "berkeley:cs170": {"equivalent_level": 8.0, "equivalents": ["mit:6.046", "stanford:cs161", "cmu:15-451"]},
        "mit:6.046": {"equivalent_level": 8.5, "equivalents": ["berkeley:cs170", "stanford:cs161"]},

        # Operating systems
        "berkeley:cs162": {"equivalent_level": 8.5, "equivalents": ["mit:6.828", "stanford:cs140", "cmu:15-410"]},
        "mit:6.828": {"equivalent_level": 9.0, "equivalents": ["berkeley:cs162", "cmu:15-410"]},

        # Machine learning
        "berkeley:cs189": {"equivalent_level": 8.0, "equivalents": ["stanford:cs229", "mit:6.867", "cmu:10-701"]},
        "stanford:cs229": {"equivalent_level": 8.0, "equivalents": ["berkeley:cs189", "mit:6.867"]},
    }

    def get_grade_inflation_factor(self, university: str) -> float:
        """Get grade inflation factor for a university."""
        if not university:
            return 1.0

        uni_lower = university.lower()

        # Check exact matches first
        for key, factor in self.GRADE_INFLATION_FACTORS.items():
            if key in uni_lower:
                return factor

        # Default to neutral
        return 1.0

    def calculate_adjusted_gpa(
        self,
        gpa: float,
        university: str,
        course_difficulty_avg: float = 5.0
    ) -> dict:
        """
        Calculate GPA adjusted for grade inflation and course difficulty.

        Returns:
            adjusted_gpa: GPA calibrated across schools
            percentile_estimate: Estimated percentile at school
            cross_school_equivalent: What this GPA would be at a neutral school
        """
        inflation_factor = self.get_grade_inflation_factor(university)

        # Adjust for inflation
        adjusted_gpa = gpa * inflation_factor

        # Further adjust for course difficulty (optional boost for hard courses)
        # If avg course difficulty > 6, give small boost
        difficulty_boost = max(0, (course_difficulty_avg - 5) * 0.02)
        adjusted_gpa = min(4.0, adjusted_gpa + difficulty_boost)

        # Estimate percentile at school
        # Rough mapping: 3.9+ = 90th, 3.7 = 75th, 3.5 = 60th, 3.3 = 50th, 3.0 = 30th
        if gpa >= 3.9:
            percentile = 90 + (gpa - 3.9) * 50  # 90-100
        elif gpa >= 3.7:
            percentile = 75 + (gpa - 3.7) * 75  # 75-90
        elif gpa >= 3.5:
            percentile = 60 + (gpa - 3.5) * 75  # 60-75
        elif gpa >= 3.3:
            percentile = 50 + (gpa - 3.3) * 50  # 50-60
        elif gpa >= 3.0:
            percentile = 30 + (gpa - 3.0) * 67  # 30-50
        else:
            percentile = max(0, gpa * 10)  # 0-30

        return {
            "original_gpa": gpa,
            "adjusted_gpa": round(adjusted_gpa, 3),
            "inflation_factor": inflation_factor,
            "difficulty_boost": round(difficulty_boost, 3),
            "estimated_percentile": round(percentile, 1),
            "university": university,
        }

    def get_course_equivalents(self, course_code: str, university: str) -> dict:
        """Get equivalent courses at other schools for comparison."""
        key = f"{university.lower().replace(' ', '')}:{course_code.lower().replace(' ', '')}"

        if key in self.COURSE_EQUIVALENCIES:
            return self.COURSE_EQUIVALENCIES[key]

        return None

    def calculate_cross_school_percentile(
        self,
        transcript_score: float,
        university: str,
        major: str = None
    ) -> dict:
        """
        Estimate where this student would rank across all schools.

        Uses university tier + transcript score to estimate cross-school percentile.
        """
        # University tier multipliers
        tier_1_schools = {"mit", "stanford", "berkeley", "cmu", "caltech"}
        tier_2_schools = {"cornell", "columbia", "princeton", "harvard", "yale", "georgia tech", "uiuc", "umich"}
        tier_3_schools = {"ucla", "uwashington", "utexas", "purdue", "uw madison"}

        uni_lower = university.lower() if university else ""

        # Base percentile from transcript score
        base_percentile = transcript_score

        # Adjust by university tier
        tier_boost = 0
        for school in tier_1_schools:
            if school in uni_lower:
                tier_boost = 10
                break

        if tier_boost == 0:
            for school in tier_2_schools:
                if school in uni_lower:
                    tier_boost = 5
                    break

        adjusted_percentile = min(99, base_percentile + tier_boost)

        return {
            "transcript_score": transcript_score,
            "university": university,
            "tier_boost": tier_boost,
            "cross_school_percentile": round(adjusted_percentile, 1),
            "interpretation": self._get_percentile_interpretation(adjusted_percentile),
        }

    def _get_percentile_interpretation(self, percentile: float) -> str:
        """Get human-readable interpretation of percentile."""
        if percentile >= 95:
            return "Exceptional - Top 5% nationally"
        elif percentile >= 90:
            return "Outstanding - Top 10% nationally"
        elif percentile >= 80:
            return "Excellent - Top 20% nationally"
        elif percentile >= 70:
            return "Strong - Above average"
        elif percentile >= 50:
            return "Good - Average for target roles"
        elif percentile >= 30:
            return "Fair - Below average"
        else:
            return "Needs improvement"

    async def enhanced_score_transcript(
        self,
        parsed: ParsedTranscript,
        db: Session,
        include_calibration: bool = True
    ) -> dict:
        """
        Enhanced scoring with cross-school calibration.

        Returns the base TranscriptScore plus:
        - adjusted_gpa: GPA calibrated for grade inflation
        - cross_school_percentile: Where student ranks nationally
        - peer_comparison: How they compare to similar students
        """
        # Get base score
        base_score = await self.score_transcript(parsed, db)

        result = {
            "base_score": base_score,
        }

        if include_calibration and parsed.cumulative_gpa:
            # Calculate adjusted GPA
            avg_difficulty = base_score.breakdown.get("rigor", {}).get("avg_difficulty", 5.0)
            result["adjusted_gpa"] = self.calculate_adjusted_gpa(
                parsed.cumulative_gpa,
                parsed.university or "",
                avg_difficulty
            )

            # Calculate cross-school percentile
            result["cross_school_percentile"] = self.calculate_cross_school_percentile(
                base_score.overall_score,
                parsed.university or "",
                parsed.major
            )

            # Add enhanced insights
            result["insights"] = self._generate_enhanced_insights(
                base_score, result["adjusted_gpa"], result["cross_school_percentile"]
            )

        return result

    def _generate_enhanced_insights(
        self,
        score: TranscriptScore,
        adjusted_gpa: dict,
        cross_school: dict
    ) -> list[str]:
        """Generate enhanced insights from calibration data."""
        insights = []

        # GPA vs adjusted
        if adjusted_gpa["adjusted_gpa"] > adjusted_gpa["original_gpa"] + 0.05:
            insights.append(
                f"GPA adjusted up from {adjusted_gpa['original_gpa']:.2f} to "
                f"{adjusted_gpa['adjusted_gpa']:.2f} due to school's grading rigor"
            )
        elif adjusted_gpa["adjusted_gpa"] < adjusted_gpa["original_gpa"] - 0.05:
            insights.append(
                f"GPA adjusted down from {adjusted_gpa['original_gpa']:.2f} to "
                f"{adjusted_gpa['adjusted_gpa']:.2f} accounting for grade inflation"
            )

        # Percentile insight
        if cross_school["cross_school_percentile"] >= 80:
            insights.append(
                f"Ranks in top {100 - cross_school['cross_school_percentile']:.0f}% "
                f"of CS students nationally"
            )

        # Course rigor insight
        if score.course_rigor_score >= 75 and adjusted_gpa["original_gpa"] >= 3.5:
            insights.append(
                "High GPA maintained despite taking very challenging courses"
            )

        return insights


# Global instance
transcript_service = TranscriptService()
