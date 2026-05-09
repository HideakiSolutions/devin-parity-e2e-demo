# Technical Specification: Lightweight Task Scheduling Service

## 1. Architecture Overview

**Pattern:** Event-Driven Microservice with Priority Queue Scheduler

```
REST API Layer (FastAPI)
        ↓
Job Manager (Registry + Validation)
        ↓
Scheduler Engine (Priority Queue + Cron Parser)
        ↓
Executor (Async Job Runner)
```

## 2. Core Components

### 2.1 Job Registry
- **In-Memory Storage:** Dictionary-based with job ID as key
- **Data Structure:** Job objects (id, name, cron_expression, status, created_at, last_run, next_run)
- **Concurrency:** Thread-safe access via `threading.Lock`

### 2.2 Scheduler Engine
- **Priority Queue:** Use `heapq` module (min-heap by next_run timestamp)
- **Cron Parser:** Integrate `croniter` library for expression validation
- **Background Worker:** Async task running on separate thread
- **Job Execution:** Trigger callable functions or webhook POST requests

### 2.3 REST API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| POST | `/jobs` | Create job (name, cron_expr, callback) |
| GET | `/jobs` | List all jobs with status |
| GET | `/jobs/{id}` | Get job details |
| DELETE | `/jobs/{id}` | Remove job |
| PATCH | `/jobs/{id}` | Update cron/status |
| GET | `/health` | Service health check |
| GET | `/metrics` | Execution metrics |

### 2.4 Health & Metrics Endpoints
- **Health:** `{status: "healthy", uptime_seconds, scheduler_active}`
- **Metrics:** `{total_jobs, completed_jobs, failed_jobs, avg_execution_ms, next_execution_time}`

## 3. Technical Constraints

| Constraint | Decision |
|-----------|----------|
| **Framework** | FastAPI (async, auto-OpenAPI docs) |
| **Storage** | In-memory only (no persistence layer) |
| **Execution Model** | Async with thread pool for blocking jobs |
| **Max Jobs** | 10,000 (configurable via env) |
| **Cron Validation** | Standard POSIX 5-field format |
| **Error Handling** | Silent failure + logging (no job retry by default) |
| **Dependencies** | fastapi, croniter, pydantic |

## 4. Data Models (Pydantic)

```python
class Job(BaseModel):
    id: str
    name: str
    cron_expression: str
    status: Literal["active", "paused", "failed"]
    callback_url: Optional[str]  # webhook endpoint
    created_at: datetime
    last_run: Optional[datetime]
    next_run: datetime
    execution_count: int = 0
```

## 5. Design Decisions

1. **Priority Queue Over Polling:** O(log n) job scheduling vs O(n) scanning
2. **Thread Safety:** Lock-based instead of queue.Queue (simpler for in-memory registry)
3. **No Persistence:** Simplifies MVP; jobs lost on restart
4. **Webhook Pattern:** Supports both internal callbacks and external services
5. **Fail-Safe Execution:** Exceptions logged, don't block scheduler

## 6. Non-Functional Requirements

- **Throughput:** ≥100 concurrent jobs
- **Latency:** Job trigger within 1 second of scheduled time
- **Availability:** 99.5% (graceful degradation on resource limits)
- **Memory:** <100MB baseline + ~1KB per job

## 7. Future Extensions (Out of Scope)

- Distributed scheduling (Redis backend)
- Job persistence / database
- Retry logic & dead-letter queues
- Job dependencies / workflows
- Timezone support for cron expressions

---

**Delivery Artifacts:** Source code (main.py + modules), requirements.txt, OpenAPI spec, unit tests (≥80% coverage)