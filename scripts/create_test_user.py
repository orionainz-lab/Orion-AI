#!/usr/bin/env python3
"""
Create Test User and Get JWT Token
===================================
Creates a test user in Supabase and retrieves their JWT token.

Usage:
    python scripts/create_test_user.py
"""

import os
from dotenv import load_dotenv
load_dotenv()

from supabase import create_client

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

def create_test_user(email: str, password: str, role: str = "user"):
    """Create a test user and return their JWT token."""
    
    # Use service role to create user (bypasses email confirmation)
    admin_client = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    
    print(f"\n--- Creating {role} user: {email} ---")
    
    try:
        # Create user using admin API
        user = admin_client.auth.admin.create_user({
            "email": email,
            "password": password,
            "email_confirm": True,  # Auto-confirm email
            "user_metadata": {"role": role}
        })
        
        print(f"[PASS] User created: {user.user.id}")
        
        # Now sign in to get the JWT token
        anon_client = create_client(SUPABASE_URL, os.getenv("SUPABASE_ANON_KEY"))
        auth_response = anon_client.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        
        access_token = auth_response.session.access_token
        print(f"[PASS] JWT Token obtained (first 50 chars): {access_token[:50]}...")
        
        return {
            "user_id": user.user.id,
            "email": email,
            "access_token": access_token
        }
        
    except Exception as e:
        error_msg = str(e)
        if "already been registered" in error_msg or "already exists" in error_msg:
            print(f"[INFO] User already exists, signing in...")
            
            # Sign in existing user
            anon_client = create_client(SUPABASE_URL, os.getenv("SUPABASE_ANON_KEY"))
            auth_response = anon_client.auth.sign_in_with_password({
                "email": email,
                "password": password
            })
            
            access_token = auth_response.session.access_token
            user_id = auth_response.user.id
            print(f"[PASS] Signed in, JWT Token obtained")
            
            return {
                "user_id": user_id,
                "email": email,
                "access_token": access_token
            }
        else:
            print(f"[FAIL] Error: {error_msg}")
            return None


def main():
    print("=" * 60)
    print("  CREATE TEST USERS FOR STORAGE RLS VERIFICATION")
    print("=" * 60)
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        print("[FAIL] Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
        return
    
    # Create regular test user
    test_user = create_test_user(
        email="testuser@orion-ai.test",
        password="TestUser123!",
        role="user"
    )
    
    # Create admin test user
    admin_user = create_test_user(
        email="testadmin@orion-ai.test",
        password="TestAdmin123!",
        role="admin"
    )
    
    print("\n" + "=" * 60)
    print("  TOKENS FOR .env FILE")
    print("=" * 60)
    
    if test_user:
        print(f"\n# Test User Token")
        print(f"TEST_USER_TOKEN={test_user['access_token']}")
    
    if admin_user:
        print(f"\n# Test Admin Token")
        print(f"TEST_ADMIN_TOKEN={admin_user['access_token']}")
    
    print("\n" + "=" * 60)
    print("  NEXT STEPS")
    print("=" * 60)
    print("""
1. Copy the tokens above to your .env file
2. Run: python scripts/verify_storage.py
3. All 3 tests should now run

NOTE: JWT tokens expire after 1 hour by default.
      Re-run this script to get fresh tokens if needed.
""")


if __name__ == "__main__":
    main()
