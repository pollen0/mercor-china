"""
Cohort comparison service for calculating percentile rankings.

Calculates where a candidate ranks among their peers (same university, graduation year).
"""

from typing import Optional, Dict, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.candidate import Candidate, CandidateVerticalProfile, VerticalProfileStatus
from ..models.employer import Vertical


class CohortService:
    """Service for calculating cohort comparisons and percentile rankings."""

    def calculate_percentile(
        self,
        score: float,
        university: Optional[str],
        graduation_year: Optional[int],
        vertical: Optional[Vertical],
        db: Session,
    ) -> Tuple[Optional[int], Optional[str], int]:
        """
        Calculate a candidate's percentile within their cohort.

        Args:
            score: Candidate's best score (0-10)
            university: Candidate's university
            graduation_year: Candidate's graduation year
            vertical: Career vertical (engineering, data, etc.)
            db: Database session

        Returns:
            Tuple of (percentile 1-100, cohort_label, cohort_size)
            Returns (None, None, 0) if cohort is too small or data is missing
        """
        if not score or not university or not graduation_year:
            return None, None, 0

        # Build query for cohort members with completed profiles
        query = db.query(CandidateVerticalProfile.best_score).join(
            Candidate, CandidateVerticalProfile.candidate_id == Candidate.id
        ).filter(
            Candidate.university == university,
            Candidate.graduation_year == graduation_year,
            CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED,
            CandidateVerticalProfile.best_score.isnot(None),
        )

        # Filter by vertical if provided
        if vertical:
            query = query.filter(CandidateVerticalProfile.vertical == vertical)

        # Get all scores in cohort
        scores = [row[0] for row in query.all()]
        cohort_size = len(scores)

        # Need at least 3 people for meaningful percentile
        if cohort_size < 3:
            return None, None, cohort_size

        # Calculate percentile (percentage of scores this candidate beats)
        scores_below = sum(1 for s in scores if s < score)
        percentile = int((scores_below / cohort_size) * 100)

        # Clamp to 1-99 (avoid claiming "top 0%" or "top 100%")
        percentile = max(1, min(99, percentile))

        # Generate cohort label
        # Shorten university name if needed
        short_university = self._shorten_university(university)
        cohort_label = f"{short_university} {graduation_year}"

        return percentile, cohort_label, cohort_size

    def get_cohort_badge(
        self,
        score: float,
        university: Optional[str],
        graduation_year: Optional[int],
        vertical: Optional[Vertical],
        db: Session,
    ) -> Optional[Dict]:
        """
        Get a cohort badge for display (e.g., "Top 10% of Berkeley 2026").

        Args:
            score: Candidate's best score
            university: Candidate's university
            graduation_year: Candidate's graduation year
            vertical: Career vertical
            db: Database session

        Returns:
            Dict with badge info or None if not applicable
        """
        percentile, cohort_label, cohort_size = self.calculate_percentile(
            score, university, graduation_year, vertical, db
        )

        if percentile is None:
            return None

        # Only show badge for top performers (top 50%)
        if percentile < 50:
            return None

        # Calculate "top X%" (inverse of percentile)
        top_percent = 100 - percentile

        return {
            "percentile": percentile,
            "top_percent": top_percent,
            "cohort_label": cohort_label,
            "cohort_size": cohort_size,
            "badge_text": f"Top {top_percent}% of {cohort_label}",
        }

    def calculate_percentile_by_year(
        self,
        score: float,
        graduation_year: Optional[int],
        vertical: Optional[Vertical],
        db: Session,
    ) -> Tuple[Optional[int], Optional[str], int]:
        """
        Calculate a candidate's percentile within their graduation year cohort (all universities).

        This is used when university-specific cohort is too small or not available.

        Args:
            score: Candidate's best score (0-10)
            graduation_year: Candidate's graduation year
            vertical: Career vertical (engineering, data, etc.)
            db: Database session

        Returns:
            Tuple of (percentile 1-100, cohort_label, cohort_size)
        """
        if not score or not graduation_year:
            return None, None, 0

        # Build query for all candidates in this graduation year with completed profiles
        query = db.query(CandidateVerticalProfile.best_score).join(
            Candidate, CandidateVerticalProfile.candidate_id == Candidate.id
        ).filter(
            Candidate.graduation_year == graduation_year,
            CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED,
            CandidateVerticalProfile.best_score.isnot(None),
        )

        # Filter by vertical if provided
        if vertical:
            query = query.filter(CandidateVerticalProfile.vertical == vertical)

        # Get all scores in cohort
        scores = [row[0] for row in query.all()]
        cohort_size = len(scores)

        # Need at least 3 people for meaningful percentile
        if cohort_size < 3:
            return None, None, cohort_size

        # Calculate percentile (percentage of scores this candidate beats)
        scores_below = sum(1 for s in scores if s < score)
        percentile = int((scores_below / cohort_size) * 100)

        # Clamp to 1-99
        percentile = max(1, min(99, percentile))

        # Generate cohort label
        cohort_label = f"Class of {graduation_year}"

        return percentile, cohort_label, cohort_size

    def get_best_cohort_badge(
        self,
        score: float,
        university: Optional[str],
        graduation_year: Optional[int],
        vertical: Optional[Vertical],
        db: Session,
    ) -> Optional[Dict]:
        """
        Get the best cohort badge - tries university+year first, then year only.

        Args:
            score: Candidate's best score
            university: Candidate's university (optional)
            graduation_year: Candidate's graduation year
            vertical: Career vertical
            db: Database session

        Returns:
            Dict with badge info or None if not applicable
        """
        # Try university-specific cohort first
        if university and graduation_year:
            badge = self.get_cohort_badge(score, university, graduation_year, vertical, db)
            if badge:
                return badge

        # Fall back to graduation year only
        if graduation_year:
            percentile, cohort_label, cohort_size = self.calculate_percentile_by_year(
                score, graduation_year, vertical, db
            )

            if percentile is None or percentile < 50:
                return None

            top_percent = 100 - percentile

            return {
                "percentile": percentile,
                "top_percent": top_percent,
                "cohort_label": cohort_label,
                "cohort_size": cohort_size,
                "badge_text": f"Top {top_percent}% of {cohort_label}",
            }

        return None

    def get_cohort_stats(
        self,
        university: str,
        graduation_year: int,
        vertical: Optional[Vertical],
        db: Session,
    ) -> Dict:
        """
        Get aggregate statistics for a cohort.

        Args:
            university: University name
            graduation_year: Graduation year
            vertical: Career vertical (optional)
            db: Database session

        Returns:
            Dict with cohort statistics
        """
        query = db.query(
            func.count(CandidateVerticalProfile.id).label("count"),
            func.avg(CandidateVerticalProfile.best_score).label("avg_score"),
            func.max(CandidateVerticalProfile.best_score).label("max_score"),
            func.min(CandidateVerticalProfile.best_score).label("min_score"),
        ).join(
            Candidate, CandidateVerticalProfile.candidate_id == Candidate.id
        ).filter(
            Candidate.university == university,
            Candidate.graduation_year == graduation_year,
            CandidateVerticalProfile.status == VerticalProfileStatus.COMPLETED,
            CandidateVerticalProfile.best_score.isnot(None),
        )

        if vertical:
            query = query.filter(CandidateVerticalProfile.vertical == vertical)

        result = query.first()

        return {
            "university": university,
            "graduation_year": graduation_year,
            "vertical": vertical.value if vertical else "all",
            "candidate_count": result.count or 0,
            "average_score": round(result.avg_score, 2) if result.avg_score else None,
            "highest_score": round(result.max_score, 2) if result.max_score else None,
            "lowest_score": round(result.min_score, 2) if result.min_score else None,
        }

    def _shorten_university(self, university: str) -> str:
        """Shorten common university names for display."""
        abbreviations = {
            "University of California, Berkeley": "Berkeley",
            "UC Berkeley": "Berkeley",
            "University of California Berkeley": "Berkeley",
            "Stanford University": "Stanford",
            "Massachusetts Institute of Technology": "MIT",
            "California Institute of Technology": "Caltech",
            "Carnegie Mellon University": "CMU",
            "University of Michigan": "Michigan",
            "University of Illinois at Urbana-Champaign": "UIUC",
            "University of Illinois Urbana-Champaign": "UIUC",
            "Georgia Institute of Technology": "Georgia Tech",
            "University of Texas at Austin": "UT Austin",
            "University of Washington": "UW",
            "University of Southern California": "USC",
            "University of California, Los Angeles": "UCLA",
            "UC Los Angeles": "UCLA",
            "University of California Los Angeles": "UCLA",
            "University of California, San Diego": "UCSD",
            "University of Pennsylvania": "Penn",
            "University of California, Davis": "UC Davis",
            "University of California, Irvine": "UC Irvine",
            "New York University": "NYU",
            "Cornell University": "Cornell",
            "Columbia University": "Columbia",
            "Princeton University": "Princeton",
            "Harvard University": "Harvard",
            "Yale University": "Yale",
            "Duke University": "Duke",
            "Northwestern University": "Northwestern",
            "Brown University": "Brown",
            "Dartmouth College": "Dartmouth",
            "Purdue University": "Purdue",
            "University of Wisconsin-Madison": "Wisconsin",
            "Ohio State University": "Ohio State",
            "Pennsylvania State University": "Penn State",
            "University of Maryland": "Maryland",
            "University of Maryland, College Park": "Maryland",
            "University of California, Santa Barbara": "UCSB",
            "UC Santa Barbara": "UCSB",
            "University of Virginia": "UVA",
            "University of North Carolina at Chapel Hill": "UNC",
        }

        # Check for exact match first
        if university in abbreviations:
            return abbreviations[university]

        # Check for partial matches
        university_lower = university.lower()
        for full_name, abbrev in abbreviations.items():
            if full_name.lower() in university_lower:
                return abbrev

        # If no abbreviation found, try to shorten
        # Remove common suffixes
        shortened = university
        for suffix in [" University", " College", " Institute of Technology"]:
            if shortened.endswith(suffix):
                shortened = shortened[:-len(suffix)]
                break

        # If still too long, just use first word
        if len(shortened) > 20:
            shortened = shortened.split()[0]

        return shortened


# Global instance
cohort_service = CohortService()
