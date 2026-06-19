import asyncio
import json
from typing import Any

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.services.settings import settings


class QwenClient:
    def __init__(self):
        self.client = AsyncOpenAI(
            api_key=settings.dashscope_api_key,
            base_url=settings.qwen_api_base,
        )

    async def assess(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel] | None = None,
        model: str | None = None,
        temperature: float = 0.3,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        model = model or settings.qwen_model_operational
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        for attempt in range(max_retries):
            try:
                if response_model is not None:
                    schema = response_model.model_json_schema()
                    messages[0]["content"] += (
                        f"\n\nYou MUST respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
                    )

                resp = await self.client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                    response_format={"type": "json_object"} if response_model else None,
                )

                content = resp.choices[0].message.content or "{}"
                parsed = json.loads(content)

                if response_model is not None:
                    validated = response_model.model_validate(parsed)
                    return validated.model_dump(mode="json")

                return parsed

            except Exception as e:
                if attempt < max_retries - 1:
                    delays = [0, 10, 30]
                    await asyncio.sleep(delays[attempt])
                    continue
                return {"error": str(e), "model": model, "status": "failed"}

    async def assess_raw(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        model = model or settings.qwen_model_operational
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        resp = await self.client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""


qwen = QwenClient()
