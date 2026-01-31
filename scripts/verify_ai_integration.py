#!/usr/bin/env python3
"""
Verify AI Integration: LangGraph + Temporal + RAG
==================================================
Checks if all AI systems are properly configured and working.

Usage:
    python scripts/verify_ai_integration.py
"""

import os
import sys
import asyncio
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")


def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def print_status(item: str, status: str, details: str = ""):
    """Print status line."""
    icon = "[PASS]" if status == "ok" else "[FAIL]" if status == "fail" else "[WARN]"
    print(f"{icon} {item}")
    if details:
        print(f"      -> {details}")


def check_env_var(name: str, sensitive: bool = True) -> tuple[bool, str]:
    """Check if environment variable is set."""
    value = os.getenv(name)
    if not value:
        return False, "NOT SET"
    if sensitive:
        return True, f"{value[:10]}...{value[-4:]}" if len(value) > 14 else "***"
    return True, value


# ============================================================
# CHECK 1: ENVIRONMENT VARIABLES
# ============================================================
def check_environment():
    """Check required environment variables."""
    print_header("1. ENVIRONMENT VARIABLES")
    
    results = {}
    
    # LangGraph/LLM APIs
    print("\n--- LLM APIs (for LangGraph) ---")
    
    anthropic_ok, anthropic_val = check_env_var("ANTHROPIC_API_KEY")
    print_status("ANTHROPIC_API_KEY", "ok" if anthropic_ok else "fail", anthropic_val)
    results["anthropic"] = anthropic_ok
    
    openai_ok, openai_val = check_env_var("OPENAI_API_KEY")
    print_status("OPENAI_API_KEY", "ok" if openai_ok else "warn", openai_val)
    results["openai"] = openai_ok
    
    # Temporal
    print("\n--- Temporal Configuration ---")
    
    temporal_host_ok, temporal_host = check_env_var("TEMPORAL_HOST", False)
    print_status("TEMPORAL_HOST", "ok" if temporal_host_ok else "fail", temporal_host)
    results["temporal_host"] = temporal_host_ok
    
    temporal_ns_ok, temporal_ns = check_env_var("TEMPORAL_NAMESPACE", False)
    print_status("TEMPORAL_NAMESPACE", "ok" if temporal_ns_ok else "fail", temporal_ns)
    results["temporal_ns"] = temporal_ns_ok
    
    # Supabase (for RAG)
    print("\n--- Supabase (for RAG) ---")
    
    supabase_url_ok, supabase_url = check_env_var("SUPABASE_URL", False)
    print_status("SUPABASE_URL", "ok" if supabase_url_ok else "fail", supabase_url)
    results["supabase_url"] = supabase_url_ok
    
    supabase_anon_ok, supabase_anon = check_env_var("SUPABASE_ANON_KEY")
    print_status("SUPABASE_ANON_KEY", "ok" if supabase_anon_ok else "fail", supabase_anon)
    results["supabase_anon"] = supabase_anon_ok
    
    return results


# ============================================================
# CHECK 2: PYTHON PACKAGES
# ============================================================
def check_packages():
    """Check required Python packages."""
    print_header("2. PYTHON PACKAGES")
    
    results = {}
    packages = [
        ("langgraph", "LangGraph reasoning framework"),
        ("temporalio", "Temporal workflow engine"),
        ("anthropic", "Claude API client"),
        ("openai", "OpenAI API client (embeddings)"),
        ("supabase", "Supabase client"),
        ("sentence_transformers", "Local embedding fallback"),
    ]
    
    for pkg_name, description in packages:
        try:
            __import__(pkg_name)
            print_status(f"{pkg_name}", "ok", description)
            results[pkg_name] = True
        except ImportError:
            print_status(f"{pkg_name}", "fail", f"NOT INSTALLED - {description}")
            results[pkg_name] = False
    
    return results


