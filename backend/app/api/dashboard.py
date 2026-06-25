from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.projections import get_dashboard_metrics, get_dashboard_trends
from app.services.database import get_session

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
async def dashboard_metrics(session: AsyncSession = Depends(get_session)):
    return await get_dashboard_metrics(session)


@router.get("/trends")
async def dashboard_trends(days: int = Query(30, ge=1, le=90), session: AsyncSession = Depends(get_session)):
    return await get_dashboard_trends(session, days)
