"""
Organization/Team management endpoints for collaborative recruiting.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime, timedelta, timezone
import uuid
import secrets
import re

from ..database import get_db
from ..models.employer import (
    Employer, Organization, OrganizationMember, OrganizationInvite,
    OrganizationRole, InviteStatus, Job
)
from .employers import get_current_employer
from ..services.email import email_service

router = APIRouter(prefix="/api/organizations", tags=["organizations"])


# ==================== SCHEMAS ====================

class OrganizationCreate(BaseModel):
    """Create a new organization."""
    name: str
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None


class OrganizationUpdate(BaseModel):
    """Update organization details."""
    name: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    logo_url: Optional[str] = None


class OrganizationResponse(BaseModel):
    """Organization response."""
    id: str
    name: str
    slug: str
    logo_url: Optional[str] = None
    website: Optional[str] = None
    industry: Optional[str] = None
    company_size: Optional[str] = None
    description: Optional[str] = None
    plan: str
    member_count: int
    created_at: datetime

    class Config:
        from_attributes = True


class MemberResponse(BaseModel):
    """Team member response."""
    id: str
    employer_id: str
    name: str
    email: str
    role: str
    joined_at: datetime
    invited_by: Optional[str] = None

    class Config:
        from_attributes = True


class InviteCreate(BaseModel):
    """Create an invite."""
    email: EmailStr
    role: str = "recruiter"


class InviteResponse(BaseModel):
    """Invite response."""
    id: str
    email: str
    role: str
    status: str
    invite_url: str
    expires_at: datetime
    created_at: datetime
    invited_by: Optional[str] = None

    class Config:
        from_attributes = True


class JoinOrganizationRequest(BaseModel):
    """Request to join via invite token."""
    token: str


# ==================== HELPERS ====================

def generate_slug(name: str) -> str:
    """Generate URL-friendly slug from organization name."""
    slug = re.sub(r'[^a-zA-Z0-9\s-]', '', name.lower())
    slug = re.sub(r'[\s_]+', '-', slug)
    slug = re.sub(r'-+', '-', slug).strip('-')
    return slug


def check_permission(member: OrganizationMember, required_roles: List[OrganizationRole]) -> bool:
    """Check if member has one of the required roles."""
    return member.role in required_roles


# ==================== ENDPOINTS ====================

@router.post("", response_model=OrganizationResponse)
async def create_organization(
    data: OrganizationCreate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Create a new organization and make the current employer the owner.
    """
    # Check if employer already belongs to an organization
    existing_membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already belong to an organization. Leave it first to create a new one."
        )

    # Generate unique slug
    base_slug = generate_slug(data.name)
    slug = base_slug
    counter = 1
    while db.query(Organization).filter(Organization.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    # Create organization
    org = Organization(
        id=str(uuid.uuid4()),
        name=data.name,
        slug=slug,
        website=data.website,
        industry=data.industry,
        company_size=data.company_size,
        description=data.description,
    )
    db.add(org)

    # Add employer as owner
    membership = OrganizationMember(
        id=str(uuid.uuid4()),
        organization_id=org.id,
        employer_id=employer.id,
        role=OrganizationRole.OWNER,
    )
    db.add(membership)

    db.commit()
    db.refresh(org)

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        website=org.website,
        industry=org.industry,
        company_size=org.company_size,
        description=org.description,
        plan=org.plan,
        member_count=1,
        created_at=org.created_at,
    )


