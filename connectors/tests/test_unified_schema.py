"""
Unit Tests for Unified Schema Models

Tests for UnifiedCustomer, UnifiedInvoice, UnifiedEvent.
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from connectors.unified_schema import (
    UnifiedBase,
    UnifiedCustomer,
    UnifiedAddress,
    UnifiedInvoice,
    UnifiedLineItem,
    UnifiedEvent
)


class TestUnifiedBase:
    """Tests for UnifiedBase model"""
    
    def test_unified_base_required_fields(self):
        """Test that required fields are enforced"""
        with pytest.raises(Exception):
            UnifiedBase()
    
    def test_unified_base_creation(self):
        """Test creating a valid UnifiedBase instance"""
        model = UnifiedBase(
            source_system="test",
            source_id="123"
        )
        assert model.source_system == "test"
        assert model.source_id == "123"
        assert model.synced_at is not None


class TestUnifiedCustomer:
    """Tests for UnifiedCustomer model"""
    
    def test_customer_creation(self):
        """Test creating a customer"""
        customer = UnifiedCustomer(
            source_system="stripe",
            source_id="cus_123",
            email="john@example.com",
            name="John Doe"
        )
        
        assert customer.email == "john@example.com"
        assert customer.name == "John Doe"
        assert customer.is_active is True
    
    def test_customer_with_address(self):
        """Test customer with billing address"""
        customer = UnifiedCustomer(
            source_system="stripe",
            source_id="cus_123",
            email="jane@example.com",
            name="Jane Smith",
            billing_address=UnifiedAddress(
                source_system="stripe",
                source_id="addr_123",
                street="123 Main St",
                city="Boston",
                postal_code="02101",
                country="US"
            )
        )
        
        assert customer.billing_address is not None
        assert customer.billing_address.city == "Boston"
        assert customer.has_complete_billing_address() is True
    
    def test_customer_display_name(self):
        """Test display name formatting"""
        customer = UnifiedCustomer(
            source_system="test",
            source_id="123",
            email="test@example.com",
            name="Test User",
            company="ACME Corp"
        )
        
        assert customer.get_display_name() == "Test User (ACME Corp)"
    
    def test_customer_email_validation(self):
        """Test email validation"""
        with pytest.raises(Exception):
            UnifiedCustomer(
                source_system="test",
                source_id="123",
                email="invalid-email",
                name="Test"
            )


class TestUnifiedInvoice:
    """Tests for UnifiedInvoice model"""
    
    def test_invoice_creation(self):
        """Test creating an invoice"""
        invoice = UnifiedInvoice(
            source_system="stripe",
            source_id="inv_123",
            customer_id="cus_123",
            invoice_number="INV-001",
            status="pending",
            subtotal=Decimal("100.00"),
            tax=Decimal("10.00"),
            total=Decimal("110.00"),
            issue_date=date.today()
        )
        
        assert invoice.invoice_number == "INV-001"
        assert invoice.total == Decimal("110.00")
    
    def test_invoice_with_line_items(self):
        """Test invoice with line items"""
        invoice = UnifiedInvoice(
            source_system="stripe",
            source_id="inv_123",
            customer_id="cus_123",
            invoice_number="INV-002",
            status="paid",
            subtotal=Decimal("0"),
            total=Decimal("0"),
            issue_date=date.today(),
            line_items=[
                UnifiedLineItem(
                    source_system="stripe",
                    source_id="li_1",
                    description="Product A",
                    quantity=2,
                    unit_price=Decimal("50.00"),
                    total=Decimal("100.00")
                )
            ]
        )
        
        assert len(invoice.line_items) == 1
        invoice.calculate_totals()
        assert invoice.subtotal == Decimal("100.00")
    
    def test_invoice_overdue_check(self):
        """Test overdue detection"""
        from datetime import timedelta
        
        overdue_invoice = UnifiedInvoice(
            source_system="test",
            source_id="123",
            customer_id="cus_123",
            invoice_number="INV-003",
            status="pending",
            subtotal=Decimal("100"),
            total=Decimal("100"),
            issue_date=date.today() - timedelta(days=60),
            due_date=date.today() - timedelta(days=30)
        )
        
        assert overdue_invoice.is_overdue() is True


class TestUnifiedEvent:
    """Tests for UnifiedEvent model"""
    
    def test_event_creation(self):
        """Test creating an event"""
        event = UnifiedEvent(
            source_system="stripe",
            source_id="evt_123",
            event_type="customer.created",
            payload={"customer_id": "cus_123"}
        )
        
        assert event.event_type == "customer.created"
        assert event.processed is False
    
    def test_event_processing(self):
        """Test marking event as processed"""
        event = UnifiedEvent(
            source_system="test",
            source_id="evt_123",
            event_type="test.event"
        )
        
        assert event.processed is False
        event.mark_processed()
        assert event.processed is True
        assert event.processed_at is not None
    
    def test_event_type_detection(self):
        """Test event type helpers"""
        customer_event = UnifiedEvent(
            source_system="test",
            source_id="evt_1",
            event_type="customer.created",
            resource_type="customer"
        )
        
        assert customer_event.is_customer_event() is True
        assert customer_event.is_invoice_event() is False


class TestUnifiedAddress:
    """Tests for UnifiedAddress model"""
    
    def test_address_formatting(self):
        """Test single-line address formatting"""
        address = UnifiedAddress(
            source_system="test",
            source_id="addr_1",
            street="123 Main St",
            city="Boston",
            state="MA",
            postal_code="02101",
            country="US"
        )
        
        formatted = address.format_single_line()
        assert "123 Main St" in formatted
        assert "Boston" in formatted
        assert "02101" in formatted
