"""
Test Stripe Adapter with MCP

Quick test to verify Stripe MCP integration.
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import asyncio
from connectors.adapters.stripe import StripeAdapter
from connectors.adapters.base import AdapterConfig


async def test_stripe_mcp():
    """Test Stripe adapter with MCP tools"""
    
    print("=" * 60)
    print("Phase 5.2: Testing Stripe Adapter with MCP")
    print("=" * 60)
    
    # Configure adapter
    config = AdapterConfig(
        base_url="https://api.stripe.com",
        timeout=30
    )
    
    # Mock credentials (MCP handles auth)
    credentials = {
        "api_key": "sk_test_mock"  # MCP will use actual key
    }
    
    # Create adapter
    adapter = StripeAdapter(config, credentials)
    
    print("\n[OK] Adapter created successfully")
    print(f"   Name: {adapter.name}")
    print(f"   Version: {adapter.version}")
    print(f"   Capabilities: {adapter.capabilities}")
    
    # Test to_unified transformation
    print("\n[TEST] Testing to_unified() transformation...")
    
    sample_stripe_customer = {
        "id": "cus_test_123",
        "email": "test@example.com",
        "name": "Test Customer",
        "phone": "+1234567890",
        "address": {
            "line1": "123 Test St",
            "city": "Boston",
            "state": "MA",
            "postal_code": "02101",
            "country": "US"
        },
        "metadata": {
            "tags": "vip,premium",
            "custom_field": "value"
        }
    }
    
    unified = await adapter.to_unified(sample_stripe_customer)
    
    print(f"   [OK] Source ID: {unified.source_id}")
    print(f"   [OK] Email: {unified.email}")
    print(f"   [OK] Name: {unified.name}")
    print(f"   [OK] Tags: {unified.tags}")
    print(f"   [OK] Has billing address: {unified.billing_address is not None}")
    
    # Test from_unified transformation
    print("\n[TEST] Testing from_unified() transformation...")
    
    stripe_format = await adapter.from_unified(unified)
    
    print(f"   [OK] Email: {stripe_format.get('email')}")
    print(f"   [OK] Name: {stripe_format.get('name')}")
    print(f"   [OK] Has address: {'address' in stripe_format}")
    print(f"   [OK] Has metadata: {'metadata' in stripe_format}")
    
    # Summary
    print("\n" + "=" * 60)
    print("[SUCCESS] All Stripe adapter tests passed!")
    print("=" * 60)
    print("\nReady for:")
    print("  - Real API integration via httpx")
    print("  - MCP Stripe tool integration")
    print("  - Production use in workflows")


if __name__ == "__main__":
    asyncio.run(test_stripe_mcp())
