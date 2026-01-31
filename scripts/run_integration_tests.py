#!/usr/bin/env python3
"""
Integration Test Runner - Phase 7 Option B

Runs all integration tests for SSO, RBAC, and Rate Limiting.
Generates comprehensive test report.
"""

import subprocess
import sys
import os
from datetime import datetime
from pathlib import Path


def print_header(title: str):
    """Print section header."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)


def run_pytest(test_path: str, description: str) -> tuple[bool, str]:
    """Run pytest and capture results."""
    print(f"\n[TEST] Running: {description}")
    print(f"   Path: {test_path}")
    
    try:
        result = subprocess.run(
            ["pytest", test_path, "-v", "--tb=short"],
            capture_output=True,
            text=True,
            timeout=300
        )
        
        success = result.returncode == 0
        output = result.stdout + result.stderr
        
        if success:
            print("   [PASS] PASSED")
        else:
            print("   [FAIL] FAILED")
            print(f"\n{output}")
        
        return success, output
    
    except subprocess.TimeoutExpired:
        print("   [TIMEOUT] Test timeout after 5 minutes")
        return False, "Test timeout after 5 minutes"
    except Exception as e:
        print(f"   [ERROR] {e}")
        return False, str(e)


def generate_report(results: list[dict], output_file: str):
    """Generate HTML test report."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed
    
    html = f"""<!DOCTYPE html>
<html>
<head>
    <title>Integration Test Report - Phase 7</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            margin: 40px;
            background: #f5f5f5;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 30px;
            border-radius: 10px;
            margin-bottom: 30px;
        }}
        .stats {{
            display: grid;
            grid-template-columns: repeat(3, 1fr);
            gap: 20px;
            margin-bottom: 30px;
        }}
        .stat-card {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .stat-value {{
            font-size: 36px;
            font-weight: bold;
            margin: 10px 0;
        }}
        .stat-label {{
            color: #666;
            font-size: 14px;
        }}
        .test-result {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            margin-bottom: 15px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }}
        .test-passed {{ border-left: 4px solid #10b981; }}
        .test-failed {{ border-left: 4px solid #ef4444; }}
        .test-name {{
            font-weight: 600;
            margin-bottom: 5px;
        }}
        .test-path {{
            color: #666;
            font-size: 12px;
            font-family: monospace;
        }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Integration Test Report</h1>
        <p>Phase 7 Option B: SSO, RBAC & Rate Limiting</p>
        <p>Generated: {timestamp}</p>
    </div>
    
    <div class="stats">
        <div class="stat-card">
            <div class="stat-label">Total Tests</div>
            <div class="stat-value">{total}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Passed</div>
            <div class="stat-value" style="color: #10b981;">{passed}</div>
        </div>
        <div class="stat-card">
            <div class="stat-label">Failed</div>
            <div class="stat-value" style="color: #ef4444;">{failed}</div>
        </div>
    </div>
    
    <h2>Test Results</h2>
"""
    
    for result in results:
        status_class = "test-passed" if result["success"] else "test-failed"
        status_icon = "✅" if result["success"] else "❌"
        
        html += f"""
    <div class="test-result {status_class}">
        <div class="test-name">{status_icon} {result['description']}</div>
        <div class="test-path">{result['path']}</div>
    </div>
"""
    
    html += """
</body>
</html>
"""
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(html)
    
    print(f"\n[REPORT] Report saved to: {output_file}")


def main():
    """Run all integration tests."""
    print_header("INTEGRATION TEST SUITE - PHASE 7 OPTION B")
    
    # Check environment
    if not os.getenv("SUPABASE_URL"):
        print("\n[WARNING] Loading environment variables from .env")
        from dotenv import load_dotenv
        load_dotenv()
    
    results = []
    
    # 1. SSO Tests
    print_header("1. SSO INTEGRATION TESTS")
    
    sso_tests = [
        ("tests/integration/sso/test_azure_ad.py", "Azure AD SSO Flow"),
    ]
    
    for test_path, description in sso_tests:
        if os.path.exists(test_path):
            success, output = run_pytest(test_path, description)
            results.append({
                "path": test_path,
                "description": description,
                "success": success,
                "output": output
            })
        else:
            print(f"   ⚠️  Skipped: {test_path} not found")
    
    # 2. RBAC Tests
    print_header("2. RBAC INTEGRATION TESTS")
    
    rbac_tests = [
        ("tests/integration/rbac/test_viewer_permissions.py", "RBAC Permission Tests"),
    ]
    
    for test_path, description in rbac_tests:
        if os.path.exists(test_path):
            success, output = run_pytest(test_path, description)
            results.append({
                "path": test_path,
                "description": description,
                "success": success,
                "output": output
            })
        else:
            print(f"   ⚠️  Skipped: {test_path} not found")
    
    # 3. Rate Limiting (Note: load tests run separately)
    print_header("3. RATE LIMITING")
    print("\n[INFO] Load tests available via:")
    print("   bash scripts/load_tests/run_load_test.sh")
    
    # Generate report
    print_header("GENERATING REPORT")
    
    os.makedirs("test-results", exist_ok=True)
    report_file = "test-results/integration-test-report.html"
    generate_report(results, report_file)
    
    # Summary
    print_header("SUMMARY")
    
    total = len(results)
    passed = sum(1 for r in results if r["success"])
    failed = total - passed
    
    print(f"\nTotal Tests: {total}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/total*100) if total > 0 else 0:.1f}%")
    
    if failed > 0:
        print("\n[FAIL] Some tests failed. See report for details.")
        sys.exit(1)
    else:
        print("\n[PASS] All tests passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
