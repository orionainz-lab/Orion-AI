"""
Unified Invoice Model

Canonical invoice representation across systems.
Maps to: Stripe Invoice, QuickBooks Invoice, Xero Invoice, etc.
"""

from pydantic import Field
from typing import Optional, List
from decimal import Decimal
from datetime import date
from .base import UnifiedBase


class UnifiedLineItem(UnifiedBase):
    """
    Invoice line item.
    
    Represents a single item/service on an invoice.
    """
    
    description: str = Field(..., description="Item description")
    quantity: int = Field(1, ge=1, description="Quantity")
    unit_price: Decimal = Field(..., description="Price per unit")
    total: Decimal = Field(..., description="Line total")
    
    # Optional
    sku: Optional[str] = Field(None, description="SKU/Product code")
    tax_rate: Optional[Decimal] = Field(
        None,
        description="Tax rate (percentage)"
    )


class UnifiedInvoice(UnifiedBase):
    """
    Canonical invoice model.
    
    Represents an invoice across all integrated systems.
    
    Schema Version: 1.0.0
    """
    
    __schema_version__ = "1.0.0"
    
    # Core fields
    customer_id: str = Field(..., description="Unified customer ID")
    invoice_number: str = Field(..., description="Invoice number")
    status: str = Field(
        ...,
        pattern="^(draft|pending|paid|void|overdue)$",
        description="Invoice status"
    )
    
    # Amounts
    subtotal: Decimal = Field(..., description="Subtotal before tax")
    tax: Decimal = Field(Decimal("0"), description="Tax amount")
    total: Decimal = Field(..., description="Total amount")
    currency: str = Field("USD", description="Currency code")
    
    # Dates
    issue_date: date = Field(..., description="Issue date")
    due_date: Optional[date] = Field(None, description="Due date")
    paid_date: Optional[date] = Field(None, description="Payment date")
    
    # Line items
    line_items: List[UnifiedLineItem] = Field(
        default_factory=list,
        description="Invoice items"
    )
    
    # Optional
    notes: Optional[str] = Field(None, description="Invoice notes")
    
    def is_overdue(self) -> bool:
        """Check if invoice is overdue"""
        from datetime import date as date_today
        if self.status == "paid" or not self.due_date:
            return False
        return date_today.today() > self.due_date
    
    def calculate_totals(self) -> None:
        """Recalculate subtotal and total from line items"""
        self.subtotal = sum(
            item.total for item in self.line_items
        )
        self.total = self.subtotal + self.tax
