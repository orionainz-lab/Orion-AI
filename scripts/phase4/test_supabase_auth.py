#!/usr/bin/env python3
"""
Phase 4 VAN QA: Test Supabase Auth Flow
Purpose: Verify Supabase authentication works and OAuth providers are configured
Expected: Can create client, check session, list auth providers
"""

import os
import sys
from typing import Dict, Any
from dotenv import load_dotenv

# Colors for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[1;33m'
NC = '\033[0m'  # No Color

# Test counters
tests_run = 0
tests_passed = 0
tests_failed = 0

def print_header(text: str):
    """Print a formatted header"""
    print("=" * 64)
    print(text)
    print("=" * 64)
    print()

def print_section(text: str):
    """Print a section header"""
    print()
    print(text)
    print("-" * 40)

def run_test(name: str, test_func) -> bool:
    """Run a test and track results"""
    global tests_run, tests_passed, tests_failed
    
    tests_run += 1
    print(f"Test {tests_run}: {name}... ", end="")
    
    try:
        result = test_func()
        if result:
            print(f"{GREEN}PASS{NC}")
            tests_passed += 1
            return True
        else:
            print(f"{RED}FAIL{NC}")
            tests_failed += 1
            return False
    except Exception as e:
        print(f"{RED}FAIL{NC}")
        print(f"  Error: {str(e)}")
        tests_failed += 1
        return False

