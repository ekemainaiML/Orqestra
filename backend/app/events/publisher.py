import json
import logging
from typing import Any

import redis.asyncio as redis
from sqlalchemy.ext.asyncio import AsyncSession

from app.events.event_store import append_event
from app.services.settings import settings

logger = logging.getLogger(__name__)

redis_client: redis.Redis | None = None
SSE_CHANNEL = "orqestra:events"


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


async def _try_notify(event_type: str, event: dict[str, Any]) -> None:
    from app.services.notifications import get_notifier, should_notify
    if not should_notify(event_type):
        return
    summary = ""
    payload = event.get("payload") or {}
    if payload.get("summary"):
        summary = payload["summary"]
    elif payload.get("reason"):
        summary = payload["reason"]
    else:
        summary = payload.get("message", str(payload)[:200])
    notifier = get_notifier()
    await notifier.notify(
        event_type=event_type,
        case_id=event.get("case_id", ""),
        actor=event.get("actor", "system"),
        summary=summary[:300],
    )


async def publish_event(
    case_id: str,
    event_type: str,
    actor: str,
    payload: dict[str, Any] | None = None,
    iteration: int = 0,
    session: AsyncSession | None = None,
) -> dict[str, Any]:
    event = await append_event(case_id, event_type, actor, payload, iteration, session=session)
    try:
        r = await get_redis()
        await r.publish(SSE_CHANNEL, json.dumps(event))
    except Exception:
        pass
    try:
        await _try_notify(event_type, event)
    except Exception as e:
        logger.warning("Notification failed for %s: %s", event_type, e)
    return event


async def subscribe_events():
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(SSE_CHANNEL)
    return pubsub
