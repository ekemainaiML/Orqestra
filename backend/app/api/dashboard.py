from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.projections import get_dashboard_metrics
from app.services.database import get_session

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
async def dashboard_metrics(session: AsyncSession = Depends(get_session)):
    return await get_dashboard_metrics(session)
