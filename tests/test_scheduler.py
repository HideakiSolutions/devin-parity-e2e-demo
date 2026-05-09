"""Unit tests for TaskScheduler."""
import pytest
from src.scheduler import TaskScheduler


def test_register_and_list():
    s = TaskScheduler()
    job_id = s.register("my-job", "*/5 * * * *", lambda: None)
    assert job_id
    jobs = s.list_jobs()
    assert any(j["job_id"] == job_id for j in jobs)


def test_delete():
    s = TaskScheduler()
    job_id = s.register("to-delete", "0 * * * *", lambda: None)
    assert s.delete(job_id) is True
    assert all(j["job_id"] != job_id for j in s.list_jobs())


def test_delete_nonexistent():
    s = TaskScheduler()
    assert s.delete("does-not-exist") is False


def test_health():
    s = TaskScheduler()
    h = s.health()
    assert h["status"] == "ok"
    assert isinstance(h["job_count"], int)