@router.get("/me", response_model=OrganizationResponse)
async def get_my_organization(
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Get the current employer's organization.
    """
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    org = membership.organization
    member_count = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org.id
    ).count()

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        website=org.website,
        industry=org.industry,
        company_size=org.company_size,
        description=org.description,
        plan=org.plan,
        member_count=member_count,
        created_at=org.created_at,
    )


@router.patch("/me", response_model=OrganizationResponse)
async def update_organization(
    data: OrganizationUpdate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Update organization details. Requires owner or admin role.
    """
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    if not check_permission(membership, [OrganizationRole.OWNER, OrganizationRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can update organization settings"
        )

    org = membership.organization

    if data.name is not None:
        org.name = data.name
    if data.website is not None:
        org.website = data.website
    if data.industry is not None:
        org.industry = data.industry
    if data.company_size is not None:
        org.company_size = data.company_size
    if data.description is not None:
        org.description = data.description
    if data.logo_url is not None:
        org.logo_url = data.logo_url

    db.commit()
    db.refresh(org)

    member_count = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == org.id
    ).count()

    return OrganizationResponse(
        id=org.id,
        name=org.name,
        slug=org.slug,
        logo_url=org.logo_url,
        website=org.website,
        industry=org.industry,
        company_size=org.company_size,
        description=org.description,
        plan=org.plan,
        member_count=member_count,
        created_at=org.created_at,
    )


# ==================== TEAM MEMBERS ====================

@router.get("/members", response_model=List[MemberResponse])
async def list_members(
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    List all members of the organization.
    """
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    members = db.query(OrganizationMember).filter(
        OrganizationMember.organization_id == membership.organization_id
    ).all()

    result = []
    for m in members:
        emp = m.employer
        invited_by_name = None
        if m.invited_by:
            invited_by_name = m.invited_by.company_name

        result.append(MemberResponse(
            id=m.id,
            employer_id=m.employer_id,
            name=emp.company_name,
            email=emp.email,
            role=m.role.value,
            joined_at=m.joined_at,
            invited_by=invited_by_name,
        ))

    return result


@router.patch("/members/{member_id}/role")
async def update_member_role(
    member_id: str,
    role: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Update a member's role. Requires owner or admin role.
    """
    my_membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not my_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    if not check_permission(my_membership, [OrganizationRole.OWNER, OrganizationRole.ADMIN]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners and admins can change member roles"
        )

    target_membership = db.query(OrganizationMember).filter(
        OrganizationMember.id == member_id,
        OrganizationMember.organization_id == my_membership.organization_id
    ).first()

    if not target_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Can't demote owner unless you're also owner
    if target_membership.role == OrganizationRole.OWNER and my_membership.role != OrganizationRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can change another owner's role"
        )

    # Can't promote to owner unless you're owner
    if role == "owner" and my_membership.role != OrganizationRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can promote someone to owner"
        )

    try:
        target_membership.role = OrganizationRole(role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {role}. Must be one of: owner, admin, recruiter, hiring_manager, interviewer"
        )

    db.commit()

    return {"success": True, "message": f"Role updated to {role}"}


@router.delete("/members/{member_id}")
async def remove_member(
    member_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Remove a member from the organization. Requires owner or admin role.
    """
    my_membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not my_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    target_membership = db.query(OrganizationMember).filter(
        OrganizationMember.id == member_id,
        OrganizationMember.organization_id == my_membership.organization_id
    ).first()

    if not target_membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Member not found"
        )

    # Self-removal is allowed
    if target_membership.employer_id == employer.id:
        # Can't remove yourself if you're the only owner
        if target_membership.role == OrganizationRole.OWNER:
            owner_count = db.query(OrganizationMember).filter(
                OrganizationMember.organization_id == my_membership.organization_id,
                OrganizationMember.role == OrganizationRole.OWNER
            ).count()
            if owner_count <= 1:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You're the only owner. Transfer ownership before leaving."
                )
    else:
        # Removing others requires admin
        if not check_permission(my_membership, [OrganizationRole.OWNER, OrganizationRole.ADMIN]):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners and admins can remove members"
            )

        # Can't remove owner unless you're owner
        if target_membership.role == OrganizationRole.OWNER and my_membership.role != OrganizationRole.OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only owners can remove other owners"
            )

    db.delete(target_membership)
    db.commit()

    return {"success": True, "message": "Member removed"}


# ==================== INVITES ====================

@router.post("/invites", response_model=InviteResponse)
async def create_invite(
    data: InviteCreate,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Create an invite to join the organization. Requires admin role or higher.
    """
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    if not check_permission(membership, [OrganizationRole.OWNER, OrganizationRole.ADMIN, OrganizationRole.RECRUITER]):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You don't have permission to invite members"
        )

    # Check if email is already a member
    existing_employer = db.query(Employer).filter(Employer.email == data.email).first()
    if existing_employer:
        existing_membership = db.query(OrganizationMember).filter(
            OrganizationMember.employer_id == existing_employer.id,
            OrganizationMember.organization_id == membership.organization_id
        ).first()
        if existing_membership:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This person is already a member of your organization"
            )

    # Check for existing pending invite
    existing_invite = db.query(OrganizationInvite).filter(
        OrganizationInvite.organization_id == membership.organization_id,
        OrganizationInvite.email == data.email,
        OrganizationInvite.status == InviteStatus.PENDING
    ).first()

    if existing_invite:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="An invite has already been sent to this email"
        )

    # Validate role
    try:
        role = OrganizationRole(data.role)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid role: {data.role}"
        )

    # Non-owners can't invite owners
    if role == OrganizationRole.OWNER and membership.role != OrganizationRole.OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only owners can invite new owners"
        )

    # Create invite
    token = secrets.token_urlsafe(32)
    invite = OrganizationInvite(
        id=str(uuid.uuid4()),
        organization_id=membership.organization_id,
        email=data.email,
        role=role,
        token=token,
        invited_by_id=employer.id,
        expires_at=datetime.now(timezone.utc) + timedelta(days=7),
    )
    db.add(invite)
    db.commit()
    db.refresh(invite)

    # Generate invite URL
    from ..config import settings
    invite_url = f"{settings.frontend_url}/join?token={token}"

    # Send invite email
    try:
        await email_service.send_organization_invite(
            to_email=data.email,
            organization_name=membership.organization.name,
            inviter_name=employer.company_name,
            role=role.value,
            invite_url=invite_url,
        )
    except Exception as e:
        # Log but don't fail
        print(f"Failed to send invite email: {e}")

    return InviteResponse(
        id=invite.id,
        email=invite.email,
        role=invite.role.value,
        status=invite.status.value,
        invite_url=invite_url,
        expires_at=invite.expires_at,
        created_at=invite.created_at,
        invited_by=employer.company_name,
    )


