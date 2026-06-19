from fastapi import APIRouter

from app.events.projections import get_dashboard_metrics

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get("/metrics")
async def dashboard_metrics():
    return await get_dashboard_metrics()
