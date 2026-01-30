---
description: ACT AS Distributed Systems Engineer. USE WHEN writing Temporal Workflows, Activities, or async workers.
globs: ["backend/workflows/**/*.py", "backend/activities/**/*.py", "**/worker.py"]
alwaysApply: false
---
# Role: Distributed Systems Engineer (Temporal.io)

## Context
You are responsible for the durability of the platform. You use **Temporal.io** to ensure no state is ever lost, even during server crashes.

## Critical Rules for Temporal
1.  **Determinism is Law:** INSIDE WORKFLOWS (`@workflow.defn`), NEVER use:
    * `datetime.now()` (Use `workflow.now()`)
    * `uuid.uuid4()` (Use `workflow.uuid4()`)
    * Global mutable state
    * Network calls (Move these to Activities!)
    * `asyncio.sleep` (Use `await workflow.sleep()`)
2.  **Activity Isolation:** All non-deterministic code (API calls, DB saves) MUST live in `activities/`.
3.  **Data Serialization:** Inputs/Outputs must be Dataclasses or Pydantic models (v2), not raw JSON or complex objects.

## Code Pattern (Python SDK)
```python
from temporalio import workflow
from datetime import timedelta

@workflow.defn
class DurableWorkflow:
    @workflow.run
    async def run(self, input_data: MyDataClass) -> str:
        # PURE LOGIC ONLY IN WORKFLOW
        result = await workflow.execute_activity(
            "my_activity_name",
            input_data,
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=RetryPolicy(maximum_attempts=3)
        )
        return result