import asyncio
import json
from typing import Any

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.services.settings import settings


class QwenClient:
    def __init__(self):
        self._client: AsyncOpenAI | None = None

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            self._client = AsyncOpenAI(
                api_key=settings.dashscope_api_key or "sk-placeholder",
                base_url=settings.qwen_api_base,
            )
        return self._client

    def _check_credentials(self) -> str | None:
        if not settings.dashscope_api_key:
            return "DASHSCOPE_API_KEY is not configured"
        return None

    async def assess(
        self,
        system_prompt: str,
        user_prompt: str,
        response_model: type[BaseModel] | None = None,
        model: str | None = None,
        temperature: float = 0.3,
        max_retries: int = 3,
    ) -> dict[str, Any]:
        error = self._check_credentials()
        if error:
            return {"error": error, "model": model or settings.qwen_model_operational, "status": "failed"}

        model = model or settings.qwen_model_operational
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        client = self._get_client()
        for attempt in range(max_retries):
            try:
                if response_model is not None:
                    schema = response_model.model_json_schema()
                    messages[0]["content"] += (
                        f"\n\nYou MUST respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
                    )

                resp = await client.chat.completions.create(  # type: ignore[call-overload, arg-type]
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

        return {"error": "max_retries exhausted", "model": model, "status": "failed"}

    async def assess_raw(
        self,
        system_prompt: str,
        user_prompt: str,
        model: str | None = None,
        temperature: float = 0.3,
    ) -> str:
        error = self._check_credentials()
        if error:
            return error

        model = model or settings.qwen_model_operational
        messages: list[dict[str, str]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        client = self._get_client()
        resp = await client.chat.completions.create(
            model=model,
            messages=messages,  # type: ignore[arg-type]
            temperature=temperature,
        )
        return resp.choices[0].message.content or ""


qwen = QwenClient()
