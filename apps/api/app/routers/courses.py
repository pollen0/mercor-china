"""
Course management and transcript analysis API endpoints.
Includes admin endpoints for course difficulty management.
"""

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Query, Header, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid

from ..database import get_db
from ..models.course import University, Course, CandidateTranscript, CandidateCourseGrade
from ..models.candidate import Candidate
from ..services.transcript import transcript_service
from ..services.candidate_scoring import candidate_scoring_service
from ..data.seed_courses import get_all_courses, get_all_universities
from ..utils.auth import get_current_candidate

# Use the same verify_admin from admin router
from .admin import verify_admin


router = APIRouter()


# ============= Pydantic Models =============

class UniversityResponse(BaseModel):
    id: str
    name: str
    short_name: str
    gpa_scale: float
    uses_plus_minus: bool = True
    tier: int
    cs_ranking: Optional[int]


class UniversityDetailResponse(BaseModel):
    id: str
    name: str
    short_name: str
    gpa_scale: float
    uses_plus_minus: bool
    tier: int
    cs_ranking: Optional[int]
    course_count: int = 0
    club_count: int = 0


class CourseResponse(BaseModel):
    id: str
    university_id: str
    department: str
    number: str
    name: str
    difficulty_tier: int
    difficulty_score: float
    typical_gpa: Optional[float]
    is_curved: bool
    course_type: str
    is_technical: bool
    is_weeder: bool
    is_proof_based: bool
    has_coding: bool
    units: int
    description: Optional[str]
    confidence: float
    source: Optional[str]


class CourseUpdate(BaseModel):
    name: Optional[str] = None
    difficulty_tier: Optional[int] = None
    difficulty_score: Optional[float] = None
    typical_gpa: Optional[float] = None
    is_curved: Optional[bool] = None
    is_weeder: Optional[bool] = None
    is_proof_based: Optional[bool] = None
    has_coding: Optional[bool] = None
    description: Optional[str] = None
    notes: Optional[str] = None


class CourseCreate(BaseModel):
    university_id: str
    department: str
    number: str
    name: str
    aliases: Optional[List[str]] = None
    difficulty_tier: int = 2
    difficulty_score: float = 5.0
    typical_gpa: Optional[float] = None
    is_curved: bool = False
    course_type: str = "elective"
    is_technical: bool = True
    is_weeder: bool = False
    is_proof_based: bool = False
    has_coding: bool = False
    units: int = 3
    description: Optional[str] = None


class TranscriptScoreResponse(BaseModel):
    overall_score: float
    course_rigor_score: float
    performance_score: float
    trajectory_score: float
    load_score: float
    achievement_score: float
    gpa: Optional[float]
    technical_gpa: Optional[float]
    total_units: int
    technical_units: int
    strengths: List[str]
    concerns: List[str]
    achievements: List[str]


class UnifiedScoreResponse(BaseModel):
    overall_score: float
    overall_grade: str
    interview_score: Optional[float]
    github_score: Optional[float]
    transcript_score: Optional[float]
    resume_score: Optional[float]
    data_completeness: float
    confidence: float
    top_strengths: List[str]
    key_concerns: List[str]
    role_fit_scores: dict


# ============= Public Course Endpoints =============

@router.get("/universities", response_model=List[UniversityResponse])
async def list_universities(db: Session = Depends(get_db)):
    """List all universities in the database."""
    universities = db.query(University).order_by(University.tier, University.name).all()
    return universities


