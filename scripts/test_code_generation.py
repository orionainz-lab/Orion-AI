"""
Phase 2 Integration Test: Code Generation

This script tests the full code generation pipeline with 20 different tasks.
It validates the 95%+ first-attempt success rate target.

Requirements:
    - Temporal Server running (localhost:7233)
    - Worker running with Phase 2 components
    - ANTHROPIC_API_KEY configured in .env

Usage:
    # Quick test (5 tasks)
    python scripts/test_code_generation.py --quick
    
    # Full test (20 tasks)
    python scripts/test_code_generation.py
    
    # Offline test (no LLM, uses mock)
    python scripts/test_code_generation.py --offline
"""

import asyncio
import sys
import time
import argparse
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from temporalio.client import Client
from temporal.config import temporal_config
from verification.ast_verifier import verify_python_syntax

# ========== TEST TASKS ==========
# 20 tasks of varying complexity

TEST_TASKS = [
    # Simple functions (5 tasks)
    {
        "id": 1,
        "task": "Create a function that adds two numbers and returns the result",
        "difficulty": "simple"
    },
    {
        "id": 2,
        "task": "Create a function that reverses a string",
        "difficulty": "simple"
    },
    {
        "id": 3,
        "task": "Create a function that finds the maximum value in a list",
        "difficulty": "simple"
    },
    {
        "id": 4,
        "task": "Create a function that checks if a number is even",
        "difficulty": "simple"
    },
    {
        "id": 5,
        "task": "Create a function that counts vowels in a string",
        "difficulty": "simple"
    },
    
    # Medium functions (5 tasks)
    {
        "id": 6,
        "task": "Create a function that counts word frequencies in a text and returns a dictionary",
        "difficulty": "medium"
    },
    {
        "id": 7,
        "task": "Create a function that validates an email address using regex",
        "difficulty": "medium"
    },
    {
        "id": 8,
        "task": "Create a function that calculates factorial recursively",
        "difficulty": "medium"
    },
    {
        "id": 9,
        "task": "Create a function that generates Fibonacci numbers up to n",
        "difficulty": "medium"
    },
    {
        "id": 10,
        "task": "Create a function that removes duplicates from a list while preserving order",
        "difficulty": "medium"
    },
    
    # Complex functions (5 tasks)
    {
        "id": 11,
        "task": "Create a Calculator class with add, subtract, multiply, and divide methods",
        "difficulty": "complex"
    },
    {
        "id": 12,
        "task": "Create a dataclass for User with name, email, and age fields with validation",
        "difficulty": "complex"
    },
    {
        "id": 13,
        "task": "Create an async function that fetches data from a URL using aiohttp",
        "difficulty": "complex"
    },
    {
        "id": 14,
        "task": "Create a context manager for timing code execution",
        "difficulty": "complex"
    },
    {
        "id": 15,
        "task": "Create a decorator that logs function calls with arguments and return value",
        "difficulty": "complex"
    },
    
    # Advanced functions (5 tasks)
    {
        "id": 16,
        "task": "Create a binary search function that works on sorted lists",
        "difficulty": "advanced"
    },
    {
        "id": 17,
        "task": "Create a function that parses a JSON string and extracts nested values by path",
        "difficulty": "advanced"
    },
    {
        "id": 18,
        "task": "Create a generator function that yields prime numbers",
        "difficulty": "advanced"
    },
    {
        "id": 19,
        "task": "Create a function that merges two sorted lists into one sorted list",
        "difficulty": "advanced"
    },
    {
        "id": 20,
        "task": "Create a simple LRU cache implementation using OrderedDict",
        "difficulty": "advanced"
    },
]


# ========== TEST FUNCTIONS ==========

async def run_code_generation_test(
    client: Client,
    task: dict,
    workflow_prefix: str = "test"
) -> dict:
    """
    Run a single code generation test via Temporal workflow.
    
    Returns:
        Test result dictionary
    """
    from agents.workflows import CodeGenerationWorkflow
    
    task_id = task["id"]
    task_desc = task["task"]
    
    print(f"\n[Task {task_id}] {task_desc[:50]}...")
    
    workflow_id = f"{workflow_prefix}-codegen-{task_id}-{int(time.time())}"
    
    start_time = time.time()
    
    try:
        result = await client.execute_workflow(
            CodeGenerationWorkflow.run,
            args=[task_desc, "python", 3, None],
            id=workflow_id,
            task_queue=temporal_config.task_queue,
        )
        
        elapsed_ms = int((time.time() - start_time) * 1000)
        
        is_valid = result.get("is_valid", False)
        iterations = result.get("iterations", 0)
        code = result.get("code", "")
        
        # Determine first-attempt success
        first_attempt_success = is_valid and iterations == 1
        
        status = "[PASS]" if is_valid else "[FAIL]"
        attempt_info = "(1st attempt)" if first_attempt_success else f"({iterations} iterations)"
        
        print(f"  {status} {attempt_info} - {elapsed_ms}ms - {len(code)} chars")
        
        return {
            "task_id": task_id,
            "task": task_desc,
            "difficulty": task["difficulty"],
            "is_valid": is_valid,
            "iterations": iterations,
            "first_attempt_success": first_attempt_success,
            "code_length": len(code),
            "elapsed_ms": elapsed_ms,
            "workflow_id": workflow_id,
            "errors": result.get("errors", [])
        }
        
    except Exception as e:
        elapsed_ms = int((time.time() - start_time) * 1000)
        print(f"  [ERROR] {e}")
        
        return {
            "task_id": task_id,
            "task": task_desc,
            "difficulty": task["difficulty"],
            "is_valid": False,
            "iterations": 0,
            "first_attempt_success": False,
            "code_length": 0,
            "elapsed_ms": elapsed_ms,
            "workflow_id": workflow_id,
            "errors": [{"message": str(e)}]
        }


