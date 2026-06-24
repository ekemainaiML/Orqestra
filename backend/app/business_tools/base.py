import asyncio
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    pass


@dataclass
class CircuitBreaker:
    failure_threshold: int = 5
    recovery_timeout: float = 30.0
    _failures: int = 0
    _state: CircuitState = CircuitState.CLOSED
    _last_failure_time: float = 0.0

    async def call(self, fn: Any, *args: Any, **kwargs: Any) -> Any:
        if self._state == CircuitState.OPEN:
            if time.monotonic() - self._last_failure_time >= self.recovery_timeout:
                self._state = CircuitState.HALF_OPEN
            else:
                raise CircuitBreakerOpenError(f"Circuit open for {self.recovery_timeout}s")

        try:
            result = await fn(*args, **kwargs)
            if self._state == CircuitState.HALF_OPEN:
                self._state = CircuitState.CLOSED
                self._failures = 0
            return result
        except Exception:
            self._failures += 1
            self._last_failure_time = time.monotonic()
            if self._failures >= self.failure_threshold:
                self._state = CircuitState.OPEN
            raise


@dataclass
class RateLimiter:
    max_calls: int
    window_seconds: float = 60.0
    _calls: list[float] = field(default_factory=list)

    async def acquire(self) -> None:
        now = time.monotonic()
        self._calls = [t for t in self._calls if now - t < self.window_seconds]
        if len(self._calls) >= self.max_calls:
            sleep = self._calls[0] + self.window_seconds - now
            if sleep > 0:
                await asyncio.sleep(sleep)
        self._calls.append(time.monotonic())


class BaseTool(ABC):
    name: str = ""
    description: str = ""

    def __init__(self) -> None:
        self._circuit_breaker: CircuitBreaker | None = None
        self._rate_limiter: RateLimiter | None = None

    def with_circuit_breaker(self, cb: CircuitBreaker) -> "BaseTool":
        self._circuit_breaker = cb
        return self

    def with_rate_limiter(self, rl: RateLimiter) -> "BaseTool":
        self._rate_limiter = rl
        return self

    @abstractmethod
    async def execute(self, **kwargs: Any) -> Any:
        ...

    async def __call__(self, **kwargs: Any) -> Any:
        if self._rate_limiter:
            await self._rate_limiter.acquire()
        if self._circuit_breaker:
            return await self._circuit_breaker.call(self.execute, **kwargs)
        return await self.execute(**kwargs)


class APITool(BaseTool):
    base_url: str = ""
    timeout: int = 30
    max_retries: int = 3
