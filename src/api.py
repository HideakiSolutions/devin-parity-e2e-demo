"""REST API for TaskScheduler — FastAPI."""
from __future__ import annotations

from typing import Any, Dict, List

try:
    from fastapi import FastAPI, HTTPException
    from pydantic import BaseModel
except ImportError:
    raise SystemExit("fastapi and pydantic required: pip install fastapi pydantic")

from src.scheduler import TaskScheduler

app = FastAPI(title="Task Scheduler Service", version="0.1.0")
_scheduler = TaskScheduler()


class JobCreate(BaseModel):
    name: str
    cron: str


@app.get("/health")
def health() -> Dict[str, Any]:
    return _scheduler.health()


@app.post("/jobs", status_code=201)
def create_job(body: JobCreate) -> Dict[str, str]:
    job_id = _scheduler.register(body.name, body.cron, lambda: None)
    return {"job_id": job_id, "status": "registered"}


@app.get("/jobs")
def list_jobs() -> List[Dict]:
    return _scheduler.list_jobs()


@app.delete("/jobs/{job_id}")
def delete_job(job_id: str) -> Dict[str, str]:
    deleted = _scheduler.delete(job_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="job_not_found")
    return {"job_id": job_id, "status": "deleted"}
