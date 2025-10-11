# Keyword service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List, Optional
from datetime import datetime

from ..models import Keyword
from ..schemas import KeywordCreate, KeywordUpdate


class KeywordService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_by_id(self, keyword_id: int) -> Optional[Keyword]:
        """Get keyword by ID"""
        result = await self.db.execute(select(Keyword).where(Keyword.id == keyword_id))
        return result.scalar_one_or_none()
    
    async def get_by_keyword(self, keyword: str) -> Optional[Keyword]:
        """Get keyword by keyword text"""
        result = await self.db.execute(select(Keyword).where(Keyword.keyword == keyword))
        return result.scalar_one_or_none()
    
    async def list_keywords(
        self, 
        skip: int = 0, 
        limit: int = 100, 
        is_active: Optional[bool] = None
    ) -> List[Keyword]:
        """List keywords with optional filtering"""
        query = select(Keyword)
        
        if is_active is not None:
            query = query.where(Keyword.is_active == is_active)
        
        query = query.order_by(Keyword.created_at.desc()).offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_keyword(self, keyword_data: KeywordCreate) -> Keyword:
        """Create a new keyword"""
        db_keyword = Keyword(
            keyword=keyword_data.keyword,
            description=keyword_data.description
        )
        self.db.add(db_keyword)
        await self.db.commit()
        await self.db.refresh(db_keyword)
        return db_keyword
    
    async def update_keyword(self, keyword_id: int, keyword_update: KeywordUpdate) -> Optional[Keyword]:
        """Update keyword"""
        keyword = await self.get_by_id(keyword_id)
        if not keyword:
            return None
        
        update_data = keyword_update.model_dump(exclude_unset=True)
        update_data["updated_at"] = datetime.utcnow()
        
        for field, value in update_data.items():
            setattr(keyword, field, value)
        
        await self.db.commit()
        await self.db.refresh(keyword)
        return keyword
    
    async def deactivate_keyword(self, keyword_id: int) -> bool:
        """Deactivate keyword (soft delete)"""
        keyword = await self.get_by_id(keyword_id)
        if not keyword:
            return False
        
        keyword.is_active = False
        keyword.updated_at = datetime.utcnow()
        
        await self.db.commit()
        return True
    
    async def count_keywords(self, is_active: Optional[bool] = None) -> int:
        """Count keywords"""
        query = select(func.count(Keyword.id))
        
        if is_active is not None:
            query = query.where(Keyword.is_active == is_active)
        
        result = await self.db.execute(query)
        return result.scalar()

