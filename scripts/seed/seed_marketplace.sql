-- Phase 6B Marketplace Seed Data
-- Created: 2026-01-31
-- Purpose: Populate marketplace with sample connectors

-- First, ensure we have a publisher user (use existing or create dummy)
-- In production, this would be the actual Orion AI system user

-- Seed marketplace connectors
-- Note: connector_id references should match actual connector IDs from Phase 5
-- For now, we'll create dummy UUIDs or reference existing connectors

INSERT INTO connector_marketplace (
  connector_id, 
  publisher_id, 
  name, 
  description, 
  category, 
  pricing_model, 
  install_count, 
  rating, 
  is_verified,
  icon_url,
  documentation_url
) VALUES
  -- Salesforce
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users ORDER BY created_at LIMIT 1),
    'Salesforce',
    'Connect to Salesforce CRM for customer data synchronization. Supports Accounts, Contacts, Leads, and Opportunities with Bulk API 2.0 for large-scale operations.',
    'crm',
    'free',
    12543,
    4.8,
    true,
    'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/salesforce.svg',
    'https://developer.salesforce.com/docs'
  ),
  -- HubSpot
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users ORDER BY created_at LIMIT 1),
    'HubSpot',
    'Integrate with HubSpot CRM to sync contacts, companies, and deals. Real-time webhook support included for instant updates.',
    'crm',
    'free',
    9876,
    4.7,
    true,
    'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/hubspot.svg',
    'https://developers.hubspot.com/docs/api/overview'
  ),
  -- Stripe
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users ORDER BY created_at LIMIT 1),
    'Stripe',
    'Payment processing integration with Stripe. Sync customers, invoices, and payment events automatically. Webhook support for real-time event processing.',
    'accounting',
    'free',
    15678,
    4.9,
    true,
    'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/stripe.svg',
    'https://stripe.com/docs/api'
  ),
  -- QuickBooks
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users ORDER BY created_at LIMIT 1),
    'QuickBooks',
    'QuickBooks Online integration for accounting data. Sync customers, invoices, and payments with OAuth 2.0 authentication and automatic token refresh.',
    'accounting',
    'free',
    8432,
    4.6,
    true,
    'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/quickbooks.svg',
    'https://developer.intuit.com/app/developer/qbo/docs/api'
  ),
  -- Slack
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users ORDER BY created_at LIMIT 1),
    'Slack',
    'Send notifications and alerts to Slack channels. Support for interactive components, Block Kit formatting, and file uploads. Perfect for workflow notifications.',
    'communication',
    'free',
    11234,
    4.8,
    true,
    'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/slack.svg',
    'https://api.slack.com'
  ),
  -- Shopify (Community)
  (
    uuid_generate_v4(),
    (SELECT id FROM auth.users ORDER BY created_at LIMIT 1),
    'Shopify',
    'E-commerce integration with Shopify. Sync products, orders, and customers in real-time. Community-maintained connector with webhook support.',
    'custom',
    'freemium',
    6789,
    4.5,
    false,
    'https://cdn.jsdelivr.net/npm/simple-icons@v9/icons/shopify.svg',
    'https://shopify.dev/docs/api'
  )
ON CONFLICT DO NOTHING;

-- Verify insertion
SELECT name, category, install_count, rating, is_verified 
FROM connector_marketplace 
ORDER BY install_count DESC;