# ============================================================
# CHECK 3: LANGGRAPH INTEGRATION
# ============================================================
def check_langgraph():
    """Check LangGraph components."""
    print_header("3. LANGGRAPH INTEGRATION")
    
    results = {}
    
    # Check graph builder
    try:
        from agents.graph_builder import build_code_generation_graph
        print_status("Graph Builder", "ok", "build_code_generation_graph() found")
        results["graph_builder"] = True
    except ImportError as e:
        print_status("Graph Builder", "fail", str(e))
        results["graph_builder"] = False
    
    # Check nodes
    try:
        from agents.nodes import plan_node, generate_node, verify_node, correct_node
        print_status("Reasoning Nodes", "ok", "4 nodes: plan, generate, verify, correct")
        results["nodes"] = True
    except ImportError as e:
        print_status("Reasoning Nodes", "fail", str(e))
        results["nodes"] = False
    
    # Check LLM clients
    try:
        from agents.llm_clients import call_llm_for_plan, call_llm_for_code
        print_status("LLM Clients", "ok", "call_llm_for_plan, call_llm_for_code")
        results["llm_clients"] = True
    except ImportError as e:
        print_status("LLM Clients", "fail", str(e))
        results["llm_clients"] = False
    
    # Check config
    try:
        from agents.config import llm_config
        print_status("LLM Config", "ok", f"Model: {llm_config.primary_model}")
        results["config"] = True
    except Exception as e:
        print_status("LLM Config", "fail", str(e))
        results["config"] = False
    
    # Check AST verifier
    try:
        from verification.ast_verifier import verify_python_syntax
        test_result = verify_python_syntax("def hello(): pass")
        status = "ok" if test_result["is_valid"] else "fail"
        print_status("AST Verifier", status, "verify_python_syntax() working")
        results["ast_verifier"] = test_result["is_valid"]
    except Exception as e:
        print_status("AST Verifier", "fail", str(e))
        results["ast_verifier"] = False
    
    return results


# ============================================================
# CHECK 4: TEMPORAL INTEGRATION
# ============================================================
def check_temporal():
    """Check Temporal components."""
    print_header("4. TEMPORAL INTEGRATION")
    
    results = {}
    
    # Check workflows
    try:
        from agents.workflows import CodeGenerationWorkflow
        print_status("Code Generation Workflow", "ok", "CodeGenerationWorkflow found")
        results["workflow"] = True
    except ImportError as e:
        print_status("Code Generation Workflow", "fail", str(e))
        results["workflow"] = False
    
    # Check activities
    try:
        from agents.activities import execute_code_generation
        print_status("Code Generation Activity", "ok", "execute_code_generation found")
        results["activity"] = True
    except ImportError as e:
        print_status("Code Generation Activity", "fail", str(e))
        results["activity"] = False
    
    # Check worker config
    try:
        from temporal.config import temporal_config
        print_status("Temporal Config", "ok", f"Host: {temporal_config.host}")
        results["temporal_config"] = True
    except ImportError as e:
        print_status("Temporal Config", "fail", str(e))
        results["temporal_config"] = False
    
    # Check if Temporal server is reachable
    try:
        import socket
        host = os.getenv("TEMPORAL_HOST", "localhost:7233")
        host_parts = host.split(":")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        result = sock.connect_ex((host_parts[0], int(host_parts[1])))
        sock.close()
        if result == 0:
            print_status("Temporal Server", "ok", f"Reachable at {host}")
            results["server"] = True
        else:
            print_status("Temporal Server", "warn", f"NOT reachable at {host}")
            results["server"] = False
    except Exception as e:
        print_status("Temporal Server", "warn", f"Could not check: {e}")
        results["server"] = False
    
    return results


# ============================================================
# CHECK 5: RAG INTEGRATION
# ============================================================
async def check_rag():
    """Check RAG components."""
    print_header("5. RAG INTEGRATION")
    
    results = {}
    
    # Check embedding service
    try:
        from services.embedding_service import EmbeddingService
        print_status("Embedding Service", "ok", "EmbeddingService found")
        results["embedding_service"] = True
    except ImportError as e:
        print_status("Embedding Service", "fail", str(e))
        results["embedding_service"] = False
    
    # Check RAG service
    try:
        from services.rag_service import RAGService
        print_status("RAG Service", "ok", "RAGService found")
        results["rag_service"] = True
    except ImportError as e:
        print_status("RAG Service", "fail", str(e))
        results["rag_service"] = False
    
    # Check context builder
    try:
        from services.context_builder import ContextBuilder
        print_status("Context Builder", "ok", "ContextBuilder found")
        results["context_builder"] = True
    except ImportError as e:
        print_status("Context Builder", "fail", str(e))
        results["context_builder"] = False
    
    # Check vector table exists
    try:
        from supabase import create_client
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        if url and key:
            client = create_client(url, key)
            # Check document_chunks table
            result = client.table("document_chunks").select("id").limit(1).execute()
            print_status("Vector Table", "ok", "document_chunks table accessible")
            results["vector_table"] = True
        else:
            print_status("Vector Table", "warn", "Supabase credentials not set")
            results["vector_table"] = False
    except Exception as e:
        print_status("Vector Table", "warn", f"Could not verify: {str(e)[:50]}")
        results["vector_table"] = False
    
    return results


