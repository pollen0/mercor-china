"""
Activity and club management API endpoints.
Includes endpoints for browsing clubs and managing candidate activities.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List
from pydantic import BaseModel
from datetime import datetime
import uuid

from ..database import get_db
from ..models.activity import Club, CandidateActivity, CandidateAward
from ..models.candidate import Candidate
from ..utils.auth import get_current_candidate
from ..data.seed_clubs import get_all_clubs
from .admin import verify_admin


router = APIRouter()


# ============= Pydantic Models =============

class ClubResponse(BaseModel):
    id: str
    university_id: str
    name: str
    short_name: Optional[str]
    category: str
    prestige_tier: int
    prestige_score: float
    is_selective: bool
    acceptance_rate: Optional[float]
    is_technical: bool
    is_professional: bool
    has_projects: bool
    has_competitions: bool
    is_honor_society: bool
    description: Optional[str]


class ActivityCreate(BaseModel):
    activity_name: str
    institution: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ActivityUpdate(BaseModel):
    activity_name: Optional[str] = None
    role: Optional[str] = None
    description: Optional[str] = None
    start_date: Optional[str] = None
    end_date: Optional[str] = None


class ActivityResponse(BaseModel):
    id: str
    activity_name: str
    organization: Optional[str]
    institution: Optional[str]
    role: Optional[str]
    role_tier: int
    description: Optional[str]
    start_date: Optional[str]
    end_date: Optional[str]
    activity_score: Optional[float]
    club: Optional[ClubResponse] = None


class AwardCreate(BaseModel):
    name: str
    issuer: Optional[str] = None
    date: Optional[str] = None
    award_type: Optional[str] = None
    description: Optional[str] = None


class AwardResponse(BaseModel):
    id: str
    name: str
    issuer: Optional[str]
    date: Optional[str]
    award_type: Optional[str]
    prestige_tier: int
    description: Optional[str]


# ============= Club Endpoints =============

@router.get("/clubs", response_model=List[ClubResponse])
async def list_clubs(
    university_id: Optional[str] = None,
    category: Optional[str] = None,
    min_prestige: Optional[int] = None,
    is_technical: Optional[bool] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """List clubs with optional filters."""
    query = db.query(Club)

    if university_id:
        query = query.filter(Club.university_id == university_id)
    if category:
        query = query.filter(Club.category == category)
    if min_prestige:
        query = query.filter(Club.prestige_tier >= min_prestige)
    if is_technical is not None:
        query = query.filter(Club.is_technical == is_technical)

    clubs = query.order_by(
        Club.prestige_tier.desc(),
        Club.prestige_score.desc()
    ).offset(offset).limit(limit).all()

    return clubs


@router.get("/clubs/{club_id}", response_model=ClubResponse)
async def get_club(club_id: str, db: Session = Depends(get_db)):
    """Get a specific club by ID."""
    club = db.query(Club).filter(Club.id == club_id).first()
    if not club:
        raise HTTPException(status_code=404, detail="Club not found")
    return club


@router.post("/admin/clubs/seed")
async def seed_clubs(
    admin=Depends(verify_admin),
    db: Session = Depends(get_db)
):
    """Seed the database with club data (admin only)."""
    clubs_data = get_all_clubs()
    added_count = 0

    for club_data in clubs_data:
        existing = db.query(Club).filter(Club.id == club_data["id"]).first()
        if not existing:
            club = Club(
                id=club_data["id"],
                university_id=club_data["university_id"],
                name=club_data["name"],
                short_name=club_data.get("short_name"),
                category=club_data.get("category", "other"),
                aliases=club_data.get("aliases"),
                prestige_tier=club_data["prestige_tier"],
                prestige_score=club_data["prestige_score"],
                is_selective=club_data.get("is_selective", False),
                acceptance_rate=club_data.get("acceptance_rate"),
                typical_members=club_data.get("typical_members"),
                leadership_bonus=club_data.get("leadership_bonus", 1.0),
                is_technical=club_data.get("is_technical", False),
                is_professional=club_data.get("is_professional", False),
                has_projects=club_data.get("has_projects", False),
                has_competitions=club_data.get("has_competitions", False),
                has_corporate_sponsors=club_data.get("has_corporate_sponsors", False),
                is_honor_society=club_data.get("is_honor_society", False),
                relevant_to=club_data.get("relevant_to"),
                description=club_data.get("description"),
                website_url=club_data.get("website_url"),
                notes=club_data.get("notes"),
                confidence=club_data.get("confidence", 1.0),
                source="research",
            )
            db.add(club)
            added_count += 1

    db.commit()

    return {
        "success": True,
        "clubs_added": added_count,
        "total_clubs": db.query(Club).count()
    }


# ============= Candidate Activity Endpoints =============

@router.get("/me/activities", response_model=List[ActivityResponse])
async def get_my_activities(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get current candidate's activities."""
    activities = db.query(CandidateActivity).filter(
        CandidateActivity.candidate_id == candidate.id
    ).all()

    result = []
    for activity in activities:
        club_response = None
        if activity.club:
            club_response = ClubResponse(
                id=activity.club.id,
                university_id=activity.club.university_id,
                name=activity.club.name,
                short_name=activity.club.short_name,
                category=activity.club.category,
                prestige_tier=activity.club.prestige_tier,
                prestige_score=activity.club.prestige_score,
                is_selective=activity.club.is_selective,
                acceptance_rate=activity.club.acceptance_rate,
                is_technical=activity.club.is_technical,
                is_professional=activity.club.is_professional,
                has_projects=activity.club.has_projects,
                has_competitions=activity.club.has_competitions,
                is_honor_society=activity.club.is_honor_society,
                description=activity.club.description,
            )

        result.append(ActivityResponse(
            id=activity.id,
            activity_name=activity.activity_name,
            organization=activity.organization,
            institution=activity.institution,
            role=activity.role,
            role_tier=activity.role_tier,
            description=activity.description,
            start_date=activity.start_date,
            end_date=activity.end_date,
            activity_score=activity.activity_score,
            club=club_response,
        ))

    return result