@router.get("/invites", response_model=List[InviteResponse])
async def list_invites(
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    List all pending invites for the organization.
    """
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    from ..config import settings

    invites = db.query(OrganizationInvite).filter(
        OrganizationInvite.organization_id == membership.organization_id
    ).order_by(OrganizationInvite.created_at.desc()).all()

    result = []
    for inv in invites:
        invited_by_name = None
        if inv.invited_by:
            invited_by_name = inv.invited_by.company_name

        result.append(InviteResponse(
            id=inv.id,
            email=inv.email,
            role=inv.role.value,
            status=inv.status.value,
            invite_url=f"{settings.frontend_url}/join?token={inv.token}",
            expires_at=inv.expires_at,
            created_at=inv.created_at,
            invited_by=invited_by_name,
        ))

    return result


@router.delete("/invites/{invite_id}")
async def cancel_invite(
    invite_id: str,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Cancel a pending invite.
    """
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="You don't belong to any organization"
        )

    invite = db.query(OrganizationInvite).filter(
        OrganizationInvite.id == invite_id,
        OrganizationInvite.organization_id == membership.organization_id
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invite not found"
        )

    if invite.status != InviteStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only cancel pending invites"
        )

    invite.status = InviteStatus.CANCELLED
    db.commit()

    return {"success": True, "message": "Invite cancelled"}


@router.post("/join")
async def join_organization(
    data: JoinOrganizationRequest,
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    Join an organization using an invite token.
    """
    # Check if employer already belongs to an organization
    existing_membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if existing_membership:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already belong to an organization. Leave it first to join another."
        )

    # Find the invite
    invite = db.query(OrganizationInvite).filter(
        OrganizationInvite.token == data.token
    ).first()

    if not invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid invite token"
        )

    if invite.status != InviteStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite is no longer valid"
        )

    if invite.expires_at < datetime.now(timezone.utc):
        invite.status = InviteStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite has expired"
        )

    # Check if the invite email matches (optional - remove for more flexibility)
    if invite.email.lower() != employer.email.lower():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This invite was sent to a different email address"
        )

    # Create membership
    membership = OrganizationMember(
        id=str(uuid.uuid4()),
        organization_id=invite.organization_id,
        employer_id=employer.id,
        role=invite.role,
        invited_by_id=invite.invited_by_id,
    )
    db.add(membership)

    # Update invite status
    invite.status = InviteStatus.ACCEPTED
    invite.accepted_at = datetime.now(timezone.utc)

    db.commit()

    return {
        "success": True,
        "message": f"You've joined {invite.organization.name}!",
        "organization_id": invite.organization_id,
        "role": invite.role.value,
    }


# ==================== TEAM JOBS ====================

@router.get("/jobs")
async def list_team_jobs(
    db: Session = Depends(get_db),
    employer: Employer = Depends(get_current_employer)
):
    """
    List all jobs from team members in the organization.
    """
    membership = db.query(OrganizationMember).filter(
        OrganizationMember.employer_id == employer.id
    ).first()

    if not membership:
        # Return only user's own jobs if not in an org
        jobs = db.query(Job).filter(Job.employer_id == employer.id).all()
    else:
        # Get all employer IDs in the organization
        member_ids = db.query(OrganizationMember.employer_id).filter(
            OrganizationMember.organization_id == membership.organization_id
        ).all()
        member_ids = [m[0] for m in member_ids]

        jobs = db.query(Job).filter(Job.employer_id.in_(member_ids)).all()

    result = []
    for job in jobs:
        result.append({
            "id": job.id,
            "title": job.title,
            "vertical": job.vertical.value if job.vertical else None,
            "role_type": job.role_type.value if job.role_type else None,
            "location": job.location,
            "is_active": job.is_active,
            "created_at": job.created_at,
            "created_by": job.employer.company_name,
            "created_by_id": job.employer_id,
        })

    return {"jobs": result}
