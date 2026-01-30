#!/usr/bin/env python3
"""
Phase 3 VAN QA Mode - Master Test Runner

Executes all 6 validation tests and generates report.
"""

import subprocess
import sys
from datetime import datetime
from typing import Dict, List, Tuple

class Colors:
    """ANSI color codes for terminal output."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def run_test(script_name: str, test_name: str) -> Tuple[int, str]:
    """Run a validation test script."""
    print(f"\n{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}Running: {test_name}{Colors.END}")
    print(f"{Colors.BLUE}{'='*60}{Colors.END}\n")
    
    try:
        result = subprocess.run(
            [sys.executable, f"scripts/{script_name}"],
            capture_output=False,
            text=True
        )
        return result.returncode, f"Completed with code {result.returncode}"
    except Exception as e:
        return 1, f"Error: {str(e)}"

def interpret_result(code: int) -> str:
    """Interpret test result code."""
    if code == 0:
        return f"{Colors.GREEN}✅ PASS{Colors.END}"
    elif code == 2:
        return f"{Colors.YELLOW}⚠️  MANUAL{Colors.END}"
    else:
        return f"{Colors.RED}❌ FAIL{Colors.END}"

def main():
    """Run all VAN QA tests."""
    print(f"\n{Colors.BOLD}{'='*60}")
    print("PHASE 3 VAN QA MODE - COMPREHENSIVE VALIDATION")
    print(f"{'='*60}{Colors.END}\n")
    
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Define all tests
    tests = [
        ("test_pgvector.py", "VAN-QA-1: pgvector Extension Availability"),
        ("test_vector_performance.py", "VAN-QA-2: HNSW Index Performance"),
        ("test_rls_enforcement.py", "VAN-QA-3: RLS Policy Enforcement"),
        ("test_embeddings_api.py", "VAN-QA-4: Embedding API Integration"),
        ("test_supabase_rls_client.py", "VAN-QA-5: Supabase Python Client with RLS"),
    ]
    
    # Run all tests
    results = {}
    for script, name in tests:
        code, message = run_test(script, name)
        results[name] = {
            'code': code,
            'status': interpret_result(code),
            'message': message
        }
    
    # Generate summary report
    print(f"\n{Colors.BOLD}{'='*60}")
    print("VALIDATION SUMMARY REPORT")
    print(f"{'='*60}{Colors.END}\n")
    
    passed = sum(1 for r in results.values() if r['code'] == 0)
    manual = sum(1 for r in results.values() if r['code'] == 2)
    failed = sum(1 for r in results.values() if r['code'] not in [0, 2])
    total = len(results)
    
    print(f"Total Tests: {total}")
    print(f"Passed:      {passed} {Colors.GREEN}✅{Colors.END}")
    print(f"Manual:      {manual} {Colors.YELLOW}⚠️{Colors.END}")
    print(f"Failed:      {failed} {Colors.RED}❌{Colors.END}")
    
    print(f"\n{Colors.BOLD}Individual Test Results:{Colors.END}\n")
    for name, result in results.items():
        print(f"{result['status']} {name}")
    
    # Overall assessment
    print(f"\n{Colors.BOLD}{'='*60}")
    print("OVERALL ASSESSMENT")
    print(f"{'='*60}{Colors.END}\n")
    
    critical_tests = [
        "VAN-QA-1: pgvector Extension Availability",
        "VAN-QA-3: RLS Policy Enforcement",
        "VAN-QA-5: Supabase Python Client with RLS"
    ]
    
    critical_failed = any(
        results[t]['code'] == 1 for t in critical_tests if t in results
    )
    
    if failed > 0:
        print(f"{Colors.RED}❌ BLOCKED: {failed} test(s) failed{Colors.END}")
        print("   Phase 3 cannot proceed until failures are resolved")
        sys.exit(1)
    elif critical_failed:
        print(f"{Colors.RED}❌ BLOCKED: Critical test(s) failed{Colors.END}")
        print("   Security or infrastructure issues must be resolved")
        sys.exit(1)
    elif manual > 0:
        print(f"{Colors.YELLOW}⚠️  CONDITIONAL: {manual} test(s) require manual verification{Colors.END}")
        print("   Complete manual verification before proceeding to BUILD")
        print("\nNext Steps:")
        print("   1. Follow instructions in test output for manual verification")
        print("   2. Ensure all critical tests (pgvector, RLS) are validated")
        print("   3. Document verification results")
        print("   4. Proceed to BUILD Mode if all verifications pass")
        sys.exit(2)
    else:
        print(f"{Colors.GREEN}✅ PASS: All tests passed!{Colors.END}")
        print("   Phase 3 is ready for BUILD Mode")
        sys.exit(0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n\n{Colors.YELLOW}Test run interrupted by user{Colors.END}")
        sys.exit(130)