@router.post("/me/activities", response_model=ActivityResponse)
async def add_activity(
    data: ActivityCreate,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Add an activity to current candidate's profile."""
    # Try to match with a known club
    club_id = None
    club = None
    activity_score = 3.0  # Default score for unknown activities

    if data.institution:
        # Try to find matching club
        university_id = _get_university_id(data.institution)
        if university_id:
            # Search by name similarity
            potential_clubs = db.query(Club).filter(
                Club.university_id == university_id
            ).all()

            for c in potential_clubs:
                if (data.activity_name.lower() in c.name.lower() or
                    (c.short_name and data.activity_name.lower() in c.short_name.lower())):
                    club = c
                    club_id = c.id
                    break

    # Calculate activity score
    if club:
        base_score = club.prestige_score
        role_multiplier = _get_role_multiplier(data.role)
        activity_score = min(10.0, base_score * role_multiplier)

    activity = CandidateActivity(
        id=str(uuid.uuid4()),
        candidate_id=candidate.id,
        club_id=club_id,
        activity_name=data.activity_name,
        institution=data.institution,
        role=data.role,
        role_tier=_get_role_tier(data.role),
        description=data.description,
        start_date=data.start_date,
        end_date=data.end_date,
        activity_score=activity_score,
    )

    db.add(activity)
    db.commit()
    db.refresh(activity)

    club_response = None
    if club:
        club_response = ClubResponse(
            id=club.id,
            university_id=club.university_id,
            name=club.name,
            short_name=club.short_name,
            category=club.category,
            prestige_tier=club.prestige_tier,
            prestige_score=club.prestige_score,
            is_selective=club.is_selective,
            acceptance_rate=club.acceptance_rate,
            is_technical=club.is_technical,
            is_professional=club.is_professional,
            has_projects=club.has_projects,
            has_competitions=club.has_competitions,
            is_honor_society=club.is_honor_society,
            description=club.description,
        )

    return ActivityResponse(
        id=activity.id,
        activity_name=activity.activity_name,
        organization=activity.organization,
        institution=activity.institution,
        role=activity.role,
        role_tier=activity.role_tier,
        description=activity.description,
        start_date=activity.start_date,
        end_date=activity.end_date,
        activity_score=activity.activity_score,
        club=club_response,
    )


@router.delete("/me/activities/{activity_id}")
async def delete_activity(
    activity_id: str,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Delete an activity from current candidate's profile."""
    activity = db.query(CandidateActivity).filter(
        CandidateActivity.id == activity_id,
        CandidateActivity.candidate_id == candidate.id
    ).first()

    if not activity:
        raise HTTPException(status_code=404, detail="Activity not found")

    db.delete(activity)
    db.commit()

    return {"success": True, "deleted_id": activity_id}


# ============= Candidate Award Endpoints =============

@router.get("/me/awards", response_model=List[AwardResponse])
async def get_my_awards(
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Get current candidate's awards."""
    awards = db.query(CandidateAward).filter(
        CandidateAward.candidate_id == candidate.id
    ).all()

    return [
        AwardResponse(
            id=award.id,
            name=award.name,
            issuer=award.issuer,
            date=award.date,
            award_type=award.award_type,
            prestige_tier=award.prestige_tier,
            description=award.description,
        )
        for award in awards
    ]


@router.post("/me/awards", response_model=AwardResponse)
async def add_award(
    data: AwardCreate,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Add an award to current candidate's profile."""
    # Estimate prestige tier based on award type
    prestige_tier = _estimate_award_tier(data.name, data.award_type, data.issuer)

    award = CandidateAward(
        id=str(uuid.uuid4()),
        candidate_id=candidate.id,
        name=data.name,
        issuer=data.issuer,
        date=data.date,
        award_type=data.award_type,
        prestige_tier=prestige_tier,
        description=data.description,
    )

    db.add(award)
    db.commit()
    db.refresh(award)

    return AwardResponse(
        id=award.id,
        name=award.name,
        issuer=award.issuer,
        date=award.date,
        award_type=award.award_type,
        prestige_tier=award.prestige_tier,
        description=award.description,
    )


@router.delete("/me/awards/{award_id}")
async def delete_award(
    award_id: str,
    candidate: Candidate = Depends(get_current_candidate),
    db: Session = Depends(get_db)
):
    """Delete an award from current candidate's profile."""
    award = db.query(CandidateAward).filter(
        CandidateAward.id == award_id,
        CandidateAward.candidate_id == candidate.id
    ).first()

    if not award:
        raise HTTPException(status_code=404, detail="Award not found")

    db.delete(award)
    db.commit()

    return {"success": True, "deleted_id": award_id}


# ============= Helper Functions =============

def _get_university_id(institution: str) -> Optional[str]:
    """Convert institution name to university ID."""
    inst_lower = institution.lower() if institution else ""
    if "berkeley" in inst_lower or "ucb" in inst_lower or "uc berkeley" in inst_lower:
        return "berkeley"
    if "illinois" in inst_lower or "uiuc" in inst_lower:
        return "uiuc"
    return None


def _get_role_tier(role: Optional[str]) -> int:
    """Determine role tier from role title."""
    if not role:
        return 1

    role_lower = role.lower()

    # Tier 5: President/Founder
    if any(x in role_lower for x in ["president", "founder", "ceo", "director"]):
        return 5

    # Tier 4: VP/Executive
    if any(x in role_lower for x in ["vice president", "vp", "executive", "chair", "head"]):
        return 4

    # Tier 3: Officer/Lead
    if any(x in role_lower for x in ["officer", "lead", "manager", "coordinator", "captain"]):
        return 3

    # Tier 2: Active member with title
    if any(x in role_lower for x in ["mentor", "tutor", "developer", "designer", "analyst"]):
        return 2

    # Tier 1: General member
    return 1


def _get_role_multiplier(role: Optional[str]) -> float:
    """Get score multiplier based on role."""
    tier = _get_role_tier(role)
    multipliers = {
        1: 1.0,   # Member
        2: 1.1,   # Active member
        3: 1.25,  # Officer
        4: 1.4,   # VP/Exec
        5: 1.5,   # President/Founder
    }
    return multipliers.get(tier, 1.0)


def _estimate_award_tier(name: str, award_type: Optional[str], issuer: Optional[str]) -> int:
    """Estimate prestige tier for an award."""
    name_lower = name.lower() if name else ""
    issuer_lower = issuer.lower() if issuer else ""

    # Tier 5: National/International recognition
    if any(x in name_lower for x in ["national", "international", "goldwater", "fulbright", "rhodes"]):
        return 5
    if any(x in name_lower for x in ["first place", "1st place", "grand prize", "winner"]):
        return 4

    # Tier 4: Major scholarships/competitions
    if any(x in name_lower for x in ["scholarship", "fellowship"]):
        if any(x in issuer_lower for x in ["google", "microsoft", "facebook", "meta", "apple"]):
            return 5
        return 4

    # Tier 3: University honors
    if any(x in name_lower for x in ["dean's list", "honors", "cum laude", "phi beta kappa"]):
        return 3

    # Tier 2: Department/local recognition
    if any(x in name_lower for x in ["award", "recognition", "certificate"]):
        return 2

    # Tier 1: Participation
    return 1
