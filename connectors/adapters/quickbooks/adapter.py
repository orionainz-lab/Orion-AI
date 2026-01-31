"""
QuickBooks Online Adapter

Accounting connector for invoices, customers, and payments.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from connectors.adapters.base import (
    BaseAdapter,
    AdapterConfig,
    AdapterCapability
)
from connectors.adapters.registry import register_adapter
from connectors.adapters.exceptions import (
    AuthenticationError,
    APIError
)
from connectors.unified_schema.customer import UnifiedCustomer


@register_adapter("quickbooks")
class QuickBooksAdapter(BaseAdapter[UnifiedCustomer]):
    """
    QuickBooks Online adapter.
    
    Supports:
    - Customer CRUD operations
    - Invoice management
    - Payment tracking
    - OAuth 2.0 with token refresh
    - Webhook support
    
    Docs: https://developer.intuit.com/app/developer/qbo/docs/api/accounting/all-entities/customer
    """
    
    name = "quickbooks"
    version = "1.0.0"
    capabilities = [
        AdapterCapability.READ,
        AdapterCapability.WRITE,
        AdapterCapability.WEBHOOK
    ]
    
    BASE_URL = "https://quickbooks.api.intuit.com/v3/company"
    
    def _get_auth_headers(self) -> dict[str, str]:
        """Get QuickBooks OAuth headers"""
        access_token = self.credentials.get("access_token", "")
        if not access_token:
            raise AuthenticationError("QuickBooks access token not provided")
        
        return {
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
            "Content-Type": "application/json"
        }
    
    def _get_realm_id(self) -> str:
        """Get QuickBooks realm ID (company ID)"""
        realm_id = self.credentials.get("realm_id", "")
        if not realm_id:
            raise AuthenticationError("QuickBooks realm_id not provided")
        return realm_id
    
    async def _refresh_token_if_needed(self):
        """
        Refresh OAuth token if expired.
        
        QuickBooks access tokens expire after 1 hour.
        """
        token_expires_at = self.credentials.get("token_expires_at")
        if not token_expires_at:
            return
        
        # Check if token expires in next 5 minutes
        expires_at = datetime.fromisoformat(token_expires_at)
        if datetime.utcnow() + timedelta(minutes=5) < expires_at:
            return  # Token still valid
        
        # Refresh token
        refresh_token = self.credentials.get("refresh_token", "")
        client_id = self.credentials.get("client_id", "")
        client_secret = self.credentials.get("client_secret", "")
        
        if not refresh_token or not client_id or not client_secret:
            raise AuthenticationError("Missing OAuth refresh credentials")
        
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://oauth.platform.intuit.com/oauth2/v1/tokens/bearer",
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": refresh_token
                    },
                    auth=(client_id, client_secret)
                )
                response.raise_for_status()
                token_data = response.json()
                
                # Update credentials
                self.credentials["access_token"] = token_data["access_token"]
                self.credentials["refresh_token"] = token_data["refresh_token"]
                self.credentials["token_expires_at"] = (
                    datetime.utcnow() + timedelta(seconds=token_data["expires_in"])
                ).isoformat()
        
        except Exception as e:
            raise AuthenticationError(f"Token refresh failed: {str(e)}")
    
    async def to_unified(self, data: dict) -> UnifiedCustomer:
        """Transform QuickBooks Customer to unified model"""
        billing_addr = data.get("BillAddr", {})
        primary_phone = data.get("PrimaryPhone", {})
        primary_email = data.get("PrimaryEmailAddr", {})
        
        return UnifiedCustomer(
            source_system="quickbooks",
            source_id=str(data["Id"]),
            email=primary_email.get("Address", "unknown@example.com"),
            name=data.get("DisplayName") or data.get("CompanyName", "Unknown"),
            phone=primary_phone.get("FreeFormNumber"),
            company=data.get("CompanyName"),
            billing_address={
                "source_system": "quickbooks",
                "source_id": str(data["Id"]),
                "street": billing_addr.get("Line1"),
                "street2": billing_addr.get("Line2"),
                "city": billing_addr.get("City"),
                "state": billing_addr.get("CountrySubDivisionCode"),
                "postal_code": billing_addr.get("PostalCode"),
                "country": billing_addr.get("Country")
            } if billing_addr else None,
            custom_fields={
                "quickbooks_sync_token": data.get("SyncToken"),
                "balance": data.get("Balance", 0)
            },
            raw_data=data
        )
    
    async def from_unified(self, model: UnifiedCustomer) -> dict:
        """Transform unified model to QuickBooks format"""
        data = {
            "DisplayName": model.name,
            "PrimaryEmailAddr": {
                "Address": str(model.email)
            }
        }
        
        if model.company:
            data["CompanyName"] = model.company
        
        if model.phone:
            data["PrimaryPhone"] = {
                "FreeFormNumber": model.phone
            }
        
        if model.billing_address:
            data["BillAddr"] = {
                "Line1": model.billing_address.street,
                "Line2": model.billing_address.street2,
                "City": model.billing_address.city,
                "CountrySubDivisionCode": model.billing_address.state,
                "PostalCode": model.billing_address.postal_code,
                "Country": model.billing_address.country or "US"
            }
        
        # Include sync token if updating existing customer
        if model.custom_fields and "quickbooks_sync_token" in model.custom_fields:
            data["SyncToken"] = model.custom_fields["quickbooks_sync_token"]
        
        return data
    
    async def list_customers(
        self,
        limit: int = 100,
        modified_since: Optional[datetime] = None
    ) -> List[UnifiedCustomer]:
        """
        List customers from QuickBooks.
        
        Args:
            limit: Max customers (1-1000)
            modified_since: Only customers modified after this date
        
        Returns:
            List of unified customers
        """
        if not self._client:
            await self.connect()
        
        await self._refresh_token_if_needed()
        
        # Build query
        query = f"SELECT * FROM Customer MAXRESULTS {min(limit, 1000)}"
        if modified_since:
            date_str = modified_since.strftime("%Y-%m-%d")
            query += f" WHERE MetaData.LastUpdatedTime >= '{date_str}'"
        
        try:
            realm_id = self._get_realm_id()
            response = await self._client.get(
                f"{self.BASE_URL}/{realm_id}/query",
                params={"query": query}
            )
            response.raise_for_status()
            data = response.json()
            
            customers = data.get("QueryResponse", {}).get("Customer", [])
            return [await self.to_unified(c) for c in customers]
        
        except Exception as e:
            raise APIError(
                f"Failed to list customers: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def create_customer(
        self,
        customer: UnifiedCustomer
    ) -> UnifiedCustomer:
        """
        Create customer in QuickBooks.
        
        Args:
            customer: Unified customer model
        
        Returns:
            Created customer with QuickBooks ID
        """
        if not self._client:
            await self.connect()
        
        await self._refresh_token_if_needed()
        
        payload = await self.from_unified(customer)
        
        try:
            realm_id = self._get_realm_id()
            response = await self._client.post(
                f"{self.BASE_URL}/{realm_id}/customer",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            return await self.to_unified(result["Customer"])
        
        except Exception as e:
            raise APIError(
                f"Failed to create customer: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def update_customer(
        self,
        customer: UnifiedCustomer
    ) -> UnifiedCustomer:
        """
        Update customer in QuickBooks.
        
        Requires source_id and sync_token in custom_fields.
        
        Args:
            customer: Unified customer model with source_id
        
        Returns:
            Updated customer
        """
        if not self._client:
            await self.connect()
        
        if not customer.source_id:
            raise APIError("Customer source_id required for update")
        
        await self._refresh_token_if_needed()
        
        payload = await self.from_unified(customer)
        payload["Id"] = customer.source_id
        
        try:
            realm_id = self._get_realm_id()
            response = await self._client.post(
                f"{self.BASE_URL}/{realm_id}/customer",
                json=payload
            )
            response.raise_for_status()
            result = response.json()
            
            return await self.to_unified(result["Customer"])
        
        except Exception as e:
            raise APIError(
                f"Failed to update customer: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def sync_invoices(
        self,
        since: Optional[datetime] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Sync invoices from QuickBooks.
        
        Args:
            since: Only invoices modified after this date
            limit: Max invoices to fetch
        
        Returns:
            List of invoice records (not yet converted to unified schema)
        """
        if not self._client:
            await self.connect()
        
        await self._refresh_token_if_needed()
        
        # Build query
        query = f"SELECT * FROM Invoice MAXRESULTS {min(limit, 1000)}"
        if since:
            date_str = since.strftime("%Y-%m-%d")
            query += f" WHERE MetaData.LastUpdatedTime >= '{date_str}'"
        
        try:
            realm_id = self._get_realm_id()
            response = await self._client.get(
                f"{self.BASE_URL}/{realm_id}/query",
                params={"query": query}
            )
            response.raise_for_status()
            data = response.json()
            
            return data.get("QueryResponse", {}).get("Invoice", [])
        
        except Exception as e:
            raise APIError(
                f"Failed to sync invoices: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
    
    async def get_customer_by_id(self, customer_id: str) -> UnifiedCustomer:
        """
        Get customer by QuickBooks ID.
        
        Args:
            customer_id: QuickBooks customer ID
        
        Returns:
            Unified customer
        """
        if not self._client:
            await self.connect()
        
        await self._refresh_token_if_needed()
        
        try:
            realm_id = self._get_realm_id()
            response = await self._client.get(
                f"{self.BASE_URL}/{realm_id}/customer/{customer_id}"
            )
            response.raise_for_status()
            result = response.json()
            
            return await self.to_unified(result["Customer"])
        
        except Exception as e:
            raise APIError(
                f"Failed to get customer: {str(e)}",
                status_code=getattr(e, "status_code", None)
            )
