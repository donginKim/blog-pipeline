# Targets API (Keyword-Blog mappings)
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..schemas import KeywordTarget, KeywordTargetCreate, KeywordTargetUpdate
from ..services.target_service import TargetService
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[KeywordTarget])
async def list_targets(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    keyword_id: Optional[int] = None,
    blog_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all keyword-blog targets with optional filtering"""
    target_service = TargetService(db)
    targets = await target_service.list_targets(
        skip=skip, 
        limit=limit, 
        keyword_id=keyword_id,
        blog_id=blog_id,
        is_active=is_active
    )
    return targets


@router.post("/", response_model=KeywordTarget)
async def create_target(
    target_data: KeywordTargetCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new keyword-blog target mapping"""
    target_service = TargetService(db)
    
    # Check if target already exists
    existing_target = await target_service.get_by_keyword_and_blog(
        target_data.keyword_id, target_data.blog_id
    )
    if existing_target:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Target mapping already exists"
        )
    
    # Verify keyword and blog exist
    keyword = await target_service.get_keyword(target_data.keyword_id)
    if not keyword:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Keyword not found"
        )
    
    blog = await target_service.get_blog(target_data.blog_id)
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    target = await target_service.create_target(target_data)
    return target


@router.get("/{target_id}", response_model=KeywordTarget)
async def get_target(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific target by ID"""
    target_service = TargetService(db)
    target = await target_service.get_by_id(target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )
    
    return target


@router.put("/{target_id}", response_model=KeywordTarget)
async def update_target(
    target_id: int,
    target_update: KeywordTargetUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a target"""
    target_service = TargetService(db)
    target = await target_service.get_by_id(target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )
    
    updated_target = await target_service.update_target(target_id, target_update)
    return updated_target


@router.delete("/{target_id}")
async def delete_target(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a target (soft delete by setting is_active=False)"""
    target_service = TargetService(db)
    target = await target_service.get_by_id(target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )
    
    await target_service.deactivate_target(target_id)
    return {"message": "Target deactivated successfully"}


@router.post("/{target_id}/crawl")
async def trigger_crawl_for_target(
    target_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Trigger a crawl for a specific target"""
    target_service = TargetService(db)
    target = await target_service.get_by_id(target_id)
    
    if not target:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Target not found"
        )
    
    # Queue crawl task
    from ..workers.crawl_worker import crawl_keyword_task
    task = crawl_keyword_task.delay(target.keyword_id, target.blog_id)
    
    return {"message": "Crawl task queued", "task_id": task.id}

