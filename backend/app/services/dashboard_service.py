# Dashboard service
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from typing import List, Dict, Any
from datetime import datetime, timedelta

from ..models import Keyword, Blog, KeywordTarget, CrawlResult, CrawlRun
from ..schemas import DashboardStats


class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_dashboard_stats(self) -> DashboardStats:
        """Get dashboard statistics"""
        # Count active keywords
        keyword_count_result = await self.db.execute(
            select(func.count(Keyword.id)).where(Keyword.is_active == True)
        )
        total_keywords = keyword_count_result.scalar()
        
        # Count active blogs
        blog_count_result = await self.db.execute(
            select(func.count(Blog.id)).where(Blog.is_active == True)
        )
        total_blogs = blog_count_result.scalar()
        
        # Count active targets
        target_count_result = await self.db.execute(
            select(func.count(KeywordTarget.id)).where(KeywordTarget.is_active == True)
        )
        total_targets = target_count_result.scalar()
        
        # Count total results
        result_count_result = await self.db.execute(select(func.count(CrawlResult.id)))
        total_results = result_count_result.scalar()
        
        # Get recent runs
        recent_runs_result = await self.db.execute(
            select(CrawlRun)
            .order_by(desc(CrawlRun.started_at))
            .limit(5)
        )
        recent_runs = recent_runs_result.scalars().all()
        
        # Get recent results
        recent_results_result = await self.db.execute(
            select(CrawlResult)
            .order_by(desc(CrawlResult.created_at))
            .limit(10)
        )
        recent_results = recent_results_result.scalars().all()
        
        return DashboardStats(
            total_keywords=total_keywords,
            total_blogs=total_blogs,
            total_targets=total_targets,
            total_results=total_results,
            recent_runs=list(recent_runs),
            recent_results=list(recent_results)
        )
    
    async def get_recent_activity(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent activity summary"""
        # Get recent crawl runs
        runs_result = await self.db.execute(
            select(CrawlRun)
            .order_by(desc(CrawlRun.started_at))
            .limit(limit)
        )
        runs = runs_result.scalars().all()
        
        activities = []
        for run in runs:
            activities.append({
                "type": "crawl_run",
                "id": run.id,
                "timestamp": run.started_at,
                "status": run.status,
                "total_keywords": run.total_keywords,
                "success_count": run.success_count,
                "fail_count": run.fail_count
            })
        
        return activities
    
    async def get_keyword_performance(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get keyword performance over time"""
        from_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily results for each keyword
        query = select(
            CrawlResult.keyword_id,
            CrawlResult.run_date,
            func.count(CrawlResult.id).label('total_results'),
            func.sum(func.case([(CrawlResult.found == True, 1)], else_=0)).label('found_count'),
            func.avg(CrawlResult.occurrences).label('avg_occurrences')
        ).where(
            CrawlResult.run_date >= from_date.date()
        ).group_by(
            CrawlResult.keyword_id,
            CrawlResult.run_date
        ).order_by(
            CrawlResult.run_date.desc()
        )
        
        result = await self.db.execute(query)
        performance_data = result.all()
        
        # Group by keyword
        keyword_performance = {}
        for row in performance_data:
            keyword_id = row.keyword_id
            if keyword_id not in keyword_performance:
                keyword_performance[keyword_id] = []
            
            keyword_performance[keyword_id].append({
                "date": row.run_date,
                "total_results": row.total_results,
                "found_count": row.found_count,
                "found_percentage": (row.found_count / row.total_results * 100) if row.total_results > 0 else 0,
                "avg_occurrences": float(row.avg_occurrences) if row.avg_occurrences else 0
            })
        
        return keyword_performance
    
    async def get_blog_performance(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get blog performance over time"""
        from_date = datetime.utcnow() - timedelta(days=days)
        
        # Get daily results for each blog
        query = select(
            CrawlResult.blog_id,
            CrawlResult.run_date,
            func.count(CrawlResult.id).label('total_results'),
            func.sum(func.case([(CrawlResult.found == True, 1)], else_=0)).label('found_count'),
            func.avg(CrawlResult.occurrences).label('avg_occurrences')
        ).where(
            CrawlResult.run_date >= from_date.date()
        ).group_by(
            CrawlResult.blog_id,
            CrawlResult.run_date
        ).order_by(
            CrawlResult.run_date.desc()
        )
        
        result = await self.db.execute(query)
        performance_data = result.all()
        
        # Group by blog
        blog_performance = {}
        for row in performance_data:
            blog_id = row.blog_id
            if blog_id not in blog_performance:
                blog_performance[blog_id] = []
            
            blog_performance[blog_id].append({
                "date": row.run_date,
                "total_results": row.total_results,
                "found_count": row.found_count,
                "found_percentage": (row.found_count / row.total_results * 100) if row.total_results > 0 else 0,
                "avg_occurrences": float(row.avg_occurrences) if row.avg_occurrences else 0
            })
        
        return blog_performance

