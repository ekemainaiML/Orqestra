import time
from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class MetricsCollector:
    request_count: int = 0
    error_count: int = 0
    status_counts: dict[int, int] = field(default_factory=lambda: defaultdict(int))
    error_types: dict[str, int] = field(default_factory=lambda: defaultdict(int))
    total_duration_ms: float = 0.0
    _start_time: float = field(default_factory=time.time)

    def record_request(self, status_code: int, duration_ms: float, error_type: str | None = None):
        self.request_count += 1
        self.status_counts[status_code] += 1
        self.total_duration_ms += duration_ms
        if error_type:
            self.error_count += 1
            self.error_types[error_type] += 1

    def snapshot(self) -> dict:
        uptime_s = time.time() - self._start_time
        return {
            "uptime_seconds": round(uptime_s, 1),
            "total_requests": self.request_count,
            "total_errors": self.error_count,
            "requests_per_second": round(self.request_count / uptime_s, 2) if uptime_s > 0 else 0.0,
            "average_duration_ms": (
                round(self.total_duration_ms / self.request_count, 1)
                if self.request_count > 0 else 0.0
            ),
            "status_counts": dict(self.status_counts),
            "error_types": dict(self.error_types),
        }


metrics = MetricsCollector()