@router.get("/universities/detailed", response_model=List[UniversityDetailResponse])
async def list_universities_detailed(db: Session = Depends(get_db)):
    """List all universities with course and club counts."""
    from ..models.activity import Club

    universities = db.query(University).order_by(University.cs_ranking.asc().nullslast(), University.name).all()
    result = []
    for uni in universities:
        course_count = db.query(Course).filter(Course.university_id == uni.id).count()
        club_count = db.query(Club).filter(Club.university_id == uni.id).count()
        result.append(UniversityDetailResponse(
            id=uni.id,
            name=uni.name,
            short_name=uni.short_name,
            gpa_scale=uni.gpa_scale,
            uses_plus_minus=uni.uses_plus_minus,
            tier=uni.tier,
            cs_ranking=uni.cs_ranking,
            course_count=course_count,
            club_count=club_count,
        ))
    return result


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(
    university_id: Optional[str] = None,
    department: Optional[str] = None,
    difficulty_min: Optional[int] = None,
    difficulty_max: Optional[int] = None,
    is_technical: Optional[bool] = None,
    limit: int = Query(100, le=500),
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """
    List courses with optional filters.
    Used by admin portal to view/search courses.
    """
    query = db.query(Course)

    if university_id:
        query = query.filter(Course.university_id == university_id)
    if department:
        query = query.filter(Course.department == department.upper())
    if difficulty_min is not None:
        query = query.filter(Course.difficulty_tier >= difficulty_min)
    if difficulty_max is not None:
        query = query.filter(Course.difficulty_tier <= difficulty_max)
    if is_technical is not None:
        query = query.filter(Course.is_technical == is_technical)

    courses = query.order_by(
        Course.university_id,
        Course.department,
        Course.number
    ).offset(offset).limit(limit).all()

    return courses


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, db: Session = Depends(get_db)):
    """Get a specific course by ID."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


# ============= Admin Course Management =============

@router.post("/admin/courses", response_model=CourseResponse)
async def create_course(
    data: CourseCreate,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Create a new course (admin only)."""
    # Generate course ID
    course_id = f"{data.university_id}_{data.department.lower()}{data.number.lower()}"

    # Check if exists
    existing = db.query(Course).filter(Course.id == course_id).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course already exists")

    course = Course(
        id=course_id,
        university_id=data.university_id,
        department=data.department.upper(),
        number=data.number.upper(),
        name=data.name,
        aliases=data.aliases or [f"{data.department.upper()} {data.number.upper()}"],
        difficulty_tier=data.difficulty_tier,
        difficulty_score=data.difficulty_score,
        typical_gpa=data.typical_gpa,
        is_curved=data.is_curved,
        course_type=data.course_type,
        is_technical=data.is_technical,
        is_weeder=data.is_weeder,
        is_proof_based=data.is_proof_based,
        has_coding=data.has_coding,
        units=data.units,
        description=data.description,
        confidence=0.8,  # Manual entry
        source="manual"
    )

    db.add(course)
    db.commit()
    db.refresh(course)

    return course


