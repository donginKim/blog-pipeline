# Target service (Keyword-Blog mappings)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime

from ..models import KeywordTarget, Keyword, Blog
from ..schemas import KeywordTargetCreate, KeywordTargetUpdate


class TargetService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, target_id: int) -> Optional[KeywordTarget]:
        """Get target by ID"""
        result = await self.db.execute(
            select(KeywordTarget)
            .where(KeywordTarget.id == target_id)
            .options(
                selectinload(KeywordTarget.keyword),
                selectinload(KeywordTarget.blog)
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_keyword_and_blog(self, keyword_id: int, blog_id: int) -> Optional[KeywordTarget]:
        """Get target by keyword and blog IDs"""
        result = await self.db.execute(
            select(KeywordTarget)
            .where(
                KeywordTarget.keyword_id == keyword_id,
                KeywordTarget.blog_id == blog_id
            )
        )
        return result.scalar_one_or_none()
    
    async def list_targets(
        self,
        skip: int = 0,
        limit: int = 100,
        keyword_id: Optional[int] = None,
        blog_id: Optional[int] = None,
        is_active: Optional[bool] = None
    ) -> List[KeywordTarget]:
        """List targets with optional filtering"""
        query = select(KeywordTarget).options(
            selectinload(KeywordTarget.keyword),
            selectinload(KeywordTarget.blog)
        )
        
        if keyword_id is not None:
            query = query.where(KeywordTarget.keyword_id == keyword_id)
        
        if blog_id is not None:
            query = query.where(KeywordTarget.blog_id == blog_id)
        
        if is_active is not None:
            query = query.where(KeywordTarget.is_active == is_active)
        
        query = query.order_by(KeywordTarget.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_target(self, target_data: KeywordTargetCreate) -> KeywordTarget:
        """Create a new target"""
        db_target = KeywordTarget(
            keyword_id=target_data.keyword_id,
            blog_id=target_data.blog_id
        )
        self.db.add(db_target)
        await self.db.commit()
        await self.db.refresh(db_target)
        return db_target
    
    async def update_target(self, target_id: int, target_update: KeywordTargetUpdate) -> Optional[KeywordTarget]:
        """Update target"""
        target = await self.get_by_id(target_id)
        if not target:
            return None
        
        update_data = target_update.model_dump(exclude_unset=True)
        
        for field, value in update_data.items():
            setattr(target, field, value)
        
        await self.db.commit()
        await self.db.refresh(target)
        return target
    
    async def deactivate_target(self, target_id: int) -> bool:
        """Deactivate target (soft delete)"""
        target = await self.get_by_id(target_id)
        if not target:
            return False
        
        target.is_active = False
        
        await self.db.commit()
        return True
    
    async def get_keyword(self, keyword_id: int) -> Optional[Keyword]:
        """Get keyword by ID"""
        result = await self.db.execute(select(Keyword).where(Keyword.id == keyword_id))
        return result.scalar_one_or_none()
    
    async def get_blog(self, blog_id: int) -> Optional[Blog]:
        """Get blog by ID"""
        result = await self.db.execute(select(Blog).where(Blog.id == blog_id))
        return result.scalar_one_or_none()
    
    async def count_targets(self, is_active: Optional[bool] = None) -> int:
        """Count targets"""
        query = select(func.count(KeywordTarget.id))
        
        if is_active is not None:
            query = query.where(KeywordTarget.is_active == is_active)
        
        result = await self.db.execute(query)
        return result.scalar()
