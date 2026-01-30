"""
Temporal Worker Process
Connects to Temporal Server and executes workflows/activities

Phase 1: Durability foundation (DurableDemoWorkflow, ApprovalWorkflow)
Phase 2: AI code generation (CodeGenerationWorkflow)
"""

import asyncio
import logging
import signal
import sys
from pathlib import Path

from temporalio.client import Client
from temporalio.worker import Worker

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from temporal.config import temporal_config

# Phase 1 workflows and activities
from temporal.workflows.durable_demo import DurableDemoWorkflow
from temporal.workflows.approval_workflow import ApprovalWorkflow
from temporal.activities.test_activities import (
    process_step,
    log_event,
    process_request,
    record_decision,
    send_notification,
    long_running_task,
)

# Phase 2 workflows and activities
from agents.workflows import CodeGenerationWorkflow
from agents.activities import execute_code_generation, verify_code_syntax

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


# Global worker instance for graceful shutdown
_worker_instance = None


def handle_shutdown(signum, frame):
    """Handle shutdown signals gracefully"""
    logger.info(f"Received signal {signum}, initiating graceful shutdown...")
    # Worker shutdown is handled by asyncio event loop


async def create_worker(client: Client) -> Worker:
    """
    Create and configure worker.
    
    Phase 1 + 2: Single monolithic worker
    - Task queue: "default"
    - Phase 1: DurableDemoWorkflow, ApprovalWorkflow
    - Phase 2: CodeGenerationWorkflow
    
    Args:
        client: Connected Temporal client
    
    Returns:
        Configured Worker instance
    """
    # Combine Phase 1 and Phase 2 workflows
    workflows = [
        # Phase 1
        DurableDemoWorkflow,
        ApprovalWorkflow,
        # Phase 2
        CodeGenerationWorkflow,
    ]
    
    # Combine Phase 1 and Phase 2 activities
    activities = [
        # Phase 1 activities
        process_step,
        log_event,
        process_request,
        record_decision,
        send_notification,
        long_running_task,
        # Phase 2 activities
        execute_code_generation,
        verify_code_syntax,
    ]
    
    worker = Worker(
        client,
        task_queue=temporal_config.task_queue,
        workflows=workflows,
        activities=activities,
    )
    
    logger.info(f"Worker created on task_queue='{temporal_config.task_queue}'")
    logger.info(f"Registered workflows: {len(workflows)} total")
    logger.info(f"  Phase 1: DurableDemoWorkflow, ApprovalWorkflow")
    logger.info(f"  Phase 2: CodeGenerationWorkflow")
    logger.info(f"Registered activities: {len(activities)} total")
    logger.info(f"  Phase 1: 6 activities")
    logger.info(f"  Phase 2: 2 activities (execute_code_generation, verify_code_syntax)")
    
    return worker


async def main():
    """
    Main worker entry point.
    
    Connects to Temporal Server and starts polling for work.
    Handles graceful shutdown on SIGINT/SIGTERM.
    """
    global _worker_instance
    
    logger.info("=" * 60)
    logger.info("TEMPORAL WORKER STARTING")
    logger.info("=" * 60)
    logger.info(f"Connecting to Temporal Server: {temporal_config.host}")
    logger.info(f"Namespace: {temporal_config.namespace}")
    logger.info(f"Task Queue: {temporal_config.task_queue}")
    
    try:
        # Connect to Temporal Server
        client = await Client.connect(
            temporal_config.host,
            namespace=temporal_config.namespace,
        )
        logger.info("Connected to Temporal Server successfully")
        
        # Create worker
        _worker_instance = await create_worker(client)
        
        logger.info("=" * 60)
        logger.info("WORKER READY - Polling for workflows...")
        logger.info("Press Ctrl+C to stop")
        logger.info("=" * 60)
        
        # Run worker (blocks until shutdown)
        await _worker_instance.run()
        
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt received")
    except Exception as e:
        logger.error(f"Worker error: {e}", exc_info=True)
        raise
    finally:
        logger.info("Worker shutdown complete")


if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, handle_shutdown)
    signal.signal(signal.SIGTERM, handle_shutdown)
    
    # Run worker
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Worker stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)
