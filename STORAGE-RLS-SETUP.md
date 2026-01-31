# Storage RLS Policies Setup Guide

## Overview
Storage RLS policies for the `brand-assets` bucket need to be created manually in the Supabase Dashboard or via the Management API.

## Required Policies

### 1. Public Read Access
**Policy Name**: `Public read access for brand-assets`
**Operation**: SELECT
**Target roles**: `public`

**Policy Definition**:
```sql
bucket_id = 'brand-assets'
```

**Description**: Allows anyone to read files from the brand-assets bucket (for serving logos, CSS, etc.)

---

### 2. Authenticated Upload
**Policy Name**: `Authenticated users can upload to brand-assets`
**Operation**: INSERT
**Target roles**: `authenticated`

**Policy Definition**:
```sql
bucket_id = 'brand-assets' 
AND auth.uid() IS NOT NULL
```

**Description**: Allows authenticated users to upload files to their organization's folder in the bucket.

---

### 3. Organization Admin Delete
**Policy Name**: `Org admins can delete brand-assets`
**Operation**: DELETE
**Target roles**: `authenticated`

**Policy Definition**:
```sql
bucket_id = 'brand-assets' 
AND auth.uid() IS NOT NULL
AND EXISTS (
  SELECT 1 FROM org_members om
  JOIN roles r ON om.role_id = r.id
  WHERE om.user_id = auth.uid()
  AND r.name IN ('Org Admin', 'Super Admin')
)
```

**Description**: Allows organization admins to delete files from the bucket.

---

## Setup Instructions

### Option 1: Supabase Dashboard (Recommended)

1. Go to **Supabase Dashboard** → **Storage** → **brand-assets**
2. Click on the **Policies** tab
3. Click **New Policy**
4. For each policy above:
   - Enter the **Policy Name**
   - Select the **Operation** (SELECT, INSERT, or DELETE)
   - Select **Target roles**
   - Enter the **Policy Definition** in the SQL editor
   - Click **Review** then **Save**

### Option 2: Management API (Advanced)

```bash
# Set your Supabase project ref and service role key
PROJECT_REF="bdvebjnxpsdhinpgvkgo"
SERVICE_ROLE_KEY="your-service-role-key"

# Create policies using Supabase Management API
curl -X POST "https://api.supabase.com/v1/projects/${PROJECT_REF}/storage/policies" \
  -H "Authorization: Bearer ${SERVICE_ROLE_KEY}" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Public read access for brand-assets",
    "definition": "bucket_id = '\''brand-assets'\''",
    "bucket_id": "brand-assets",
    "operation": "SELECT",
    "target_role": "public"
  }'
```

---

## Verification

After creating the policies, verify they work:

```python
from supabase import create_client
import os

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_ANON_KEY")  # Use anon key to test public access
)

# Test public read access
try:
    files = supabase.storage.from_('brand-assets').list()
    print(f"✓ Public read access works: {len(files)} files visible")
except Exception as e:
    print(f"✗ Public read access failed: {e}")

# Test authenticated upload (requires auth token)
# ... upload test code ...
```

---

## Policy Status

- ⏳ **Public Read**: Needs manual setup
- ⏳ **Authenticated Upload**: Needs manual setup  
- ⏳ **Admin Delete**: Needs manual setup

**Note**: These policies cannot be created via SQL due to Supabase security restrictions. They must be created through the Dashboard or Management API.

---

## Alternative: Use Service Role Key

If you don't want to set up RLS policies immediately, you can:

1. Use the **SERVICE_ROLE_KEY** for all storage operations (bypasses RLS)
2. Implement access control in your application code
3. Add RLS policies later when ready for production

**Warning**: Using SERVICE_ROLE_KEY bypasses all RLS rules. Only use in backend services, never expose to frontend.

---

## Next Steps

1. ✓ Storage bucket created: `brand-assets`
2. ⏳ Add RLS policies (manual step via Dashboard)
3. ✓ Environment variables configured
4. ✓ Backend services ready to use storage

Once policies are added, the white-label branding system will be fully functional!
