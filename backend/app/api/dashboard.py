# Dashboard API
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_db
from ..schemas import DashboardStats
from ..services.dashboard_service import DashboardService
from .auth import get_current_user

router = APIRouter()


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats(
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get dashboard statistics and recent data"""
    dashboard_service = DashboardService(db)
    stats = await dashboard_service.get_dashboard_stats()
    return stats


@router.get("/recent-activity")
async def get_recent_activity(
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """Get recent activity summary"""
    dashboard_service = DashboardService(db)
    activity = await dashboard_service.get_recent_activity(limit=limit)
    return activity

