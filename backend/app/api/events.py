import asyncio

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse

from app.events.publisher import SSE_CHANNEL, subscribe_events

router = APIRouter(prefix="/events", tags=["events"])


@router.get("/stream")
async def event_stream():
    async def event_generator():
        pubsub = await subscribe_events()
        try:
            while True:
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=30.0)
                if message and message["type"] == "message":
                    data = message.get("data", "{}")
                    if isinstance(data, bytes):
                        data = data.decode()
                    yield {"event": "orqestra_event", "data": data}
                else:
                    yield {"event": "ping", "data": "keepalive"}
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            await pubsub.unsubscribe(SSE_CHANNEL)
            await pubsub.close()

    return EventSourceResponse(event_generator())
