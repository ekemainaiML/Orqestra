import json
import uuid
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.events.publisher import publish_event
from app.models.case import Case
from app.models.customer import Customer
from app.services.database import async_session

router = APIRouter(prefix="/demo", tags=["demo"])


def _load_demo_cases():
    path = Path(__file__).parent.parent.parent / "seed" / "demo_cases.json"
    return json.loads(path.read_text())


@router.get("/cases")
async def list_demo_cases():
    return _load_demo_cases()


@router.post("/launch/{scenario}")
async def launch_demo(scenario: str):
    demo_cases = _load_demo_cases()
    match = next((dc for dc in demo_cases if dc["scenario"] == scenario), None)
    if not match:
        raise HTTPException(status_code=404, detail=f"Unknown scenario: {scenario}")

    async with async_session() as session:
        customer = await session.get(Customer, uuid.UUID(match["customer_id"]))
        if not customer:
            raise HTTPException(status_code=404, detail="Demo customer not found")

        case = Case(
            customer_id=uuid.UUID(match["customer_id"]),
            request_text=match["request_text"],
            workflow_type="order_fulfillment",
        )
        session.add(case)
        await session.commit()
        await session.refresh(case)

    await publish_event(str(case.id), "case_created", "system", {
        "scenario": scenario,
        "description": match["description"],
    })

    return {
        "case_id": str(case.id),
        "scenario": scenario,
        "description": match["description"],
        "message": f"Demo case '{scenario}' launched. Case ID: {case.id}",
    }