async def run_offline_test(task: dict) -> dict:
    """
    Run offline test (no LLM) - tests AST verification only.
    """
    task_id = task["id"]
    task_desc = task["task"]
    
    print(f"\n[Task {task_id}] {task_desc[:50]}... (offline)")
    
    # Generate simple code based on task
    simple_code = generate_mock_code(task_desc)
    
    # Verify with AST
    result = verify_python_syntax(simple_code)
    
    status = "[PASS]" if result["is_valid"] else "[FAIL]"
    print(f"  {status} (mock code)")
    
    return {
        "task_id": task_id,
        "task": task_desc,
        "difficulty": task["difficulty"],
        "is_valid": result["is_valid"],
        "iterations": 1,
        "first_attempt_success": result["is_valid"],
        "code_length": len(simple_code),
        "elapsed_ms": 5,
        "workflow_id": "offline",
        "errors": result.get("errors", [])
    }


def generate_mock_code(task: str) -> str:
    """Generate simple mock code for offline testing."""
    # Create basic function based on keywords in task
    if "add" in task.lower():
        return "def add(a: int, b: int) -> int:\n    return a + b"
    elif "reverse" in task.lower():
        return "def reverse(s: str) -> str:\n    return s[::-1]"
    elif "max" in task.lower():
        return "def find_max(lst: list) -> int:\n    return max(lst)"
    elif "even" in task.lower():
        return "def is_even(n: int) -> bool:\n    return n % 2 == 0"
    elif "class" in task.lower():
        return "class Calculator:\n    def add(self, a, b):\n        return a + b"
    else:
        return "def example():\n    pass"


def print_summary(results: list) -> dict:
    """Print test summary and return metrics."""
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    total = len(results)
    valid = sum(1 for r in results if r["is_valid"])
    first_attempt = sum(1 for r in results if r["first_attempt_success"])
    
    # By difficulty
    by_difficulty = {}
    for r in results:
        diff = r["difficulty"]
        if diff not in by_difficulty:
            by_difficulty[diff] = {"total": 0, "valid": 0, "first": 0}
        by_difficulty[diff]["total"] += 1
        if r["is_valid"]:
            by_difficulty[diff]["valid"] += 1
        if r["first_attempt_success"]:
            by_difficulty[diff]["first"] += 1
    
    # Calculate rates
    valid_rate = (valid / total * 100) if total > 0 else 0
    first_rate = (first_attempt / total * 100) if total > 0 else 0
    
    print(f"\nTotal Tasks: {total}")
    print(f"Valid Code: {valid}/{total} ({valid_rate:.1f}%)")
    print(f"First-Attempt Success: {first_attempt}/{total} ({first_rate:.1f}%)")
    
    print("\nBy Difficulty:")
    for diff, stats in sorted(by_difficulty.items()):
        d_rate = stats["valid"] / stats["total"] * 100
        f_rate = stats["first"] / stats["total"] * 100
        print(f"  {diff}: {stats['valid']}/{stats['total']} valid ({d_rate:.0f}%), "
              f"{stats['first']}/{stats['total']} first-attempt ({f_rate:.0f}%)")
    
    # Timing
    total_time = sum(r["elapsed_ms"] for r in results)
    avg_time = total_time / total if total > 0 else 0
    print(f"\nTotal Time: {total_time}ms")
    print(f"Average Time: {avg_time:.0f}ms per task")
    
    # Target check
    print("\n" + "-" * 60)
    target_met = first_rate >= 95
    if target_met:
        print("[SUCCESS] Target MET: 95%+ first-attempt success rate")
    else:
        print(f"[PENDING] Target NOT MET: {first_rate:.1f}% < 95%")
    print("-" * 60)
    
    return {
        "total": total,
        "valid": valid,
        "first_attempt": first_attempt,
        "valid_rate": valid_rate,
        "first_rate": first_rate,
        "total_time_ms": total_time,
        "avg_time_ms": avg_time,
        "target_met": target_met
    }


# ========== MAIN ==========

async def main():
    parser = argparse.ArgumentParser(description="Phase 2 Code Generation Tests")
    parser.add_argument("--quick", action="store_true", help="Run quick test (5 tasks)")
    parser.add_argument("--offline", action="store_true", help="Run offline (no LLM)")
    args = parser.parse_args()
    
    print("=" * 60)
    print("PHASE 2: CODE GENERATION INTEGRATION TESTS")
    print("=" * 60)
    
    # Select tasks
    if args.quick:
        tasks = TEST_TASKS[:5]
        print(f"Mode: QUICK ({len(tasks)} tasks)")
    else:
        tasks = TEST_TASKS
        print(f"Mode: FULL ({len(tasks)} tasks)")
    
    results = []
    
    if args.offline:
        print("Running OFFLINE tests (no LLM, AST verification only)")
        for task in tasks:
            result = await run_offline_test(task)
            results.append(result)
    else:
        print(f"Connecting to Temporal: {temporal_config.host}")
        
        try:
            client = await Client.connect(
                temporal_config.host,
                namespace=temporal_config.namespace
            )
            print("Connected to Temporal Server")
            print("Note: Worker must be running with Phase 2 workflows")
            
            for task in tasks:
                result = await run_code_generation_test(client, task)
                results.append(result)
                
        except Exception as e:
            print(f"\n[ERROR] Could not connect to Temporal: {e}")
            print("Make sure Temporal is running and worker is started")
            sys.exit(1)
    
    # Print summary
    metrics = print_summary(results)
    
    # Exit code based on target
    sys.exit(0 if metrics["target_met"] else 1)


if __name__ == "__main__":
    asyncio.run(main())