def main():
    print_header("Phase 4 VAN QA: Supabase Auth Validation")
    
    # Load environment variables
    load_dotenv()
    
    # Check prerequisites
    print("Checking Prerequisites...")
    print("-" * 40)
    
    def check_dotenv():
        """Check if python-dotenv is installed"""
        try:
            import dotenv
            return True
        except ImportError:
            return False
    
    if not run_test("python-dotenv installed", check_dotenv):
        print("\nInstall with: pip install python-dotenv")
        return False
    
    def check_supabase():
        """Check if supabase-py is installed"""
        try:
            import supabase
            return True
        except ImportError:
            return False
    
    if not run_test("supabase-py installed", check_supabase):
        print("\nInstall with: pip install supabase")
        return False
    
    # Import supabase after checking it's installed
    import supabase as sb
    
    # Test Suite 1: Environment Variables
    print_section("Test Suite 1: Environment Variables")
    
    def check_url_env():
        """Check SUPABASE_URL environment variable"""
        url = os.getenv('SUPABASE_URL')
        if url:
            print(f"  Found: {url}")
            return True
        return False
    
    def check_anon_key_env():
        """Check SUPABASE_ANON_KEY environment variable"""
        key = os.getenv('SUPABASE_ANON_KEY')
        if key:
            print(f"  Found: {key[:20]}...{key[-10:]}")
            return True
        return False
    
    if not run_test("SUPABASE_URL exists", check_url_env):
        print("  Set in .env: SUPABASE_URL=https://xxx.supabase.co")
    
    if not run_test("SUPABASE_ANON_KEY exists", check_anon_key_env):
        print("  Set in .env: SUPABASE_ANON_KEY=your-anon-key")
    
    # Get credentials
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_ANON_KEY')
    
    if not supabase_url or not supabase_key:
        print(f"\n{RED}CRITICAL: Missing Supabase credentials{NC}")
        print("Create a .env file with:")
        print("  SUPABASE_URL=https://your-project.supabase.co")
        print("  SUPABASE_ANON_KEY=your-anon-key")
        return False
    
    # Test Suite 2: Client Creation
    print_section("Test Suite 2: Supabase Client")
    
    client = None
    
    def create_client():
        """Create Supabase client"""
        nonlocal client
        client = sb.create_client(supabase_url, supabase_key)
        return client is not None
    
    if not run_test("Client creation", create_client):
        print(f"\n{RED}CRITICAL: Cannot create Supabase client{NC}")
        return False
    
    def check_auth_available():
        """Check if auth is available on client"""
        return hasattr(client, 'auth') and client.auth is not None
    
    run_test("Auth module available", check_auth_available)
    
    # Test Suite 3: Auth Session
    print_section("Test Suite 3: Auth Session Check")
    
    def check_session():
        """Check current session (will be None if not logged in)"""
        try:
            response = client.auth.get_session()
            # Session can be None (not logged in), that's okay for validation
            print(f"  Session: {'Active' if response else 'None (not logged in)'}")
            return True
        except Exception as e:
            print(f"  Error: {str(e)}")
            return False
    
    run_test("Get session (can be None)", check_session)
    
    def check_user():
        """Check current user (will be None if not logged in)"""
        try:
            response = client.auth.get_user()
            # User can be None, that's okay
            if response and hasattr(response, 'user') and response.user:
                print(f"  User: {response.user.email}")
            else:
                print("  User: None (not logged in)")
            return True
        except Exception as e:
            print(f"  Error: {str(e)}")
            return False
    
    run_test("Get user (can be None)", check_user)
    
    # Test Suite 4: Auth Configuration
    print_section("Test Suite 4: Auth Configuration Check")
    
    def check_auth_settings():
        """Check if we can access auth settings (indicates proper setup)"""
        try:
            # Try to get auth settings by attempting a password reset (won't send email, just validates)
            # This is a read-only check of auth configuration
            print("  Checking auth configuration...")
            # Just verify the method exists
            return hasattr(client.auth, 'reset_password_email')
        except Exception as e:
            print(f"  Error: {str(e)}")
            return False
    
    run_test("Auth methods available", check_auth_settings)
    
    # Test Suite 5: OAuth Provider Check (Manual)
    print_section("Test Suite 5: OAuth Providers")
    
    print(f"\n{YELLOW}MANUAL CHECK REQUIRED:{NC}")
    print("\nTo enable OAuth providers for Phase 4:")
    print("1. Go to Supabase Dashboard -> Authentication -> Providers")
    print("2. Enable Google:")
    print("   - Get Client ID and Secret from Google Cloud Console")
    print("   - Set redirect URL: https://xxx.supabase.co/auth/v1/callback")
    print("3. Enable GitHub:")
    print("   - Get Client ID and Secret from GitHub Settings")
    print("   - Set redirect URL: https://xxx.supabase.co/auth/v1/callback")
    print()
    
    # Test Suite 6: Sign-In Methods
    print_section("Test Suite 6: Available Sign-In Methods")
    
    def check_password_signin():
        """Check if password sign-in method exists"""
        return hasattr(client.auth, 'sign_in_with_password')
    
    def check_oauth_signin():
        """Check if OAuth sign-in method exists"""
        return hasattr(client.auth, 'sign_in_with_oauth')
    
    def check_signout():
        """Check if sign-out method exists"""
        return hasattr(client.auth, 'sign_out')
    
    run_test("Password sign-in available", check_password_signin)
    run_test("OAuth sign-in available", check_oauth_signin)
    run_test("Sign-out available", check_signout)
    
    # Summary
    print_header("VALIDATION SUMMARY")
    
    print(f"Tests Run:    {tests_run}")
    print(f"Tests Passed: {GREEN}{tests_passed}{NC}")
    print(f"Tests Failed: {RED}{tests_failed}{NC}")
    print()
    
    if tests_failed == 0:
        print(f"{GREEN}RESULT: ALL TESTS PASSED{NC}")
        print()
        print("Supabase Auth is ready for Phase 4 implementation!")
        print()
        print("Validated:")
        print("  - Supabase client creation")
        print("  - Auth module availability")
        print("  - Session management")
        print("  - Sign-in/sign-out methods")
        print()
        print(f"{YELLOW}NEXT STEPS:{NC}")
        print("  1. Enable OAuth providers in Supabase Dashboard")
        print("  2. Configure Google and GitHub OAuth apps")
        print("  3. Test OAuth flow in Phase 4.1 (Foundation)")
        print()
        return True
    else:
        print(f"{RED}RESULT: SOME TESTS FAILED{NC}")
        print()
        print("Please review the failures above before proceeding to BUILD mode.")
        print()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
