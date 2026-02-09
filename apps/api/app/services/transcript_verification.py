"""
Transcript verification service for freshness checking and tampering detection.
Analyzes transcripts for authenticity and recency.
"""

import re
import logging
from typing import Optional
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger("pathway.transcript_verification")

# Current date for freshness checks
CURRENT_DATE = datetime.now()
CURRENT_YEAR = CURRENT_DATE.year
CURRENT_MONTH = CURRENT_DATE.month


@dataclass
class VerificationFlag:
    """A single verification flag/concern."""
    code: str  # e.g., "STALE_TRANSCRIPT", "GPA_MISMATCH"
    severity: str  # "high", "medium", "low"
    message: str
    details: Optional[dict] = None


@dataclass
class TranscriptVerificationResult:
    """Complete verification result for a transcript."""
    status: str  # "verified", "warning", "suspicious"
    confidence_score: float  # 0-100
    flags: list[VerificationFlag] = field(default_factory=list)
    checks_performed: list[str] = field(default_factory=list)
    summary: str = ""


class TranscriptVerificationService:
    """Service for verifying transcript authenticity and freshness."""

    # Grade point mappings
    GRADE_TO_POINTS = {
        "A+": 4.0, "A": 4.0, "A-": 3.7,
        "B+": 3.3, "B": 3.0, "B-": 2.7,
        "C+": 2.3, "C": 2.0, "C-": 1.7,
        "D+": 1.3, "D": 1.0, "D-": 0.7,
        "F": 0.0,
    }

    def verify_transcript(
        self,
        parsed_transcript: dict,
        pdf_metadata: Optional[dict] = None,
        graduation_year: Optional[int] = None,
    ) -> TranscriptVerificationResult:
        """
        Run all verification checks on a transcript.

        Args:
            parsed_transcript: Parsed transcript data with courses, semesters, gpa
            pdf_metadata: PDF metadata (creator, creation date, mod date, etc.)
            graduation_year: Expected graduation year if known

        Returns:
            TranscriptVerificationResult with status, score, and flags
        """
        flags: list[VerificationFlag] = []
        checks_performed: list[str] = []

        # 1. Freshness check
        freshness_flags = self._check_freshness(parsed_transcript, graduation_year)
        flags.extend(freshness_flags)
        checks_performed.append("freshness")

        # 2. GPA cross-validation
        gpa_flags = self._cross_validate_gpa(parsed_transcript)
        flags.extend(gpa_flags)
        checks_performed.append("gpa_validation")

        # 3. Statistical anomaly detection
        anomaly_flags = self._detect_statistical_anomalies(parsed_transcript)
        flags.extend(anomaly_flags)
        checks_performed.append("statistical_analysis")

        # 4. Semester gap detection
        gap_flags = self._detect_semester_gaps(parsed_transcript)
        flags.extend(gap_flags)
        checks_performed.append("semester_gaps")

        # 5. Grade distribution check
        dist_flags = self._check_grade_distribution(parsed_transcript)
        flags.extend(dist_flags)
        checks_performed.append("grade_distribution")

        # 6. PDF metadata analysis (if available)
        if pdf_metadata:
            meta_flags = self._analyze_pdf_metadata(pdf_metadata)
            flags.extend(meta_flags)
            checks_performed.append("pdf_metadata")

        # Calculate confidence score
        confidence_score = self._calculate_confidence_score(flags)

        # Determine status
        if confidence_score >= 60:
            status = "verified"
        elif confidence_score >= 30:
            status = "warning"
        else:
            status = "suspicious"

        # Generate summary
        summary = self._generate_summary(status, flags, confidence_score)

        return TranscriptVerificationResult(
            status=status,
            confidence_score=confidence_score,
            flags=flags,
            checks_performed=checks_performed,
            summary=summary,
        )

    def _check_freshness(
        self,
        parsed_transcript: dict,
        graduation_year: Optional[int] = None,
    ) -> list[VerificationFlag]:
        """
        Check if transcript contains expected recent semesters.

        Logic:
        - Month 1-5 (Jan-May): Expect Fall of previous year to be latest
        - Month 6-8 (Jun-Aug): Expect Spring of current year to be latest
        - Month 9-12 (Sep-Dec): Expect Spring of current year to be latest (Fall just started)

        If graduated: Expect through Spring of graduation year
        """
        flags = []
        semesters = parsed_transcript.get("semesters", [])

        if not semesters:
            return flags

        # Determine expected latest semester
        if graduation_year and graduation_year < CURRENT_YEAR:
            # Already graduated - expect through Spring of graduation year
            expected_term = "spring"
            expected_year = graduation_year
        elif CURRENT_MONTH <= 5:
            # Jan-May: Fall of previous year should be complete
            expected_term = "fall"
            expected_year = CURRENT_YEAR - 1
        elif CURRENT_MONTH <= 8:
            # Jun-Aug: Spring of current year should be complete
            expected_term = "spring"
            expected_year = CURRENT_YEAR
        else:
            # Sep-Dec: Spring of current year should be latest (Fall just started)
            expected_term = "spring"
            expected_year = CURRENT_YEAR

        # Find the latest semester in transcript
        latest_semester = self._find_latest_semester(semesters)

        if latest_semester:
            sem_year = latest_semester.get("year")
            sem_term = latest_semester.get("term", "").lower()

            # Check if transcript is stale
            is_stale = False
            if sem_year and sem_year < expected_year:
                is_stale = True
            elif sem_year == expected_year:
                if expected_term == "fall" and sem_term == "spring":
                    is_stale = True
                elif expected_term == "spring" and sem_term == "fall":
                    # Fall is before Spring, so this is actually fine if same year
                    is_stale = True

            if is_stale:
                expected_str = f"{expected_term.title()} {expected_year}"
                actual_str = f"{sem_term.title()} {sem_year}" if sem_term else f"{sem_year}"
                flags.append(VerificationFlag(
                    code="STALE_TRANSCRIPT",
                    severity="medium",
                    message=f"Transcript appears outdated. Expected up to {expected_str}, but latest is {actual_str}",
                    details={
                        "expected_term": expected_term,
                        "expected_year": expected_year,
                        "actual_term": sem_term,
                        "actual_year": sem_year,
                    }
                ))

        return flags

    def _find_latest_semester(self, semesters: list) -> Optional[dict]:
        """Find the chronologically latest semester."""
        if not semesters:
            return None

        def semester_key(sem):
            year = sem.get("year", 0) or 0
            term = (sem.get("term") or sem.get("name") or "").lower()
            # Spring = 1, Summer = 2, Fall = 3
            if "spring" in term:
                term_order = 1
            elif "summer" in term:
                term_order = 2
            elif "fall" in term:
                term_order = 3
            else:
                term_order = 0
            return (year, term_order)

        return max(semesters, key=semester_key)

    def _cross_validate_gpa(self, parsed_transcript: dict) -> list[VerificationFlag]:
        """
        Cross-validate reported GPA against calculated GPA from individual grades.
        """
        flags = []
        reported_gpa = parsed_transcript.get("cumulative_gpa") or parsed_transcript.get("gpa")

        if not reported_gpa:
            return flags

        # Calculate GPA from courses
        courses = parsed_transcript.get("courses", [])
        if not courses:
            # Try getting courses from semesters
            semesters = parsed_transcript.get("semesters", [])
            for sem in semesters:
                courses.extend(sem.get("courses", []))

        if len(courses) < 5:
            return flags  # Not enough courses to validate

        total_points = 0
        total_units = 0

        for course in courses:
            grade = course.get("grade", "")
            units = course.get("units") or course.get("credits") or 3

            # Skip pass/fail and other non-standard grades
            if grade.upper() in ("P", "NP", "CR", "NC", "S", "U", "W", "I", "IP"):
                continue

            points = self.GRADE_TO_POINTS.get(grade.upper())
            if points is not None:
                total_points += points * units
                total_units += units

        if total_units > 0:
            calculated_gpa = total_points / total_units
            difference = abs(reported_gpa - calculated_gpa)

            if difference > 0.3:
                flags.append(VerificationFlag(
                    code="GPA_MISMATCH_HIGH",
                    severity="high",
                    message=f"Reported GPA ({reported_gpa:.2f}) differs significantly from calculated GPA ({calculated_gpa:.2f})",
                    details={
                        "reported_gpa": reported_gpa,
                        "calculated_gpa": round(calculated_gpa, 2),
                        "difference": round(difference, 2),
                        "courses_analyzed": total_units,
                    }
                ))
            elif difference > 0.15:
                flags.append(VerificationFlag(
                    code="GPA_MISMATCH_MODERATE",
                    severity="medium",
                    message=f"Reported GPA ({reported_gpa:.2f}) differs from calculated GPA ({calculated_gpa:.2f})",
                    details={
                        "reported_gpa": reported_gpa,
                        "calculated_gpa": round(calculated_gpa, 2),
                        "difference": round(difference, 2),
                    }
                ))

        return flags

    def _detect_statistical_anomalies(self, parsed_transcript: dict) -> list[VerificationFlag]:
        """
        Detect statistical anomalies that might indicate tampering.
        """
        flags = []

        # Get all courses
        courses = parsed_transcript.get("courses", [])
        if not courses:
            semesters = parsed_transcript.get("semesters", [])
            for sem in semesters:
                courses.extend(sem.get("courses", []))

        if len(courses) < 10:
            return flags

        # Check for all identical grades
        grades = [c.get("grade", "").upper() for c in courses if c.get("grade")]
        grades = [g for g in grades if g not in ("P", "NP", "CR", "NC", "W", "I")]

        if len(grades) >= 20:
            unique_grades = set(grades)
            if len(unique_grades) == 1:
                flags.append(VerificationFlag(
                    code="ALL_IDENTICAL_GRADES",
                    severity="medium",
                    message=f"All {len(grades)} graded courses have identical grade ({list(unique_grades)[0]})",
                    details={"grade": list(unique_grades)[0], "count": len(grades)}
                ))

        # Check for GPA > 4.0 on 4.0 scale
        reported_gpa = parsed_transcript.get("cumulative_gpa") or parsed_transcript.get("gpa")
        if reported_gpa and reported_gpa > 4.0:
            flags.append(VerificationFlag(
                code="GPA_OVER_SCALE",
                severity="high",
                message=f"Reported GPA ({reported_gpa}) exceeds 4.0 scale",
                details={"gpa": reported_gpa}
            ))

        # Check for excessive pass/fail
        pnp_grades = [g for g in [c.get("grade", "").upper() for c in courses] if g in ("P", "NP", "CR", "NC", "S", "U")]
        pnp_ratio = len(pnp_grades) / len(courses) if courses else 0
        if pnp_ratio > 0.5:
            flags.append(VerificationFlag(
                code="EXCESSIVE_PASS_FAIL",
                severity="medium",
                message=f"Over 50% of courses ({len(pnp_grades)}/{len(courses)}) are pass/fail",
                details={"pnp_count": len(pnp_grades), "total_count": len(courses), "ratio": round(pnp_ratio, 2)}
            ))

        return flags

    def _detect_semester_gaps(self, parsed_transcript: dict) -> list[VerificationFlag]:
        """
        Detect missing semesters that might indicate selective reporting.
        """
        flags = []
        semesters = parsed_transcript.get("semesters", [])

        if len(semesters) < 2:
            return flags

        # Extract years and terms
        semester_data = []
        for sem in semesters:
            year = sem.get("year")
            name = sem.get("name", "").lower()
            term = sem.get("term", "").lower()

            if not year:
                # Try to extract from name
                year_match = re.search(r'20\d{2}', name)
                if year_match:
                    year = int(year_match.group())

            if not term:
                if "fall" in name:
                    term = "fall"
                elif "spring" in name:
                    term = "spring"
                elif "summer" in name:
                    term = "summer"

            if year and term in ("fall", "spring"):
                semester_data.append({"year": year, "term": term})

        if len(semester_data) < 2:
            return flags

        # Sort by year and term
        semester_data.sort(key=lambda x: (x["year"], 0 if x["term"] == "spring" else 1))

        # Build expected sequence
        first = semester_data[0]
        last = semester_data[-1]

        expected = []
        year = first["year"]
        term = first["term"]

        while (year, term) <= (last["year"], last["term"]):
            expected.append({"year": year, "term": term})
            if term == "spring":
                term = "fall"
            else:
                term = "spring"
                year += 1

        # Find gaps
        actual_set = {(s["year"], s["term"]) for s in semester_data}
        missing = [s for s in expected if (s["year"], s["term"]) not in actual_set]

        for gap in missing:
            flags.append(VerificationFlag(
                code="MISSING_SEMESTER",
                severity="medium",
                message=f"Missing {gap['term'].title()} {gap['year']} semester",
                details={"year": gap["year"], "term": gap["term"]}
            ))

        return flags

    def _check_grade_distribution(self, parsed_transcript: dict) -> list[VerificationFlag]:
        """
        Check if grade distribution is suspiciously uniform or perfect.
        """
        flags = []

        courses = parsed_transcript.get("courses", [])
        if not courses:
            semesters = parsed_transcript.get("semesters", [])
            for sem in semesters:
                courses.extend(sem.get("courses", []))

        if len(courses) < 15:
            return flags

        # Get numeric grades
        grade_points = []
        for course in courses:
            grade = course.get("grade", "").upper()
            points = self.GRADE_TO_POINTS.get(grade)
            if points is not None:
                grade_points.append(points)

        if len(grade_points) < 15:
            return flags

        # Calculate standard deviation
        mean = sum(grade_points) / len(grade_points)
        variance = sum((x - mean) ** 2 for x in grade_points) / len(grade_points)
        std_dev = variance ** 0.5

        # Check for suspiciously low variance (nearly all same grades)
        if std_dev < 0.1:
            flags.append(VerificationFlag(
                code="UNIFORM_GRADES",
                severity="low",
                message=f"Grade distribution is unusually uniform (std dev: {std_dev:.3f})",
                details={"std_dev": round(std_dev, 3), "mean": round(mean, 2)}
            ))

        # Check for no grade below A- across many courses
        if len(grade_points) >= 20 and all(p >= 3.7 for p in grade_points):
            flags.append(VerificationFlag(
                code="ALL_A_GRADES",
                severity="low",
                message=f"All {len(grade_points)} graded courses are A- or above",
                details={"count": len(grade_points)}
            ))

        return flags

    def _analyze_pdf_metadata(self, metadata: dict) -> list[VerificationFlag]:
        """
        Analyze PDF metadata for signs of tampering.
        """
        flags = []

        creator = (metadata.get("Creator") or metadata.get("creator") or "").lower()
        producer = (metadata.get("Producer") or metadata.get("producer") or "").lower()
        creation_date = metadata.get("CreationDate") or metadata.get("creation_date")
        mod_date = metadata.get("ModDate") or metadata.get("mod_date")

        # Check for editing software
        editing_software = ["photoshop", "illustrator", "acrobat", "pdf editor", "foxit", "nitro", "pdfelement"]
        for software in editing_software:
            if software in creator or software in producer:
                flags.append(VerificationFlag(
                    code="EDITED_WITH_SOFTWARE",
                    severity="high",
                    message=f"PDF appears to have been created/edited with {software.title()}",
                    details={"creator": creator, "producer": producer}
                ))
                break

        # Check for modification after creation
        if creation_date and mod_date and mod_date != creation_date:
            # Parse dates if they're strings
            try:
                if isinstance(creation_date, str) and isinstance(mod_date, str):
                    # PDF dates are often in format D:20240101120000
                    if creation_date != mod_date:
                        flags.append(VerificationFlag(
                            code="PDF_MODIFIED",
                            severity="medium",
                            message="PDF has been modified after creation",
                            details={"creation_date": creation_date, "mod_date": mod_date}
                        ))
            except Exception:
                pass

        # Check for generic creator (might be fine, just noting)
        generic_creators = ["chrome", "firefox", "safari", "microsoft print", "print to pdf"]
        is_generic = any(g in creator for g in generic_creators)

        # University systems often have specific creators
        university_indicators = ["banner", "peoplesoft", "ellucian", "jenzabar", "oracle", "student information"]
        has_university_indicator = any(u in creator.lower() or u in producer.lower() for u in university_indicators)

        if is_generic and not has_university_indicator:
            flags.append(VerificationFlag(
                code="GENERIC_PDF_CREATOR",
                severity="low",
                message="PDF created with generic tool rather than university system",
                details={"creator": creator}
            ))

        return flags

    def _calculate_confidence_score(self, flags: list[VerificationFlag]) -> float:
        """
        Calculate confidence score starting at 100 and subtracting based on flags.

        Penalties:
        - HIGH severity: -20 points
        - MEDIUM severity: -8 points
        - LOW severity: -3 points
        """
        score = 100.0

        for flag in flags:
            if flag.severity == "high":
                score -= 20
            elif flag.severity == "medium":
                score -= 8
            elif flag.severity == "low":
                score -= 3

        return max(0, min(100, score))

    def _generate_summary(
        self,
        status: str,
        flags: list[VerificationFlag],
        confidence_score: float,
    ) -> str:
        """Generate a human-readable summary of verification results."""
        if status == "verified":
            if not flags:
                return "Transcript verification passed with no issues detected."
            else:
                return f"Transcript verification passed with {len(flags)} minor observation(s)."
        elif status == "warning":
            high_count = sum(1 for f in flags if f.severity == "high")
            medium_count = sum(1 for f in flags if f.severity == "medium")
            return f"Transcript requires review: {high_count} critical and {medium_count} moderate issue(s) detected."
        else:  # suspicious
            high_count = sum(1 for f in flags if f.severity == "high")
            return f"Transcript verification failed: {high_count} critical issue(s) detected. Manual review recommended."


# Global instance
transcript_verification_service = TranscriptVerificationService()
