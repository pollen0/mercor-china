from .candidate import Candidate, CandidateVerticalProfile, VerticalProfileStatus, InterviewHistoryEntry
from .employer import Employer, Job, InterviewQuestion, InviteToken, Vertical, RoleType, CandidateQuestionHistory
from .profile_token import ProfileToken
from .interview import InterviewSession, InterviewResponse, Match, InterviewStatus, MatchStatus, FollowupQueue, FollowupQueueStatus
from .message import Message, MessageType
from .coding_challenge import CodingChallenge
from .github_analysis import GitHubAnalysis, ProjectType, CodeOriginSignal
from .course import (
    University, Course, CourseGradeMapping, DifficultyTier, CourseType,
    CandidateTranscript, CandidateCourseGrade
)
from .activity import (
    Club, CandidateActivity, CandidateAward,
    ActivityTier, ActivityCategory
)
from .ml_scoring import (
    # Enums
    ScoringEventType, LabelSource, OutcomeType, OutcomeStage, CompanyTier, ExperimentStatus,
    # Core ML tables
    ScoringEvent, ScoringLabel, LabelingTask, CandidateOutcome,
    # Detailed analysis tables
    InterviewTranscriptML, GitHubAnalysisML, ResumeAnalysisML, TranscriptAnalysisML,
    # Unified scoring
    UnifiedCandidateScore,
    # Experiments and training
    MLExperiment, MLTrainingRun, ScoreCalibration
)

__all__ = [
    "Candidate",
    "CandidateVerticalProfile",
    "VerticalProfileStatus",
    "InterviewHistoryEntry",
    "Employer",
    "Job",
    "InterviewQuestion",
    "CandidateQuestionHistory",
    "InviteToken",
    "InterviewSession",
    "InterviewResponse",
    "Match",
    "InterviewStatus",
    "MatchStatus",
    "FollowupQueue",
    "FollowupQueueStatus",
    "Vertical",
    "RoleType",
    "Message",
    "MessageType",
    "CodingChallenge",
    "GitHubAnalysis",
    "ProjectType",
    "CodeOriginSignal",
    # Course database
    "University",
    "Course",
    "CourseGradeMapping",
    "DifficultyTier",
    "CourseType",
    "CandidateTranscript",
    "CandidateCourseGrade",
    # Activity/club database
    "Club",
    "CandidateActivity",
    "CandidateAward",
    "ActivityTier",
    "ActivityCategory",
    # ML Scoring infrastructure
    "ScoringEventType",
    "LabelSource",
    "OutcomeType",
    "OutcomeStage",
    "CompanyTier",
    "ExperimentStatus",
    "ScoringEvent",
    "ScoringLabel",
    "LabelingTask",
    "CandidateOutcome",
    "InterviewTranscriptML",
    "GitHubAnalysisML",
    "ResumeAnalysisML",
    "TranscriptAnalysisML",
    "UnifiedCandidateScore",
    "MLExperiment",
    "MLTrainingRun",
    "ScoreCalibration",
    # Profile sharing
    "ProfileToken",
]
