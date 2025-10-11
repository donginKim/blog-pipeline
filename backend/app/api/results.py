# Results API
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from datetime import date

from ..core.database import get_db
from ..schemas import CrawlResult, ResultFilter, CrawlRun
from ..services.result_service import ResultService
from .auth import get_current_user

router = APIRouter()


@router.get("/", response_model=List[CrawlResult])
async def list_results(
    keyword_id: Optional[int] = None,
    blog_id: Optional[int] = None,
    found: Optional[bool] = None,
    run_date_from: Optional[date] = None,
    run_date_to: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List crawl results with filtering"""
    result_service = ResultService(db)
    
    filter_params = ResultFilter(
        keyword_id=keyword_id,
        blog_id=blog_id,
        found=found,
        run_date_from=run_date_from,
        run_date_to=run_date_to,
        limit=limit,
        offset=skip
    )
    
    results = await result_service.list_results(filter_params)
    return results


@router.get("/stats")
async def get_result_stats(
    keyword_id: Optional[int] = None,
    blog_id: Optional[int] = None,
    run_date_from: Optional[date] = None,
    run_date_to: Optional[date] = None,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get statistics for crawl results"""
    result_service = ResultService(db)
    
    filter_params = ResultFilter(
        keyword_id=keyword_id,
        blog_id=blog_id,
        run_date_from=run_date_from,
        run_date_to=run_date_to
    )
    
    stats = await result_service.get_result_stats(filter_params)
    return stats


@router.get("/runs", response_model=List[CrawlRun])
async def list_crawl_runs(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """List crawl runs"""
    result_service = ResultService(db)
    runs = await result_service.list_crawl_runs(skip=skip, limit=limit)
    return runs


@router.get("/runs/{run_id}", response_model=CrawlRun)
async def get_crawl_run(
    run_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get a specific crawl run"""
    result_service = ResultService(db)
    run = await result_service.get_crawl_run(run_id)
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl run not found"
        )
    
    return run


@router.get("/runs/{run_id}/results", response_model=List[CrawlResult])
async def get_run_results(
    run_id: int,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get results for a specific crawl run"""
    result_service = ResultService(db)
    run = await result_service.get_crawl_run(run_id)
    
    if not run:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Crawl run not found"
        )
    
    results = await result_service.get_results_by_run_id(run_id, skip=skip, limit=limit)
    return results


@router.post("/trigger-crawl")
async def trigger_full_crawl(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Trigger a full crawl of all active targets"""
    from ..workers.crawl_worker import crawl_all_keywords_task
    
    task = crawl_all_keywords_task.delay()
    return {"message": "Full crawl task queued", "task_id": task.id}

