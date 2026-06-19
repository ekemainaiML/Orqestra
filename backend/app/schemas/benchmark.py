from typing import Any

from pydantic import BaseModel


class BenchmarkResponse(BaseModel):
    single_agent: dict[str, Any]
    organization: dict[str, Any]
    comparison: dict[str, Any]
