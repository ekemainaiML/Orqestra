import json
from typing import Any

import redis.asyncio as redis

from app.events.event_store import append_event
from app.services.settings import settings

redis_client: redis.Redis | None = None
SSE_CHANNEL = "orqestra:events"


async def get_redis() -> redis.Redis:
    global redis_client
    if redis_client is None:
        redis_client = redis.from_url(settings.redis_url, decode_responses=True)
    return redis_client


async def publish_event(
    case_id: str,
    event_type: str,
    actor: str,
    payload: dict[str, Any] | None = None,
    iteration: int = 0,
) -> dict[str, Any]:
    event = await append_event(case_id, event_type, actor, payload, iteration)
    try:
        r = await get_redis()
        await r.publish(SSE_CHANNEL, json.dumps(event))
    except Exception:
        pass
    return event


async def subscribe_events():
    r = await get_redis()
    pubsub = r.pubsub()
    await pubsub.subscribe(SSE_CHANNEL)
    return pubsub
