# Blogs API
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from ..core.database import get_db
from ..schemas import Blog, BlogCreate, BlogUpdate
from ..services.blog_service import BlogService
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[Blog])
async def list_blogs(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    is_active: Optional[bool] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List all blogs with optional filtering"""
    blog_service = BlogService(db)
    blogs = await blog_service.list_blogs(
        skip=skip, limit=limit, is_active=is_active
    )
    return blogs


@router.post("/", response_model=Blog)
async def create_blog(
    blog_data: BlogCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Create a new blog"""
    blog_service = BlogService(db)
    blog = await blog_service.create_blog(blog_data)
    return blog


@router.get("/{blog_id}", response_model=Blog)
async def get_blog(
    blog_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific blog by ID"""
    blog_service = BlogService(db)
    blog = await blog_service.get_by_id(blog_id)
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    return blog


@router.put("/{blog_id}", response_model=Blog)
async def update_blog(
    blog_id: int,
    blog_update: BlogUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Update a blog"""
    blog_service = BlogService(db)
    blog = await blog_service.get_by_id(blog_id)
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    updated_blog = await blog_service.update_blog(blog_id, blog_update)
    return updated_blog


@router.delete("/{blog_id}")
async def delete_blog(
    blog_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Delete a blog (soft delete by setting is_active=False)"""
    blog_service = BlogService(db)
    blog = await blog_service.get_by_id(blog_id)
    
    if not blog:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Blog not found"
        )
    
    await blog_service.deactivate_blog(blog_id)
    return {"message": "Blog deactivated successfully"}

