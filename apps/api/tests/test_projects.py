"""
Axorks OS — Phase 6: Project Management Tests

Tests Projects CRUD, Sprints CRUD, Tasks CRUD, Kanban status updates, and Time Entries.
"""

import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_project_crud_and_tasks(auth_client: AsyncClient):
    # 1. Create Project
    res = await auth_client.post(
        "/api/v1/projects",
        json={
            "name": "SaaS Platform Delivery",
            "budget": 75000.00,
            "currency": "USD",
            "status": "active",
        },
    )
    assert res.status_code == 200
    project = res.json()["data"]
    project_id = project["id"]
    assert project["name"] == "SaaS Platform Delivery"

    # 2. List Projects
    res = await auth_client.get("/api/v1/projects")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1

    # 3. Create Sprint
    res = await auth_client.post(
        "/api/v1/projects/sprints",
        json={
            "project_id": project_id,
            "name": "Sprint 1 — Core Architecture",
            "goal": "Deliver user auth and database schema",
        },
    )
    assert res.status_code == 200
    sprint = res.json()["data"]
    sprint_id = sprint["id"]
    assert sprint["name"] == "Sprint 1 — Core Architecture"

    # 4. Create Task
    res = await auth_client.post(
        "/api/v1/projects/tasks",
        json={
            "project_id": project_id,
            "sprint_id": sprint_id,
            "title": "Implement Async PostgreSQL Database Connection",
            "type": "task",
            "status": "in_progress",
            "priority": "high",
            "estimate_hours": 8.0,
        },
    )
    assert res.status_code == 200
    task = res.json()["data"]
    task_id = task["id"]
    assert task["title"] == "Implement Async PostgreSQL Database Connection"

    # 5. Update Task Status (Kanban move to Done)
    res = await auth_client.patch(
        f"/api/v1/projects/tasks/{task_id}",
        json={"status": "done"},
    )
    assert res.status_code == 200
    assert res.json()["data"]["status"] == "done"

    # 6. Log Time
    res = await auth_client.post(
        "/api/v1/projects/time",
        json={
            "project_id": project_id,
            "task_id": task_id,
            "hours": 6.5,
            "description": "Implemented asyncpg connection pool and alembic migrations.",
            "logged_date": "2026-07-29",
        },
    )
    assert res.status_code == 200
    entry = res.json()["data"]
    assert float(entry["hours"]) == 6.5

    # 7. List Time Entries
    res = await auth_client.get(f"/api/v1/projects/time?project_id={project_id}")
    assert res.status_code == 200
    assert len(res.json()["data"]) >= 1
