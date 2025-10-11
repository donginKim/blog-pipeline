# Result service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from sqlalchemy.orm import selectinload
from typing import List, Optional, Dict, Any
from datetime import date, datetime

from ..models import CrawlResult, CrawlRun, Keyword, Blog
from ..schemas import ResultFilter


class ResultService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def list_results(self, filter_params: ResultFilter) -> List[CrawlResult]:
        """List crawl results with filtering"""
        query = select(CrawlResult).options(
            selectinload(CrawlResult.keyword),
            selectinload(CrawlResult.blog)
        )
        
        conditions = []
        
        if filter_params.keyword_id is not None:
            conditions.append(CrawlResult.keyword_id == filter_params.keyword_id)
        
        if filter_params.blog_id is not None:
            conditions.append(CrawlResult.blog_id == filter_params.blog_id)
        
        if filter_params.found is not None:
            conditions.append(CrawlResult.found == filter_params.found)
        
        if filter_params.run_date_from is not None:
            conditions.append(CrawlResult.run_date >= filter_params.run_date_from)
        
        if filter_params.run_date_to is not None:
            conditions.append(CrawlResult.run_date <= filter_params.run_date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(CrawlResult.created_at.desc())
        query = query.offset(filter_params.offset).limit(filter_params.limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_result_stats(self, filter_params: ResultFilter) -> Dict[str, Any]:
        """Get statistics for crawl results"""
        query = select(CrawlResult)
        
        conditions = []
        
        if filter_params.keyword_id is not None:
            conditions.append(CrawlResult.keyword_id == filter_params.keyword_id)
        
        if filter_params.blog_id is not None:
            conditions.append(CrawlResult.blog_id == filter_params.blog_id)
        
        if filter_params.run_date_from is not None:
            conditions.append(CrawlResult.run_date >= filter_params.run_date_from)
        
        if filter_params.run_date_to is not None:
            conditions.append(CrawlResult.run_date <= filter_params.run_date_to)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # Total results
        total_result = await self.db.execute(select(func.count(CrawlResult.id)).select_from(query.subquery()))
        total_count = total_result.scalar()
        
        # Found results
        found_result = await self.db.execute(
            select(func.count(CrawlResult.id))
            .select_from(query.where(CrawlResult.found == True).subquery())
        )
        found_count = found_result.scalar()
        
        # Not found results
        not_found_count = total_count - found_count
        
        # Average occurrences
        avg_result = await self.db.execute(
            select(func.avg(CrawlResult.occurrences))
            .select_from(query.subquery())
        )
        avg_occurrences = avg_result.scalar() or 0
        
        return {
            "total_count": total_count,
            "found_count": found_count,
            "not_found_count": not_found_count,
            "found_percentage": (found_count / total_count * 100) if total_count > 0 else 0,
            "average_occurrences": round(float(avg_occurrences), 2)
        }
    
    async def list_crawl_runs(self, skip: int = 0, limit: int = 50) -> List[CrawlRun]:
        """List crawl runs"""
        query = select(CrawlRun).order_by(CrawlRun.started_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def get_crawl_run(self, run_id: int) -> Optional[CrawlRun]:
        """Get a specific crawl run"""
        result = await self.db.execute(select(CrawlRun).where(CrawlRun.id == run_id))
        return result.scalar_one_or_none()
    
    async def get_results_by_run_id(self, run_id: int, skip: int = 0, limit: int = 100) -> List[CrawlResult]:
        """Get results for a specific crawl run"""
        query = select(CrawlResult).where(CrawlResult.crawl_run_id == run_id)
        query = query.options(
            selectinload(CrawlResult.keyword),
            selectinload(CrawlResult.blog)
        )
        query = query.order_by(CrawlResult.created_at.desc())
        query = query.offset(skip).limit(limit)
        
        result = await self.db.execute(query)
        return result.scalars().all()
    
    async def create_crawl_run(self) -> CrawlRun:
        """Create a new crawl run"""
        db_run = CrawlRun()
        self.db.add(db_run)
        await self.db.commit()
        await self.db.refresh(db_run)
        return db_run
    
    async def update_crawl_run(
        self, 
        run_id: int, 
        status: Optional[str] = None,
        finished_at: Optional[datetime] = None,
        total_keywords: Optional[int] = None,
        success_count: Optional[int] = None,
        fail_count: Optional[int] = None,
        error_message: Optional[str] = None
    ) -> Optional[CrawlRun]:
        """Update crawl run"""
        run = await self.get_crawl_run(run_id)
        if not run:
            return None
        
        if status is not None:
            run.status = status
        if finished_at is not None:
            run.finished_at = finished_at
        if total_keywords is not None:
            run.total_keywords = total_keywords
        if success_count is not None:
            run.success_count = success_count
        if fail_count is not None:
            run.fail_count = fail_count
        if error_message is not None:
            run.error_message = error_message
        
        await self.db.commit()
        await self.db.refresh(run)
        return run
    
    async def create_crawl_result(
        self,
        keyword_id: int,
        blog_id: int,
        keyword_target_id: int,
        found: bool,
        occurrences: int,
        run_date: date,
        crawl_run_id: Optional[int] = None,
        section: Optional[str] = None,
        matched_url: Optional[str] = None,
        matched_title: Optional[str] = None,
        snapshot_json: Optional[str] = None
    ) -> CrawlResult:
        """Create a new crawl result"""
        db_result = CrawlResult(
            crawl_run_id=crawl_run_id,
            keyword_id=keyword_id,
            blog_id=blog_id,
            keyword_target_id=keyword_target_id,
            found=found,
            occurrences=occurrences,
            section=section,
            matched_url=matched_url,
            matched_title=matched_title,
            snapshot_json=snapshot_json,
            run_date=run_date
        )
        self.db.add(db_result)
        await self.db.commit()
        await self.db.refresh(db_result)
        return db_result

