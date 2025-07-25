"""
User profiles API routes.
Single responsibility: Handle all profile-related HTTP endpoints.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, validator

from ..core.database import get_db
from ..models.database import UserProfile, create_profile_hash
from ..core.config import get_settings

logger = logging.getLogger(__name__)
router = APIRouter()
settings = get_settings()

# Pydantic models for request/response
class ProfileCreate(BaseModel):
    """Profile creation request model"""
    profile_name: str
    industry: str
    department: str
    role_level: str
    
    @validator('profile_name')
    def validate_profile_name(cls, v):
        if len(v.strip()) < 2:
            raise ValueError('Profile name must be at least 2 characters')
        if len(v.strip()) > 100:
            raise ValueError('Profile name must be less than 100 characters')
        return v.strip()
    
    @validator('industry')
    def validate_industry(cls, v):
        valid_industries = ['electric', 'broadband', 'municipal', 'technology', 'financial', 'healthcare']
        if v not in valid_industries:
            raise ValueError(f'Industry must be one of: {valid_industries}')
        return v
    
    @validator('department')
    def validate_department(cls, v):
        valid_departments = ['engineering', 'marketing', 'sales', 'executive', 'operations', 'it', 'customer_service']
        if v not in valid_departments:
            raise ValueError(f'Department must be one of: {valid_departments}')
        return v
    
    @validator('role_level')
    def validate_role_level(cls, v):
        valid_roles = ['individual', 'manager', 'director', 'executive', 'c_level']
        if v not in valid_roles:
            raise ValueError(f'Role level must be one of: {valid_roles}')
        return v


class ProfileUpdate(BaseModel):
    """Profile update request model"""
    profile_name: Optional[str] = None
    is_active: Optional[bool] = None
    
    @validator('profile_name')
    def validate_profile_name(cls, v):
        if v is not None:
            if len(v.strip()) < 2:
                raise ValueError('Profile name must be at least 2 characters')
            if len(v.strip()) > 100:
                raise ValueError('Profile name must be less than 100 characters')
            return v.strip()
        return v


class ProfileResponse(BaseModel):
    """Profile response model"""
    id: int
    profile_name: str
    industry: str
    department: str
    role_level: str
    user_session_id: Optional[str]
    is_active: bool
    created_at: str
    updated_at: str
    
    class Config:
        from_attributes = True


# API Routes
@router.get("/profiles", response_model=List[ProfileResponse])
async def get_profiles(
    session_id: Optional[str] = None,
    active_only: bool = True,
    db: Session = Depends(get_db)
):
    """Get all profiles, optionally filtered by session ID"""
    try:
        query = db.query(UserProfile)
        
        if session_id:
            query = query.filter(UserProfile.user_session_id == session_id)
        
        if active_only:
            query = query.filter(UserProfile.is_active == True)
        
        profiles = query.order_by(UserProfile.created_at.desc()).all()
        
        logger.info(f"Retrieved {len(profiles)} profiles (session_id={session_id})")
        return profiles
        
    except Exception as e:
        logger.error(f"Error retrieving profiles: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profiles"
        )


@router.get("/profiles/{profile_id}", response_model=ProfileResponse)
async def get_profile(profile_id: int, db: Session = Depends(get_db)):
    """Get a specific profile by ID"""
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with ID {profile_id} not found"
            )
        
        logger.info(f"Retrieved profile {profile_id}: {profile.profile_name}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving profile {profile_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve profile"
        )


@router.post("/profiles", response_model=ProfileResponse, status_code=status.HTTP_201_CREATED)
async def create_profile(
    profile_data: ProfileCreate,
    session_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Create a new user profile"""
    try:
        # Check if profile with same name exists for this session
        existing_profile = db.query(UserProfile).filter(
            UserProfile.profile_name == profile_data.profile_name,
            UserProfile.user_session_id == session_id
        ).first()
        
        if existing_profile:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Profile with name '{profile_data.profile_name}' already exists"
            )
        
        # Create new profile
        profile = UserProfile(
            profile_name=profile_data.profile_name,
            industry=profile_data.industry,
            department=profile_data.department,
            role_level=profile_data.role_level,
            user_session_id=session_id
        )
        
        db.add(profile)
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Created profile {profile.id}: {profile.profile_name}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating profile: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create profile"
        )


@router.put("/profiles/{profile_id}", response_model=ProfileResponse)
async def update_profile(
    profile_id: int,
    profile_data: ProfileUpdate,
    db: Session = Depends(get_db)
):
    """Update an existing profile"""
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with ID {profile_id} not found"
            )
        
        # Update fields if provided
        if profile_data.profile_name is not None:
            profile.profile_name = profile_data.profile_name
        
        if profile_data.is_active is not None:
            profile.is_active = profile_data.is_active
        
        db.commit()
        db.refresh(profile)
        
        logger.info(f"Updated profile {profile_id}: {profile.profile_name}")
        return profile
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile {profile_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.delete("/profiles/{profile_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_profile(profile_id: int, db: Session = Depends(get_db)):
    """Delete a profile (soft delete by setting is_active=False)"""
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with ID {profile_id} not found"
            )
        
        # Soft delete by setting is_active=False
        profile.is_active = False
        db.commit()
        
        logger.info(f"Deleted profile {profile_id}: {profile.profile_name}")
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting profile {profile_id}: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete profile"
        )


@router.get("/profiles/{profile_id}/hash")
async def get_profile_hash(profile_id: int, db: Session = Depends(get_db)):
    """Get the profile hash for AI analysis caching"""
    try:
        profile = db.query(UserProfile).filter(UserProfile.id == profile_id).first()
        
        if not profile:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Profile with ID {profile_id} not found"
            )
        
        profile_hash = create_profile_hash(
            profile.industry,
            profile.department,
            profile.role_level
        )
        
        return {
            "profile_id": profile_id,
            "profile_hash": profile_hash,
            "industry": profile.industry,
            "department": profile.department,
            "role_level": profile.role_level
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting profile hash for {profile_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get profile hash"
        )