# ============================================================
# CHECK 6: LIVE API TESTS
# ============================================================
async def check_live_apis():
    """Test live API connections."""
    print_header("6. LIVE API TESTS")
    
    results = {}
    
    # Test Anthropic API
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if api_key and api_key != "your-anthropic-api-key-here":
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            # Quick test with latest model
            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=10,
                messages=[{"role": "user", "content": "Say hi"}]
            )
            print_status("Anthropic API", "ok", f"Claude responding: {response.content[0].text[:20]}")
            results["anthropic_live"] = True
        else:
            print_status("Anthropic API", "fail", "API key not configured")
            results["anthropic_live"] = False
    except Exception as e:
        error_msg = str(e)[:60]
        print_status("Anthropic API", "warn", f"API error: {error_msg}")
        results["anthropic_live"] = False
    
    # Test OpenAI API (for embeddings)
    try:
        api_key = os.getenv("OPENAI_API_KEY")
        if api_key and api_key != "your-key-here":
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input="test"
            )
            print_status("OpenAI Embeddings", "ok", "Embedding API responding")
            results["openai_live"] = True
        else:
            print_status("OpenAI Embeddings", "warn", "API key not configured (using local fallback)")
            results["openai_live"] = False
    except Exception as e:
        error_msg = str(e)[:60]
        print_status("OpenAI Embeddings", "warn", f"Not available: {error_msg}")
        results["openai_live"] = False
    
    return results


# ============================================================
# SUMMARY
# ============================================================
def print_summary(all_results: dict):
    """Print summary of all checks."""
    print_header("SUMMARY")
    
    # Count results
    total = 0
    passed = 0
    failed = 0
    warned = 0
    
    for category, results in all_results.items():
        for key, value in results.items():
            total += 1
            if value is True:
                passed += 1
            elif value is False:
                failed += 1
            else:
                warned += 1
    
    print(f"\n  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    print(f"  Warnings: {warned}")
    
    # Specific recommendations
    print("\n" + "-" * 60)
    print("  MISSING API KEYS (Action Required)")
    print("-" * 60)
    
    anthropic_key = os.getenv("ANTHROPIC_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    missing = []
    
    if not anthropic_key or anthropic_key == "your-anthropic-api-key-here":
        missing.append("ANTHROPIC_API_KEY")
        print("\n  [CRITICAL] ANTHROPIC_API_KEY not set")
        print("  -> Required for: LangGraph code generation (Claude)")
        print("  -> Get key at: https://console.anthropic.com/")
        print("  -> Add to .env: ANTHROPIC_API_KEY=sk-ant-...")
    
    if not openai_key or openai_key == "your-key-here":
        missing.append("OPENAI_API_KEY")
        print("\n  [OPTIONAL] OPENAI_API_KEY not set")
        print("  -> Required for: RAG embeddings (text-embedding-3-small)")
        print("  -> Fallback: Local sentence-transformers (slower)")
        print("  -> Get key at: https://platform.openai.com/api-keys")
        print("  -> Add to .env: OPENAI_API_KEY=sk-...")
    
    if not missing:
        print("\n  All API keys configured!")
    
    # Integration status
    print("\n" + "-" * 60)
    print("  INTEGRATION STATUS")
    print("-" * 60)
    
    langgraph_ok = all_results.get("langgraph", {})
    temporal_ok = all_results.get("temporal", {})
    rag_ok = all_results.get("rag", {})
    
    print(f"\n  LangGraph:  {'READY' if all(langgraph_ok.values()) else 'NEEDS ATTENTION'}")
    print(f"  Temporal:   {'READY' if temporal_ok.get('workflow') and temporal_ok.get('activity') else 'NEEDS ATTENTION'}")
    print(f"  RAG:        {'READY' if all(rag_ok.values()) else 'NEEDS ATTENTION'}")
    
    return missing


# ============================================================
# MAIN
# ============================================================
async def main():
    """Run all checks."""
    print("\n")
    print("*" * 60)
    print("*  ORION-AI: AI INTEGRATION VERIFICATION")
    print("*" * 60)
    
    all_results = {}
    
    # Run checks
    all_results["env"] = check_environment()
    all_results["packages"] = check_packages()
    all_results["langgraph"] = check_langgraph()
    all_results["temporal"] = check_temporal()
    all_results["rag"] = await check_rag()
    all_results["apis"] = await check_live_apis()
    
    # Print summary
    missing = print_summary(all_results)
    
    print("\n" + "=" * 60)
    if missing:
        print("  STATUS: CONFIGURATION INCOMPLETE")
        print(f"  Missing: {', '.join(missing)}")
    else:
        print("  STATUS: ALL SYSTEMS READY")
    print("=" * 60 + "\n")
    
    return len(missing) == 0


if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
