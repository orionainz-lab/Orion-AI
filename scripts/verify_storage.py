import os
from supabase import create_client, Client

# Load environment variables from .env file
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("Loaded environment variables from .env file")
except ImportError:
    print("WARNING: python-dotenv not installed")

# Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
# You need a valid JWT token for an authenticated user to test upload
USER_TOKEN = os.getenv("TEST_USER_TOKEN") 
# You need a valid JWT token for an Org Admin to test delete
ADMIN_TOKEN = os.getenv("TEST_ADMIN_TOKEN")

BUCKET_NAME = 'brand-assets'

def get_client(token=None) -> Client:
    """Helper to get a Supabase client with specific auth context."""
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    return create_client(SUPABASE_URL, SUPABASE_ANON_KEY, options={"headers": headers})

def test_public_read():
    print(f"\n--- Testing Public Read Policy (SELECT) ---")
    try:
        # Use anon key (public access)
        #
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        files = client.storage.from_(BUCKET_NAME).list()
        print(f"[PASS] Success: Public read access works. Found {len(files)} files.")
    except Exception as e:
        print(f"[FAIL] Failed: Public read access denied or error occurred.\nError: {e}")

def test_auth_upload():
    print(f"\n--- Testing Authenticated Upload Policy (INSERT) ---")
    if not USER_TOKEN:
        print("[SKIP] Skipping: TEST_USER_TOKEN not found in environment.")
        return

    try:
        # Client pretending to be a logged-in user
        #
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        client.auth.set_session(access_token=USER_TOKEN, refresh_token="dummy")
        
        # specific file to test (use PNG which is allowed)
        file_name = "test-verification-file.png"
        # Create a minimal valid PNG (1x1 transparent pixel)
        file_body = bytes([
            0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A,  # PNG signature
            0x00, 0x00, 0x00, 0x0D, 0x49, 0x48, 0x44, 0x52,  # IHDR chunk
            0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,  # 1x1 dimensions
            0x08, 0x06, 0x00, 0x00, 0x00, 0x1F, 0x15, 0xC4,  # 8-bit RGBA
            0x89, 0x00, 0x00, 0x00, 0x0A, 0x49, 0x44, 0x41,  # IDAT chunk
            0x54, 0x78, 0x9C, 0x63, 0x00, 0x01, 0x00, 0x00,  # compressed data
            0x05, 0x00, 0x01, 0x0D, 0x0A, 0x2D, 0xB4, 0x00,  # ...
            0x00, 0x00, 0x00, 0x49, 0x45, 0x4E, 0x44, 0xAE,  # IEND chunk
            0x42, 0x60, 0x82
        ])
        
        client.storage.from_(BUCKET_NAME).upload(
            path=file_name,
            file=file_body,
            file_options={"content-type": "image/png", "upsert": "true"}
        )
        print(f"[PASS] Success: Authenticated upload works for '{file_name}'.")
    except Exception as e:
        print(f"[FAIL] Failed: Upload denied.\nError: {e}")

def test_admin_delete():
    print(f"\n--- Testing Admin Delete Policy (DELETE) ---")
    if not ADMIN_TOKEN:
        print("[SKIP] Skipping: TEST_ADMIN_TOKEN not found in environment.")
        return

    try:
        # Client pretending to be an Admin
        #
        client = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        client.auth.set_session(access_token=ADMIN_TOKEN, refresh_token="dummy")
        
        file_name = "test-verification-file.png"
        
        client.storage.from_(BUCKET_NAME).remove([file_name])
        print(f"[PASS] Success: Admin delete works for '{file_name}'.")
    except Exception as e:
        print(f"[FAIL] Failed: Delete denied.\nError: {e}")

if __name__ == "__main__":
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        print("Error: Please set SUPABASE_URL and SUPABASE_ANON_KEY environment variables.")
    else:
        test_public_read()
        test_auth_upload()
        test_admin_delete()
