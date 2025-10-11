# Blog service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from ..models import Blog
from ..schemas import BlogCreate, BlogUpdate


class BlogService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, blog_id: int) -> Optional[Blog]:
        """Get blog by ID"""
        result = await self.db.execute(select(Blog).where(Blog.id == blog_id))
        return result.scalar_one_or_none()
    
    async def get_by_url_pattern(self, url_pattern: str) -> Optional[Blog]:
        """Get blog by URL pattern"""
        result = await self.db.execute(select(Blog).where(Blog.url_pattern == url_pattern))
        return result.scalar_one_or_none()
    
    async def list_blogs(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> List[Blog]:
        """List blogs with optional filtering"""
        query = select(Blog)
        
        if is_active is not None:
            query = query.where(Blog.is_active == is_active)
        
        query = query.order_by(Blog.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_blog(self, blog_data: BlogCreate) -> Blog:
        """Create a new blog"""
        db_blog = Blog(
            name=blog_data.name,
            url_pattern=blog_data.url_pattern,
            description=blog_data.description
        )
        self.db.add(db_blog)
        await self.db.commit()
        await self.db.refresh(db_blog)
        return db_blog
    
    async def update_blog(self, blog_id: int, blog_update: BlogUpdate) -> Optional[Blog]:
        """Update blog"""
        blog = await self.get_by_id(blog_id)
        if not blog:
            return None
        
        update_data = blog_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(blog, field, value)
        
        await self.db.commit()
        await self.db.refresh(blog)
        return blog
    
    async def deactivate_blog(self, blog_id: int) -> bool:
        """Deactivate blog (soft delete)"""
        blog = await self.get_by_id(blog_id)
        if not blog:
            return False
        
        blog.is_active = False
        blog.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def count_blogs(self, is_active: Optional[bool] = None) -> int:
        """Count blogs"""
        query = select(func.count(Blog.id))
        
        if is_active is not None:
            query = query.where(Blog.is_active == is_active)
        
        result = await self.db.execute(query)
        return result.scalar()

