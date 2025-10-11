# Keywords API
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..schemas import Keyword, KeywordCreate, KeywordUpdate
from ..services.keyword_service import KeywordService
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[Keyword])
async def list_keywords(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all keywords with optional filtering"""
    keyword_service = KeywordService(db)
    keywords = await keyword_service.list_keywords(
        skip=skip, limit=limit, is_active=is_active
    )
    return keywords


@router.post("/", response_model=Keyword)
async def create_keyword(
    keyword_data: KeywordCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new keyword"""
    keyword_service = KeywordService(db)
    
    # Check if keyword already exists
    existing_keyword = await keyword_service.get_by_keyword(keyword_data.keyword)
    if existing_keyword:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Keyword already exists"
        )
    
    keyword = await keyword_service.create_keyword(keyword_data)
    return keyword


@router.get("/{keyword_id}", response_model=Keyword)
async def get_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific keyword by ID"""
    keyword_service = KeywordService(db)
    keyword = await keyword_service.get_by_id(keyword_id)
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    return keyword


@router.put("/{keyword_id}", response_model=Keyword)
async def update_keyword(
    keyword_id: int,
    keyword_update: KeywordUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a keyword"""
    keyword_service = KeywordService(db)
    keyword = await keyword_service.get_by_id(keyword_id)
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    # Check if new keyword name conflicts
    if keyword_update.keyword and keyword_update.keyword != keyword.keyword:
        existing_keyword = await keyword_service.get_by_keyword(keyword_update.keyword)
        if existing_keyword:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Keyword already exists"
            )
    
    updated_keyword = await keyword_service.update_keyword(keyword_id, keyword_update)
    return updated_keyword


@router.delete("/{keyword_id}")
async def delete_keyword(
    keyword_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a keyword (soft delete by setting is_active=False)"""
    keyword_service = KeywordService(db)
    keyword = await keyword_service.get_by_id(keyword_id)
    
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    await keyword_service.deactivate_keyword(keyword_id)
    return {"message": "Keyword deactivated successfully"}

