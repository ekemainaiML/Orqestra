import asyncio
import collections.abc
import json
from typing import Any

from openai import AsyncOpenAI
from pydantic import BaseModel

from app.business_tools.definitions import TOOL_EXECUTOR
from app.services.settings import settings


class QwenClient:
    def __init__(self):
        self._client: AsyncOpenAI | None = None
        self._max_tool_rounds = 5

    def _get_client(self) -> AsyncOpenAI:
        if self._client is None:
            from httpx import AsyncClient, Limits, Timeout

            http_client = AsyncClient(
                timeout=Timeout(60.0, connect=10.0),
                limits=Limits(max_keepalive_connections=10, max_connections=20),
            )
            self._client = AsyncOpenAI(
                api_key=settings.dashscope_api_key or "sk-placeholder",
                base_url=settings.qwen_api_base,
                http_client=http_client,
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

                resp = await client.chat.completions.create(
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

    async def assess_with_tools(
        self,
        system_prompt: str,
        user_prompt: str,
        tools: list[dict[str, Any]],
        response_model: type[BaseModel] | None = None,
        model: str | None = None,
        temperature: float = 0.3,
        max_retries: int = 3,
        on_tool_call: collections.abc.Callable[..., collections.abc.Awaitable[None]] | None = None,
    ) -> dict[str, Any]:
        error = self._check_credentials()
        if error:
            return {"error": error, "model": model or settings.qwen_model_operational, "status": "failed"}

        model = model or settings.qwen_model_operational
        messages: list[dict[str, Any]] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        if response_model is not None:
            schema = response_model.model_json_schema()
            messages[0]["content"] += (
                f"\n\nAfter using tools, respond with valid JSON matching this schema:\n{json.dumps(schema, indent=2)}"
            )

        client = self._get_client()
        tool_executor = TOOL_EXECUTOR

        for attempt in range(max_retries):
            try:
                for _ in range(self._max_tool_rounds):
                    resp = await client.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        tools=tools if len(tools) > 0 else None,
                        tool_choice="auto",
                    )

                    msg = resp.choices[0].message

                    if not msg.tool_calls:
                        content = msg.content or "{}"
                        parsed = json.loads(content)
                        if response_model is not None:
                            validated = response_model.model_validate(parsed)
                            return validated.model_dump(mode="json")
                        return parsed

                    messages.append({"role": "assistant", "content": msg.content, "tool_calls": msg.tool_calls})

                    async def run_tool(tc: Any) -> dict[str, Any]:
                        fn_name = tc.function.name
                        fn_args = json.loads(tc.function.arguments)
                        executor = tool_executor.get(fn_name)
                        if executor is not None:
                            result = await executor(**fn_args)
                        else:
                            result = {"error": f"Unknown tool: {fn_name}"}
                        if on_tool_call is not None:
                            await on_tool_call(fn_name, fn_args, result)
                        return {"tool_call_id": tc.id, "content": json.dumps(result)}

                    tool_results = await asyncio.gather(*[run_tool(tc) for tc in msg.tool_calls])
                    for tr in tool_results:
                        messages.append({"role": "tool", **tr})

                return {"error": "max_tool_rounds exceeded", "model": model, "status": "failed"}
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
        max_retries: int = 3,
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
        for attempt in range(max_retries):
            try:
                resp = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=temperature,
                )
                return resp.choices[0].message.content or ""
            except Exception as e:
                if attempt < max_retries - 1:
                    delays = [0, 10, 30]
                    await asyncio.sleep(delays[attempt])
                    continue
                return f"error: {e}"


qwen = QwenClient()
