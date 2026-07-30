import pytest
from uuid import uuid4
from src.modules.automation.service import AutomationService
from src.modules.automation.schemas import WorkflowCreate

@pytest.mark.asyncio
async def test_automation_flow(db):
    svc = AutomationService(db)
    org_id = uuid4()
    ws_id = uuid4()
    user_id = uuid4()

    # 1. Create Workflow
    wf_data = WorkflowCreate(
        name="Auto-assign Lead Workflow",
        trigger_type="entity_event",
        trigger_config={"entity": "lead", "event": "created"},
        conditions=[{"field": "score", "op": "gt", "value": 50}],
        actions=[{"type": "assign", "data": {"owner_id": str(user_id)}}]
    )
    wf = await svc.create_workflow(org_id, ws_id, user_id, wf_data)
    assert wf.name == "Auto-assign Lead Workflow"

    # 2. Trigger Test Run (passing condition)
    exec_pass = await svc.trigger_test_run(
        wf.id, org_id, entity_type="lead", entity_id=uuid4(), entity_data={"score": 80}
    )
    assert exec_pass.status == "success"
    assert len(exec_pass.steps_log) >= 2

    # 3. Trigger Test Run (failing condition -> skipped)
    exec_skip = await svc.trigger_test_run(
        wf.id, org_id, entity_type="lead", entity_id=uuid4(), entity_data={"score": 30}
    )
    assert exec_skip.status == "skipped"
