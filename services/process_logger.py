"""
Phase 3: Process Logger Service

Logs workflow and agent events to Supabase for process intelligence.
Integrates with Temporal activities for audit trail.
"""

from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class ProcessLogger:
    """Log process events for audit and analytics."""
    
    def __init__(self, supabase_client):
        """
        Initialize process logger.
        
        Args:
            supabase_client: Supabase client (use service_role for inserts)
        """
        self.supabase = supabase_client
    
    async def log_event(
        self,
        event_type: str,
        event_name: str,
        user_id: Optional[str] = None,
        workflow_id: Optional[str] = None,
        workflow_run_id: Optional[str] = None,
        activity_id: Optional[str] = None,
        input_data: Optional[Dict] = None,
        output_data: Optional[Dict] = None,
        error_data: Optional[Dict] = None,
        status: str = "completed",
        duration_ms: Optional[int] = None,
        metadata: Optional[Dict] = None
    ) -> None:
        """
        Log single process event.
        
        Args:
            event_type: Type of event (workflow_start, rag_query, etc.)
            event_name: Human-readable event name
            user_id: User who triggered event
            workflow_id: Temporal workflow ID
            workflow_run_id: Temporal run ID
            activity_id: Temporal activity ID
            input_data: Event input (JSON)
            output_data: Event output (JSON)
            error_data: Error details (JSON)
            status: Event status (started, completed, failed)
            duration_ms: Execution duration in milliseconds
            metadata: Additional metadata (JSON)
        """
        try:
            self.supabase.table('process_events').insert({
                'event_type': event_type,
                'event_name': event_name,
                'user_id': user_id,
                'workflow_id': workflow_id,
                'workflow_run_id': workflow_run_id,
                'activity_id': activity_id,
                'input_data': input_data,
                'output_data': output_data,
                'error_data': error_data,
                'status': status,
                'duration_ms': duration_ms,
                'event_timestamp': datetime.utcnow().isoformat(),
                'metadata': metadata or {}
            }).execute()
            
            logger.debug(f"Logged event: {event_type}/{event_name}")
            
        except Exception as e:
            # Don't fail workflow on logging error
            logger.warning(f"Failed to log event: {e}")
    
    async def log_workflow_start(
        self,
        workflow_id: str,
        user_id: str,
        task: str
    ):
        """Log workflow start event."""
        await self.log_event(
            event_type='workflow_start',
            event_name='code_generation',
            user_id=user_id,
            workflow_id=workflow_id,
            input_data={'task': task},
            status='started'
        )
    
    async def log_workflow_complete(
        self,
        workflow_id: str,
        user_id: str,
        result: Dict,
        duration_ms: int
    ):
        """Log workflow completion event."""
        await self.log_event(
            event_type='workflow_complete',
            event_name='code_generation',
            user_id=user_id,
            workflow_id=workflow_id,
            output_data=result,
            status='completed',
            duration_ms=duration_ms
        )
    
    async def log_workflow_failed(
        self,
        workflow_id: str,
        user_id: str,
        error: str,
        duration_ms: int
    ):
        """Log workflow failure event."""
        await self.log_event(
            event_type='workflow_failed',
            event_name='code_generation',
            user_id=user_id,
            workflow_id=workflow_id,
            error_data={'error': error},
            status='failed',
            duration_ms=duration_ms
        )
    
    async def log_rag_query(
        self,
        query_text: str,
        user_id: str,
        result_count: int,
        document_ids: List[str],
        avg_similarity: float,
        duration_ms: int
    ):
        """Log RAG query event."""
        await self.log_event(
            event_type='rag_query',
            event_name='semantic_search',
            user_id=user_id,
            input_data={'query': query_text},
            output_data={
                'result_count': result_count,
                'document_ids': document_ids,
                'avg_similarity': avg_similarity
            },
            status='completed',
            duration_ms=duration_ms
        )
