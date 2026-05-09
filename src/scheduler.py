"""Task scheduler implementation.

Generated from technical specification:
# Technical Specification: Lightweight Task Scheduling Service

## 1. Architecture Overview

**Pattern:** Event-Driven Microservice with Priority Queue Scheduler

```
REST API Layer (FastAPI)
        ...
"""
from __future__ import annotations

import heapq
import threading
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Callable, Dict, List, Optional


@dataclass(order=True)
class ScheduledJob:
    next_run: float
    job_id: str = field(compare=False)
    name: str = field(compare=False)
    cron: str = field(compare=False)
    handler: Callable = field(compare=False, repr=False)
    enabled: bool = field(default=True, compare=False)


class TaskScheduler:
    """In-memory task scheduler with cron-style triggers."""

    def __init__(self) -> None:
        self._jobs: Dict[str, ScheduledJob] = {}
        self._queue: List[ScheduledJob] = []
        self._lock = threading.Lock()

    def register(self, name: str, cron: str, handler: Callable) -> str:
        job_id = str(uuid.uuid4())
        job = ScheduledJob(
            next_run=datetime.now(timezone.utc).timestamp(),
            job_id=job_id,
            name=name,
            cron=cron,
            handler=handler,
        )
        with self._lock:
            self._jobs[job_id] = job
            heapq.heappush(self._queue, job)
        return job_id

    def list_jobs(self) -> List[Dict]:
        with self._lock:
            return [
                {"job_id": j.job_id, "name": j.name, "cron": j.cron, "enabled": j.enabled}
                for j in self._jobs.values()
            ]

    def delete(self, job_id: str) -> bool:
        with self._lock:
            if job_id not in self._jobs:
                return False
            self._jobs[job_id].enabled = False
            del self._jobs[job_id]
            return True

    def health(self) -> Dict:
        return {"status": "ok", "job_count": len(self._jobs)}
