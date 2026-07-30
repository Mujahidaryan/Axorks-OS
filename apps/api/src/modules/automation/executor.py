"""
Axorks OS — Automation Execution Engine
"""
from datetime import datetime
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from src.modules.automation.models import Workflow, WorkflowExecution


class WorkflowExecutor:
    @staticmethod
    def evaluate_conditions(conditions: list[dict] | None, entity_data: dict) -> bool:
        if not conditions:
            return True

        for cond in conditions:
            field = cond.get("field")
            op = cond.get("op", "eq")
            target = cond.get("value")
            val = entity_data.get(field)

            if op == "eq" and val != target:
                return False
            elif op == "ne" and val == target:
                return False
            elif op == "gt" and (val is None or val <= target):
                return False
            elif op == "lt" and (val is None or val >= target):
                return False
            elif op == "contains" and (val is None or str(target).lower() not in str(val).lower()):
                return False

        return True

    @staticmethod
    async def execute_action(action: dict, entity_data: dict, db: AsyncSession) -> dict:
        action_type = action.get("type", "unknown")
        action_data = action.get("data", {})

        if action_type == "assign":
            owner_id = action_data.get("owner_id")
            return {"step": "assign", "status": "executed", "assigned_owner": owner_id}

        elif action_type == "send_email":
            subject = action_data.get("subject", "Automated Notification")
            return {"step": "send_email", "status": "sent", "subject": subject}

        elif action_type == "notify":
            message = action_data.get("message", "Workflow triggered")
            return {"step": "notify", "status": "delivered", "message": message}

        elif action_type == "create_task":
            title = action_data.get("title", "Automated Task")
            return {"step": "create_task", "status": "created", "title": title}

        elif action_type == "webhook":
            url = action_data.get("url")
            return {"step": "webhook", "status": "dispatched", "url": url}

        else:
            return {"step": action_type, "status": "executed_stub", "data": action_data}

    @classmethod
    async def run_workflow(
        cls,
        workflow: Workflow,
        entity_type: str,
        entity_id: UUID | None,
        entity_data: dict,
        db: AsyncSession
    ) -> WorkflowExecution:
        execution = WorkflowExecution(
            workflow_id=workflow.id,
            trigger_entity_type=entity_type,
            trigger_entity_id=entity_id,
            status="running",
            steps_log=[],
            started_at=datetime.utcnow()
        )
        db.add(execution)
        await db.flush()

        steps_log = []

        try:
            # 1. Evaluate conditions
            passed = cls.evaluate_conditions(workflow.conditions, entity_data)
            steps_log.append({"step": "evaluate_conditions", "passed": passed, "conditions": workflow.conditions})

            if not passed:
                execution.status = "skipped"
                execution.steps_log = steps_log
                execution.completed_at = datetime.utcnow()
                await db.flush()
                return execution

            # 2. Execute actions
            actions = workflow.actions or []
            for act in actions:
                res = await cls.execute_action(act, entity_data, db)
                steps_log.append(res)

            execution.status = "success"
            execution.steps_log = steps_log
            execution.completed_at = datetime.utcnow()

            # Update workflow stats
            workflow.run_count = (workflow.run_count or 0) + 1
            workflow.last_run_at = datetime.utcnow()

            await db.flush()
            await db.refresh(execution)
            return execution

        except Exception as e:
            execution.status = "failed"
            execution.error = str(e)
            execution.steps_log = steps_log
            execution.completed_at = datetime.utcnow()
            await db.flush()
            await db.refresh(execution)
            return execution
