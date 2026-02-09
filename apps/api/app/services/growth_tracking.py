"""
Growth Tracking Service for tracking student progress over time.
Handles resume versioning, GitHub analysis history, and profile change logging.
"""
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import desc

from ..models.resume_version import ResumeVersion
from ..models.github_analysis_history import GitHubAnalysisHistory
from ..models.profile_change_log import ProfileChangeLog, ProfileChangeType
from ..models.candidate import Candidate, InterviewHistoryEntry
from ..models.github_analysis import GitHubAnalysis
from ..utils.date_parser import parse_date_string, format_relative_date

logger = logging.getLogger("pathway.growth_tracking")


def generate_cuid(prefix: str) -> str:
    """Generate a CUID with the given prefix."""
    return f"{prefix}{uuid.uuid4().hex[:24]}"


class GrowthTrackingService:
    """Service for tracking student growth over time."""

    @staticmethod
    def create_resume_version(
        db: Session,
        candidate_id: str,
        storage_key: str,
        raw_text: Optional[str],
        parsed_data: Optional[Dict],
        original_filename: Optional[str] = None,
        file_size_bytes: Optional[int] = None,
    ) -> ResumeVersion:
        """
        Create a new resume version, marking previous as non-current.
        Computes deltas from the previous version.

        Args:
            db: Database session
            candidate_id: Candidate ID
            storage_key: R2 storage key for the resume file
            raw_text: Extracted raw text from resume
            parsed_data: Parsed structured data from resume
            original_filename: Original filename
            file_size_bytes: File size in bytes

        Returns:
            The newly created ResumeVersion
        """
        # Get previous version for delta computation
        previous_version = db.query(ResumeVersion).filter(
            ResumeVersion.candidate_id == candidate_id,
            ResumeVersion.is_current == True
        ).first()

        # Compute version number
        version_number = 1
        if previous_version:
            version_number = previous_version.version_number + 1
            # Mark previous as non-current
            previous_version.is_current = False

        # Compute deltas
        skills_added = []
        skills_removed = []
        projects_added = 0
        experience_added = 0

        if previous_version and previous_version.parsed_data and parsed_data:
            prev_skills = set(previous_version.parsed_data.get("skills", []))
            new_skills = set(parsed_data.get("skills", []))
            skills_added = list(new_skills - prev_skills)
            skills_removed = list(prev_skills - new_skills)

            prev_projects = len(previous_version.parsed_data.get("projects", []))
            new_projects = len(parsed_data.get("projects", []))
            projects_added = max(0, new_projects - prev_projects)

            prev_experience = len(previous_version.parsed_data.get("experience", []))
            new_experience = len(parsed_data.get("experience", []))
            experience_added = max(0, new_experience - prev_experience)

        # Create new version
        resume_version = ResumeVersion(
            id=generate_cuid("rv"),
            candidate_id=candidate_id,
            version_number=version_number,
            storage_key=storage_key,
            original_filename=original_filename,
            file_size_bytes=file_size_bytes,
            raw_text=raw_text,
            parsed_data=parsed_data,
            skills_added=skills_added if skills_added else None,
            skills_removed=skills_removed if skills_removed else None,
            projects_added=projects_added if projects_added > 0 else None,
            experience_added=experience_added if experience_added > 0 else None,
            is_current=True,
        )

        db.add(resume_version)
        db.commit()
        db.refresh(resume_version)

        logger.info(f"Created resume version {version_number} for candidate {candidate_id}")
        return resume_version

    @staticmethod
    def create_github_analysis_snapshot(
        db: Session,
        candidate_id: str,
        analysis: GitHubAnalysis,
    ) -> GitHubAnalysisHistory:
        """
        Create a snapshot of GitHub analysis for history tracking.
        Computes delta from previous snapshot.

        Args:
            db: Database session
            candidate_id: Candidate ID
            analysis: The GitHubAnalysis object with current scores

        Returns:
            The newly created GitHubAnalysisHistory entry
        """
        # Get previous snapshot for delta computation
        previous_snapshot = db.query(GitHubAnalysisHistory).filter(
            GitHubAnalysisHistory.candidate_id == candidate_id
        ).order_by(desc(GitHubAnalysisHistory.analyzed_at)).first()

        # Compute deltas
        score_delta = None
        repos_delta = None

        if previous_snapshot:
            if previous_snapshot.overall_score is not None and analysis.overall_score is not None:
                score_delta = analysis.overall_score - previous_snapshot.overall_score
            if previous_snapshot.total_repos_analyzed is not None and analysis.total_repos_analyzed is not None:
                repos_delta = analysis.total_repos_analyzed - previous_snapshot.total_repos_analyzed

        # Create snapshot
        snapshot = GitHubAnalysisHistory(
            id=generate_cuid("gah"),
            candidate_id=candidate_id,
            github_analysis_id=analysis.id,
            overall_score=analysis.overall_score,
            originality_score=analysis.originality_score,
            activity_score=analysis.activity_score,
            depth_score=analysis.depth_score,
            collaboration_score=analysis.collaboration_score,
            total_repos_analyzed=analysis.total_repos_analyzed,
            total_commits_by_user=analysis.total_commits_by_user,
            primary_languages=analysis.primary_languages,
            score_delta=score_delta,
            repos_delta=repos_delta,
        )

        db.add(snapshot)
        db.commit()
        db.refresh(snapshot)

        logger.info(
            f"Created GitHub analysis snapshot for candidate {candidate_id}: "
            f"score={analysis.overall_score}, delta={score_delta}"
        )
        return snapshot

    @staticmethod
    def log_profile_change(
        db: Session,
        candidate_id: str,
        change_type: str,
        field_name: str,
        old_value: Any,
        new_value: Any,
        change_source: str = "manual",
    ) -> ProfileChangeLog:
        """
        Log a profile field change.

        Args:
            db: Database session
            candidate_id: Candidate ID
            change_type: Type of change (from ProfileChangeType)
            field_name: Specific field that changed
            old_value: Previous value
            new_value: New value
            change_source: Source of change (manual, resume_parse, transcript_verify)

        Returns:
            The newly created ProfileChangeLog entry
        """
        # Convert values to JSON-serializable format
        def to_json_value(val):
            if val is None:
                return None
            if isinstance(val, (str, int, float, bool, list, dict)):
                return val
            return str(val)

        change_log = ProfileChangeLog(
            id=generate_cuid("pcl"),
            candidate_id=candidate_id,
            change_type=change_type,
            field_name=field_name,
            old_value=to_json_value(old_value),
            new_value=to_json_value(new_value),
            change_source=change_source,
        )

        db.add(change_log)
        db.commit()
        db.refresh(change_log)

        logger.info(
            f"Logged profile change for candidate {candidate_id}: "
            f"{change_type} {field_name} from {old_value} to {new_value}"
        )
        return change_log

    @staticmethod
    def get_growth_timeline(
        db: Session,
        candidate_id: str,
        time_range: str = "1y",
    ) -> Dict[str, Any]:
        """
        Get growth timeline for a candidate.

        Args:
            db: Database session
            candidate_id: Candidate ID
            time_range: Time range filter ("6m", "1y", "2y", "all")

        Returns:
            Dictionary with summary and events
        """
        # Determine date cutoff
        cutoff_date = None
        if time_range == "6m":
            cutoff_date = datetime.utcnow() - timedelta(days=180)
        elif time_range == "1y":
            cutoff_date = datetime.utcnow() - timedelta(days=365)
        elif time_range == "2y":
            cutoff_date = datetime.utcnow() - timedelta(days=730)
        # "all" means no cutoff

        # Get candidate
        candidate = db.query(Candidate).filter(Candidate.id == candidate_id).first()
        if not candidate:
            return {"error": "Candidate not found"}

        events = []

        # Get interview history
        interview_query = db.query(InterviewHistoryEntry).filter(
            InterviewHistoryEntry.candidate_id == candidate_id
        )
        if cutoff_date:
            interview_query = interview_query.filter(InterviewHistoryEntry.completed_at >= cutoff_date)
        interviews = interview_query.order_by(desc(InterviewHistoryEntry.completed_at)).all()

        for i, interview in enumerate(interviews):
            delta = None
            if i < len(interviews) - 1:
                prev_interview = interviews[i + 1]
                if interview.overall_score and prev_interview.overall_score:
                    delta = round(interview.overall_score - prev_interview.overall_score, 1)

            events.append({
                "event_type": "interview",
                "event_date": interview.completed_at.isoformat() if interview.completed_at else None,
                "title": f"Completed Interview #{len(interviews) - i}",
                "subtitle": f"Score: {interview.overall_score:.1f}" if interview.overall_score else None,
                "delta": delta,
                "icon": "interview",
            })

        # Get resume versions
        resume_query = db.query(ResumeVersion).filter(
            ResumeVersion.candidate_id == candidate_id
        )
        if cutoff_date:
            resume_query = resume_query.filter(ResumeVersion.uploaded_at >= cutoff_date)
        resume_versions = resume_query.order_by(desc(ResumeVersion.uploaded_at)).all()

        for rv in resume_versions:
            subtitle_parts = []
            if rv.skills_added:
                subtitle_parts.append(f"+{len(rv.skills_added)} skills")
            if rv.projects_added:
                subtitle_parts.append(f"+{rv.projects_added} project{'s' if rv.projects_added > 1 else ''}")
            if rv.experience_added:
                subtitle_parts.append(f"+{rv.experience_added} experience")

            events.append({
                "event_type": "resume",
                "event_date": rv.uploaded_at.isoformat() if rv.uploaded_at else None,
                "title": f"Resume Updated (v{rv.version_number})",
                "subtitle": ", ".join(subtitle_parts) if subtitle_parts else None,
                "delta": None,
                "icon": "document",
            })

        # Get GitHub analysis history
        github_query = db.query(GitHubAnalysisHistory).filter(
            GitHubAnalysisHistory.candidate_id == candidate_id
        )
        if cutoff_date:
            github_query = github_query.filter(GitHubAnalysisHistory.analyzed_at >= cutoff_date)
        github_history = github_query.order_by(desc(GitHubAnalysisHistory.analyzed_at)).all()

        for gh in github_history:
            events.append({
                "event_type": "github",
                "event_date": gh.analyzed_at.isoformat() if gh.analyzed_at else None,
                "title": "GitHub Analysis Updated",
                "subtitle": f"Score: {gh.overall_score:.0f}" if gh.overall_score else None,
                "delta": round(gh.score_delta, 0) if gh.score_delta else None,
                "icon": "github",
            })

        # Get profile changes (only significant ones)
        change_query = db.query(ProfileChangeLog).filter(
            ProfileChangeLog.candidate_id == candidate_id,
            ProfileChangeLog.change_type.in_([
                ProfileChangeType.GPA_UPDATE.value,
                ProfileChangeType.MAJOR_CHANGE.value,
                ProfileChangeType.ACTIVITY_ADDED.value,
                ProfileChangeType.AWARD_ADDED.value,
            ])
        )
        if cutoff_date:
            change_query = change_query.filter(ProfileChangeLog.changed_at >= cutoff_date)
        profile_changes = change_query.order_by(desc(ProfileChangeLog.changed_at)).all()

        for pc in profile_changes:
            title_map = {
                ProfileChangeType.GPA_UPDATE.value: "GPA Updated",
                ProfileChangeType.MAJOR_CHANGE.value: "Major Changed",
                ProfileChangeType.ACTIVITY_ADDED.value: "Activity Added",
                ProfileChangeType.AWARD_ADDED.value: "Award Added",
            }
            events.append({
                "event_type": "profile",
                "event_date": pc.changed_at.isoformat() if pc.changed_at else None,
                "title": title_map.get(pc.change_type, "Profile Updated"),
                "subtitle": str(pc.new_value) if pc.new_value else None,
                "delta": None,
                "icon": "profile",
            })

        # Sort all events by date (newest first)
        events.sort(key=lambda x: x["event_date"] or "", reverse=True)

        # Compute summary
        total_interviews = len(interviews)
        interview_score_change = None
        if len(interviews) >= 2:
            first_score = interviews[-1].overall_score
            latest_score = interviews[0].overall_score
            if first_score and latest_score:
                interview_score_change = round(latest_score - first_score, 1)

        github_connected = bool(candidate.github_username)
        github_score_change = None
        if len(github_history) >= 2:
            first_gh = github_history[-1]
            latest_gh = github_history[0]
            if first_gh.overall_score and latest_gh.overall_score:
                github_score_change = round(latest_gh.overall_score - first_gh.overall_score, 0)

        resume_versions_count = len(resume_versions)
        skills_growth_count = sum(
            len(rv.skills_added or []) for rv in resume_versions
        )

        return {
            "candidate_id": candidate_id,
            "candidate_name": candidate.name,
            "summary": {
                "total_interviews": total_interviews,
                "interview_score_change": interview_score_change,
                "github_connected": github_connected,
                "github_score_change": github_score_change,
                "resume_versions_count": resume_versions_count,
                "skills_growth_count": skills_growth_count,
            },
            "events": events,
        }


# Singleton instance
growth_tracking_service = GrowthTrackingService()
