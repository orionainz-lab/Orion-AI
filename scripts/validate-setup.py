#!/usr/bin/env python3
"""Phase 0 Setup Validation Script"""

import os
import sys
from pathlib import Path
from typing import List, Tuple

# Constants
REQUIRED_DIRS = [
    'memory-bank', 'memory-bank/creative', 'memory-bank/reflection',
    'memory-bank/archive', 'build_plan', 'scripts', '.cursor/rules',
    'services', 'utils', 'temporal', 'connectors', 'frontend', 'docker'
]

REQUIRED_RULES = [
    'distributed-systems.md', 'ai-orchestration.md', 'verification.md',
    'frontend.md', 'realtime-systems.md', 'ml-engineer.md',
    'security.md', 'backend-api.md', 'sdet.md'
]

MEMORY_BANK_FILES = [
    'tasks.md', 'activeContext.md', 'systemPatterns.md',
    'progress.md', 'projectbrief.md', 'productContext.md',
    'techContext.md', 'style-guide.md'
]

SCRIPTS = [
    'setup-directories.sh', 'generate-rules.py',
    'validate-setup.py', 'run-all.sh'
]

def check_directory_structure() -> List[Tuple[bool, str, str]]:
    """Validate directory structure"""
    results = []
    for dir_name in REQUIRED_DIRS:
        path = Path(dir_name)
        exists = path.exists() and path.is_dir()
        results.append((
            exists,
            f"{dir_name}/ exists",
            f"Create: mkdir -p {dir_name}" if not exists else ""
        ))
    return results

def check_rule_files() -> List[Tuple[bool, str, str]]:
    """Validate rule files"""
    results = []
    for rule_file in REQUIRED_RULES:
        path = Path(f".cursor/rules/{rule_file}")
        exists = path.exists()
        
        if exists:
            lines = len(path.read_text(encoding='utf-8').splitlines())
            message = f"{rule_file} ({lines} lines)"
            if lines > 300:
                message += " - WARNING: Exceeds 300 lines"
        else:
            message = f"{rule_file} (MISSING)"
        
        fix = f"Run: python scripts/generate-rules.py" if not exists else ""
        results.append((exists, message, fix))
    return results

def check_memory_bank() -> List[Tuple[bool, str, str]]:
    """Validate Memory Bank files"""
    results = []
    for file_name in MEMORY_BANK_FILES:
        path = Path(f"memory-bank/{file_name}")
        exists = path.exists()
        has_content = exists and path.stat().st_size > 0
        
        status = exists and has_content
        message = f"{file_name} exists and has content" if status else \
                  f"{file_name} (MISSING or EMPTY)"
        fix = f"Check: memory-bank/{file_name}" if not status else ""
        results.append((status, message, fix))
    return results

def check_scripts() -> List[Tuple[bool, str, str]]:
    """Validate setup scripts"""
    results = []
    for script in SCRIPTS:
        path = Path(f"scripts/{script}")
        exists = path.exists()
        message = f"{script} exists" if exists else f"{script} (MISSING)"
        fix = f"Missing script: scripts/{script}" if not exists else ""
        results.append((exists, message, fix))
    return results

def print_results(category: str, results: List[Tuple[bool, str, str]]):
    """Print validation results for a category"""
    print(f"\n{category}")
    for passed, message, fix in results:
        symbol = "Pass" if passed else "FAIL"
        print(f"  [{symbol}] {message}")
        if fix:
            print(f"         Fix: {fix}")

def main():
    print("\n" + "=" * 70)
    print("  PHASE 0 VALIDATION REPORT")
    print("=" * 70)
    
    # Run all checks
    dir_results = check_directory_structure()
    rule_results = check_rule_files()
    mb_results = check_memory_bank()
    script_results = check_scripts()
    
    # Print results
    print_results("DIRECTORY STRUCTURE", dir_results)
    print_results("RULE FILES", rule_results)
    print_results("MEMORY BANK", mb_results)
    print_results("SCRIPTS", script_results)
    
    # Summary
    all_results = dir_results + rule_results + mb_results + script_results
    total = len(all_results)
    passed = sum(1 for r in all_results if r[0])
    failed = total - passed
    
    print("\n" + "=" * 70)
    print("\nVALIDATION SUMMARY")
    print(f"  Total Checks: {total}")
    print(f"  Passed: {passed}")
    print(f"  Failed: {failed}")
    
    if failed > 0:
        print(f"\nSTATUS: VALIDATION FAILED")
        print("\nREQUIRED FIXES:")
        for i, (passed, _, fix) in enumerate(all_results, 1):
            if not passed and fix:
                print(f"  {i}. {fix}")
        print("\nRun validation again after fixes: python scripts/validate-setup.py")
        print("")
        sys.exit(1)
    else:
        print(f"\nSTATUS: ALL CHECKS PASSED")
        print("\nPhase 0 setup is complete and validated!")
        print("")
        sys.exit(0)

if __name__ == "__main__":
    main()
