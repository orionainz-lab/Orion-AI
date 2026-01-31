"""
Unified Customer Model

Canonical customer/contact representation across systems.
Maps to: Stripe Customer, HubSpot Contact, Salesforce Account, etc.
"""

from pydantic import EmailStr, Field
from typing import Optional, List
from .base import UnifiedBase


class UnifiedAddress(UnifiedBase):
    """
    Unified address model.
    
    Can be used for billing, shipping, or general addresses.
    """
    
    street: Optional[str] = Field(None, description="Street address")
    street2: Optional[str] = Field(None, description="Apt/Suite number")
    city: Optional[str] = Field(None, description="City")
    state: Optional[str] = Field(None, description="State/Province")
    postal_code: Optional[str] = Field(None, description="ZIP/Postal code")
    country: Optional[str] = Field(None, description="Country code")
    
    def format_single_line(self) -> str:
        """Format address as single line"""
        parts = [
            self.street,
            self.street2,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join(p for p in parts if p)


class UnifiedCustomer(UnifiedBase):
    """
    Canonical customer model.
    
    Represents a customer/contact across all integrated systems.
    
    Schema Version: 1.0.0
    - email: Required email address
    - name: Required full name
    - phone: Optional phone number
    - company: Optional company name
    - addresses: Optional billing/shipping addresses
    - tags: Optional list of labels
    - custom_fields: Optional custom metadata
    """
    
    __schema_version__ = "1.0.0"
    
    # Core required fields
    email: EmailStr = Field(..., description="Email address")
    name: str = Field(..., min_length=1, description="Full name")
    
    # Optional fields
    phone: Optional[str] = Field(None, description="Phone number")
    company: Optional[str] = Field(None, description="Company name")
    
    # Nested objects
    billing_address: Optional[UnifiedAddress] = Field(
        None,
        description="Billing address"
    )
    shipping_address: Optional[UnifiedAddress] = Field(
        None,
        description="Shipping address"
    )
    
    # Metadata
    tags: List[str] = Field(
        default_factory=list,
        description="Labels/tags"
    )
    custom_fields: dict = Field(
        default_factory=dict,
        description="Custom key-value data"
    )
    
    # Status
    is_active: bool = Field(True, description="Active status")
    
    def get_display_name(self) -> str:
        """Get formatted display name"""
        if self.company:
            return f"{self.name} ({self.company})"
        return self.name
    
    def has_complete_billing_address(self) -> bool:
        """Check if billing address is complete"""
        if not self.billing_address:
            return False
        return all([
            self.billing_address.street,
            self.billing_address.city,
            self.billing_address.postal_code,
            self.billing_address.country
        ])
