#!/usr/bin/env python3
"""
Phase 3: Document Ingestion CLI

Command-line tool for batch document ingestion.
Usage: python scripts/ingest_documents.py
"""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
load_dotenv()


def progress_callback(current: int, total: int, title: str):
    """Print progress for batch ingestion."""
    percent = (current / total) * 100
    print(f"[{current}/{total}] ({percent:.0f}%) {title}")


async def ingest_sample_documents():
    """Ingest sample documents for testing."""
    print("="*60)
    print("PHASE 3: Document Ingestion")
    print("="*60)
    
    # Check environment
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role for ingestion
    
    if not supabase_url or not supabase_key:
        print("\nERROR: Missing Supabase credentials")
        print("Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")
        return False
    
    # Initialize services
    from supabase import create_client
    from services.document_ingestion import DocumentIngestionService
    
    supabase = create_client(supabase_url, supabase_key)
    ingestion_service = DocumentIngestionService(supabase)
    
    # Sample documents
    documents = [
        {
            'title': 'Python Async Best Practices',
            'content': '''
            Python async programming allows concurrent execution of I/O-bound tasks.
            
            Key concepts:
            1. async/await syntax for defining coroutines
            2. asyncio.create_task() for concurrent execution
            3. asyncio.gather() for waiting on multiple tasks
            
            Best practices:
            - Use async for I/O operations (database, API calls)
            - Avoid blocking calls inside async functions
            - Handle exceptions with try/except in coroutines
            ''',
            'created_by': '00000000-0000-0000-0000-000000000000',  # Placeholder
            'document_type': 'guide',
            'visibility': 'public'
        },
        {
            'title': 'Supabase RLS Patterns',
            'content': '''
            Row Level Security (RLS) in Supabase enforces permissions at the database level.
            
            Common patterns:
            1. Owner-only: WHERE created_by = auth.uid()
            2. Team-based: WHERE team_id IN (SELECT team_id FROM team_members WHERE user_id = auth.uid())
            3. Public: WHERE visibility = 'public'
            
            Security notes:
            - Always enable RLS on user-facing tables
            - Test with actual user JWTs, not service_role
            - Use EXPLAIN to check RLS query performance
            ''',
            'created_by': '00000000-0000-0000-0000-000000000000',
            'document_type': 'guide',
            'visibility': 'public'
        }
    ]
    
    print(f"\nIngesting {len(documents)} sample documents...")
    
    # Ingest batch
    stats = await ingestion_service.ingest_documents_batch(
        documents,
        progress_callback=progress_callback
    )
    
    # Print results
    print("\n" + "="*60)
    print("INGESTION COMPLETE")
    print("="*60)
    print(f"\nTotal documents: {stats['total_documents']}")
    print(f"Successful: {stats['successful']}")
    print(f"Failed: {stats['failed']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Total embeddings: {stats['total_embeddings']}")
    
    if stats['errors']:
        print("\nErrors:")
        for error in stats['errors']:
            print(f"  - {error['title']}: {error['error']}")
    
    return stats['failed'] == 0


def main():
    """Run document ingestion."""
    loop = asyncio.get_event_loop()
    success = loop.run_until_complete(ingest_sample_documents())
    
    return 0 if success else 1


if __name__ == '__main__':
    sys.exit(main())