@router.patch("/admin/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    data: CourseUpdate,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Update a course's difficulty or metadata (admin only)."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Update fields
    update_data = data.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(course, field, value)

    course.updated_at = datetime.utcnow()
    course.last_verified_at = datetime.utcnow()

    db.commit()
    db.refresh(course)

    return course


@router.delete("/admin/courses/{course_id}")
async def delete_course(
    course_id: str,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Delete a course (admin only)."""
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()

    return {"success": True, "message": f"Course {course_id} deleted"}


@router.post("/admin/courses/seed")
async def seed_courses(
    admin=Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Seed the database with initial course data (admin only)."""
    # Seed universities
    universities = get_all_universities()
    added_universities = 0
    for uni_data in universities:
        existing = db.query(University).filter(University.id == uni_data["id"]).first()
        if not existing:
            university = University(**uni_data)
            db.add(university)
            added_universities += 1

    # Seed courses (filter to valid model columns only)
    from sqlalchemy import inspect as sa_inspect
    valid_keys = {c.key for c in sa_inspect(Course).column_attrs}
    courses = get_all_courses()
    added_courses = 0
    for course_data in courses:
        existing = db.query(Course).filter(Course.id == course_data["id"]).first()
        if not existing:
            filtered = {k: v for k, v in course_data.items() if k in valid_keys}
            course = Course(**filtered)
            db.add(course)
            added_courses += 1

    db.commit()

    return {
        "success": True,
        "universities_added": added_universities,
        "courses_added": added_courses
    }


@router.get("/admin/courses/stats")
async def get_course_stats(
    admin=Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Get statistics about the course database."""
    total_courses = db.query(Course).count()
    total_universities = db.query(University).count()

    # Count by difficulty tier
    tier_counts = {}
    for tier in range(1, 6):
        count = db.query(Course).filter(Course.difficulty_tier == tier).count()
        tier_counts[f"tier_{tier}"] = count

    # Count by university
    uni_counts = db.query(
        Course.university_id,
        db.query(Course).filter(Course.university_id == Course.university_id).count()
    ).distinct().all()

    return {
        "total_courses": total_courses,
        "total_universities": total_universities,
        "by_difficulty_tier": tier_counts,
        "by_university": {u[0]: u[1] for u in uni_counts} if uni_counts else {}
    }


# ============= Transcript Endpoints =============

@router.post("/me/transcript/upload")
async def upload_transcript(
    file: UploadFile = File(...),
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """
    Upload and analyze a transcript PDF.
    Parses courses, grades, and calculates transcript score.
    """
    # Get filename
    filename = file.filename or "transcript.pdf"

    # Read file
    file_bytes = await file.read()

    # Comprehensive file validation (extension, size, and magic bytes)
    from ..utils.file_validation import validate_transcript_file
    is_valid, error = validate_transcript_file(file_bytes, filename)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error)

    # Extract text from PDF
    try:
        raw_text = transcript_service.extract_text_from_pdf(file_bytes)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to read PDF: {str(e)}")

    if not raw_text or len(raw_text) < 100:
        raise HTTPException(status_code=400, detail="Could not extract text from PDF")

    # Parse transcript using AI
    parsed = await transcript_service.parse_transcript(raw_text)

    if not parsed.courses:
        raise HTTPException(
            status_code=400,
            detail="Could not parse any courses from transcript. Please ensure it's a valid academic transcript."
        )

    # Score the transcript
    score = await transcript_service.score_transcript(parsed, db)

    # Upload file to R2 storage
    file_url = None
    try:
        from ..services.storage import storage_service
        from ..config import settings
        from io import BytesIO
        timestamp = datetime.utcnow().strftime("%Y%m%d")
        unique_id = uuid.uuid4().hex[:8]
        storage_key = f"transcripts/{candidate.id}/{timestamp}_{unique_id}.pdf"
        storage_service.client.upload_fileobj(
            BytesIO(file_bytes),
            settings.r2_bucket_name,
            storage_key,
            ExtraArgs={"ContentType": "application/pdf"}
        )
        file_url = storage_key
    except Exception:
        # Storage upload failed — continue without persisting the file
        # The parsed data is still saved to the database
        pass

    # Create or update transcript record
    existing = db.query(CandidateTranscript).filter(
        CandidateTranscript.candidate_id == candidate.id
    ).first()

    if existing:
        transcript = existing
    else:
        transcript = CandidateTranscript(
            id=str(uuid.uuid4()),
            candidate_id=candidate.id
        )
        db.add(transcript)

    # Update transcript data
    transcript.file_url = file_url
    transcript.university_id = transcript_service._get_university_id(parsed.university or "")
    transcript.cumulative_gpa = parsed.cumulative_gpa or score.gpa
    transcript.major_gpa = score.technical_gpa

    # Store parsed courses as JSON with edge case tracking
    transcript.parsed_courses = [
        {
            "code": c.code,
            "name": c.name,
            "grade": c.grade,
            "units": c.units,
            "semester": c.semester,
            "year": c.year,
            "is_graduate": c.is_graduate,
            "is_pass_fail": c.is_pass_fail,
            "is_transfer": c.is_transfer,
            "is_ap": c.is_ap,
            "student_year": c.student_year
        }
        for c in parsed.courses
    ]

    # Store scores
    transcript.transcript_score = score.overall_score
    transcript.course_rigor_score = score.course_rigor_score
    transcript.performance_score = score.performance_score
    transcript.trajectory_score = score.trajectory_score
    transcript.load_score = score.load_score
    transcript.score_breakdown = score.breakdown
    transcript.score_breakdown["strengths"] = score.strengths
    transcript.score_breakdown["concerns"] = score.concerns
    transcript.score_breakdown["achievements"] = score.achievements

    transcript.semesters_analyzed = len(parsed.semesters)
    transcript.total_units = score.total_units
    transcript.technical_units = score.technical_units

    transcript.analyzed_at = datetime.utcnow()

    # Update candidate's education info if parsed
    if parsed.university:
        candidate.university = parsed.university
    if parsed.major:
        candidate.major = parsed.major
    if parsed.majors:
        candidate.majors = parsed.majors
    if parsed.minors:
        candidate.minors = parsed.minors
    if parsed.graduation_year:
        candidate.graduation_year = parsed.graduation_year
    if score.gpa:
        candidate.gpa = score.gpa
    if score.technical_gpa:
        candidate.major_gpa = score.technical_gpa
    # Transfer student info
    if parsed.is_transfer:
        candidate.is_transfer = True
        candidate.transfer_university = parsed.transfer_university
    if parsed.ap_credits:
        candidate.ap_credits = parsed.ap_credits

    db.commit()

    return {
        "success": True,
        "transcript_id": transcript.id,
        "university": parsed.university,
        "majors": parsed.majors,
        "minors": parsed.minors,
        "is_transfer": parsed.is_transfer,
        "ap_credits": len(parsed.ap_credits),
        "courses_found": len(parsed.courses),
        "semesters": len(parsed.semesters),
        "scores": {
            "overall": score.overall_score,
            "course_rigor": score.course_rigor_score,
            "performance": score.performance_score,
            "trajectory": score.trajectory_score,
            "load": score.load_score,
            "achievement": score.achievement_score
        },
        "gpa": score.gpa,
        "technical_gpa": score.technical_gpa,
        "strengths": score.strengths[:5],
        "achievements": score.achievements[:5]
    }


@router.get("/me/transcript", response_model=Optional[TranscriptScoreResponse])
async def get_my_transcript(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get current candidate's transcript analysis."""
    transcript = db.query(CandidateTranscript).filter(
        CandidateTranscript.candidate_id == candidate.id
    ).first()

    if not transcript or transcript.transcript_score is None:
        return None

    breakdown = transcript.score_breakdown or {}

    return TranscriptScoreResponse(
        overall_score=transcript.transcript_score,
        course_rigor_score=transcript.course_rigor_score or 0,
        performance_score=transcript.performance_score or 0,
        trajectory_score=transcript.trajectory_score or 0,
        load_score=transcript.load_score or 0,
        achievement_score=breakdown.get("achievements", []) and 70 or 50,
        gpa=transcript.cumulative_gpa,
        technical_gpa=transcript.major_gpa,
        total_units=transcript.total_units or 0,
        technical_units=transcript.technical_units or 0,
        strengths=breakdown.get("strengths", []),
        concerns=breakdown.get("concerns", []),
        achievements=breakdown.get("achievements", [])
    )


# ============= Unified Scoring Endpoints =============

@router.get("/me/unified-score", response_model=UnifiedScoreResponse)
async def get_my_unified_score(
    role_type: Optional[str] = None,
    vertical: Optional[str] = None,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """
    Get unified candidate score combining all signals.
    Optionally filter by target role/vertical for role-specific fit.
    """
    score = candidate_scoring_service.calculate_unified_score(
        candidate=candidate,
        db=db,
        role_type=role_type,
        vertical=vertical
    )

    return UnifiedScoreResponse(
        overall_score=score.overall_score,
        overall_grade=score.overall_grade,
        interview_score=score.interview.score if score.interview.available else None,
        github_score=score.github.score if score.github.available else None,
        transcript_score=score.transcript.score if score.transcript.available else None,
        resume_score=score.resume.score if score.resume.available else None,
        data_completeness=score.data_completeness,
        confidence=score.confidence,
        top_strengths=score.top_strengths,
        key_concerns=score.key_concerns,
        role_fit_scores=score.role_fit_scores
    )


# ============= Research Unknown Courses =============

@router.post("/courses/research")
async def research_course(
    course_code: str,
    university: str,
    admin=Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """
    Research an unknown course to estimate its difficulty.
    Uses AI to gather information about the course.
    """
    result = await transcript_service.research_unknown_course(course_code, university)

    return {
        "course_code": course_code,
        "university": university,
        **result
    }
