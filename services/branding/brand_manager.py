"""
Phase 6C: White-Label Branding - Brand Manager
Dynamic theming, custom domains, and branding customization.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass
from supabase import Client
import hashlib
import secrets


@dataclass
class BrandConfig:
    """Brand configuration model"""
    org_id: str
    # Visual
    logo_url: Optional[str]
    favicon_url: Optional[str]
    primary_color: str
    secondary_color: str
    accent_color: str
    custom_css_url: Optional[str]
    # Email
    email_from_name: Optional[str]
    email_from_address: Optional[str]
    email_header_logo_url: Optional[str]
    email_footer_text: Optional[str]
    # Features
    show_powered_by: bool
    custom_help_link: Optional[str]
    custom_support_email: Optional[str]


@dataclass
class CustomDomain:
    """Custom domain model"""
    org_id: str
    domain: str
    verification_status: str  # 'pending', 'verified', 'failed'
    verification_token: str
    verification_method: str  # 'dns', 'file'
    ssl_status: str  # 'pending', 'provisioned', 'failed'


class BrandManager:
    """
    Manages white-label branding and custom domains.
    
    Features:
    - Dynamic theming (colors, logos)
    - Custom domains with DNS verification
    - Email branding
    - Custom CSS
    - Asset management via CDN
    """
    
    def __init__(self, supabase_client: Client, cdn_base_url: str):
        """
        Initialize brand manager.
        
        Args:
            supabase_client: Supabase client
            cdn_base_url: Base URL for brand assets (Supabase Storage or CDN)
        """
        self.client = supabase_client
        self.cdn_base_url = cdn_base_url
        self.storage_bucket = "brand-assets"
    
    # ========================================
    # BRAND CONFIGURATION
    # ========================================
    
    async def get_brand_config(self, org_id: str) -> Optional[BrandConfig]:
        """Get brand configuration for organization"""
        response = self.client.table("brand_configs").select("*").eq("org_id", org_id).execute()
        
        if not response.data:
            return None
        
        data = response.data[0]
        return BrandConfig(
            org_id=data["org_id"],
            logo_url=data.get("logo_url"),
            favicon_url=data.get("favicon_url"),
            primary_color=data.get("primary_color", "#3B82F6"),
            secondary_color=data.get("secondary_color", "#10B981"),
            accent_color=data.get("accent_color", "#8B5CF6"),
            custom_css_url=data.get("custom_css_url"),
            email_from_name=data.get("email_from_name"),
            email_from_address=data.get("email_from_address"),
            email_header_logo_url=data.get("email_header_logo_url"),
            email_footer_text=data.get("email_footer_text"),
            show_powered_by=data.get("show_powered_by", True),
            custom_help_link=data.get("custom_help_link"),
            custom_support_email=data.get("custom_support_email")
        )
    
    async def create_or_update_brand_config(
        self,
        org_id: str,
        **config
    ) -> BrandConfig:
        """Create or update brand configuration"""
        # Check if config exists
        existing = await self.get_brand_config(org_id)
        
        if existing:
            # Update
            response = self.client.table("brand_configs").update(config).eq("org_id", org_id).execute()
        else:
            # Create
            config["org_id"] = org_id
            response = self.client.table("brand_configs").insert(config).execute()
        
        if not response.data:
            raise Exception("Failed to save brand configuration")
        
        return await self.get_brand_config(org_id)
    
    async def get_theme_css(self, org_id: str) -> str:
        """
        Generate CSS variables for organization theme.
        
        Returns:
            CSS string with custom theme variables
        """
        brand = await self.get_brand_config(org_id)
        
        if not brand:
            # Return default theme
            return self._generate_default_theme()
        
        css = f"""
:root {{
  /* Brand Colors */
  --color-primary: {brand.primary_color};
  --color-secondary: {brand.secondary_color};
  --color-accent: {brand.accent_color};
  
  /* Derived Colors */
  --color-primary-hover: {self._darken_color(brand.primary_color, 10)};
  --color-primary-light: {self._lighten_color(brand.primary_color, 90)};
  
  /* Brand Assets */
  --logo-url: url('{brand.logo_url or '/default-logo.png'}');
  --favicon-url: url('{brand.favicon_url or '/default-favicon.png'}');
}}

/* Apply brand colors to common components */
.btn-primary {{
  background-color: var(--color-primary);
}}

.btn-primary:hover {{
  background-color: var(--color-primary-hover);
}}

.text-primary {{
  color: var(--color-primary);
}}

.bg-primary {{
  background-color: var(--color-primary);
}}

.border-primary {{
  border-color: var(--color-primary);
}}

/* Hide powered-by if configured */
{"" if brand.show_powered_by else ".powered-by { display: none; }"}
"""
        
        # Add custom CSS if provided
        if brand.custom_css_url:
            css += f"\n/* Custom CSS */\n@import url('{brand.custom_css_url}');\n"
        
        return css
    
    # ========================================
    # ASSET MANAGEMENT
    # ========================================
    
    async def upload_logo(
        self,
        org_id: str,
        file_path: str,
        file_content: bytes
    ) -> str:
        """
        Upload organization logo to CDN.
        
        Args:
            org_id: Organization ID
            file_path: Original file name (e.g., logo.png)
            file_content: File bytes
        
        Returns:
            Public URL of uploaded logo
        """
        # Generate unique filename
        ext = file_path.split(".")[-1]
        filename = f"{org_id}/logo.{ext}"
        
        # Upload to Supabase Storage
        self.client.storage.from_(self.storage_bucket).upload(
            filename,
            file_content,
            {"content-type": f"image/{ext}"}
        )
        
        # Get public URL
        url = self.client.storage.from_(self.storage_bucket).get_public_url(filename)
        
        # Update brand config
        await self.create_or_update_brand_config(org_id, logo_url=url)
        
        return url
    
    async def upload_favicon(
        self,
        org_id: str,
        file_content: bytes
    ) -> str:
        """Upload organization favicon"""
        filename = f"{org_id}/favicon.ico"
        
        self.client.storage.from_(self.storage_bucket).upload(
            filename,
            file_content,
            {"content-type": "image/x-icon"}
        )
        
        url = self.client.storage.from_(self.storage_bucket).get_public_url(filename)
        
        await self.create_or_update_brand_config(org_id, favicon_url=url)
        
        return url
    
    async def upload_custom_css(
        self,
        org_id: str,
        css_content: str
    ) -> str:
        """Upload custom CSS file"""
        filename = f"{org_id}/custom.css"
        
        self.client.storage.from_(self.storage_bucket).upload(
            filename,
            css_content.encode(),
            {"content-type": "text/css"}
        )
        
        url = self.client.storage.from_(self.storage_bucket).get_public_url(filename)
        
        await self.create_or_update_brand_config(org_id, custom_css_url=url)
        
        return url
    
    # ========================================
    # CUSTOM DOMAINS
    # ========================================
    
    async def add_custom_domain(
        self,
        org_id: str,
        domain: str,
        verification_method: str = "dns"
    ) -> CustomDomain:
        """
        Add custom domain for organization.
        
        Args:
            org_id: Organization ID
            domain: Domain name (e.g., integrations.company.com)
            verification_method: 'dns' or 'file'
        
        Returns:
            CustomDomain with verification token
        """
        # Generate verification token
        verification_token = f"orion-verify-{secrets.token_urlsafe(32)}"
        
        # Insert domain
        domain_data = {
            "org_id": org_id,
            "domain": domain,
            "verification_status": "pending",
            "verification_token": verification_token,
            "verification_method": verification_method,
            "ssl_status": "pending"
        }
        
        response = self.client.table("domain_verifications").insert(domain_data).execute()
        
        if not response.data:
            raise Exception(f"Failed to add domain: {domain}")
        
        data = response.data[0]
        
        return CustomDomain(
            org_id=data["org_id"],
            domain=data["domain"],
            verification_status=data["verification_status"],
            verification_token=data["verification_token"],
            verification_method=data["verification_method"],
            ssl_status=data["ssl_status"]
        )
    
    async def get_domain_verification_instructions(
        self,
        domain: str
    ) -> Dict[str, Any]:
        """
        Get verification instructions for custom domain.
        
        Returns:
            DNS records or file instructions
        """
        response = self.client.table("domain_verifications").select("*").eq("domain", domain).execute()
        
        if not response.data:
            raise Exception(f"Domain not found: {domain}")
        
        domain_data = response.data[0]
        method = domain_data["verification_method"]
        token = domain_data["verification_token"]
        
        if method == "dns":
            return {
                "method": "dns",
                "instructions": "Add the following TXT record to your DNS:",
                "records": [
                    {
                        "type": "TXT",
                        "name": "_orion-verification",
                        "value": token,
                        "ttl": 3600
                    },
                    {
                        "type": "CNAME",
                        "name": domain,
                        "value": "app.orion-ai.com",
                        "ttl": 3600
                    }
                ]
            }
        else:
            # File verification
            return {
                "method": "file",
                "instructions": f"Upload a file to: https://{domain}/.well-known/orion-verification.txt",
                "file_content": token
            }
    
    async def verify_domain(self, domain: str) -> bool:
        """
        Verify custom domain ownership.
        
        Checks DNS/file and updates verification status.
        
        Returns:
            True if verified
        """
        # Get domain data
        response = self.client.table("domain_verifications").select("*").eq("domain", domain).execute()
        
        if not response.data:
            return False
        
        domain_data = response.data[0]
        method = domain_data["verification_method"]
        token = domain_data["verification_token"]
        
        verified = False
        
        if method == "dns":
            # Check DNS TXT record
            # TODO: Implement DNS lookup
            # For now, manual verification
            verified = False
        else:
            # Check file
            # TODO: Implement HTTP file check
            verified = False
        
        if verified:
            # Update status
            self.client.table("domain_verifications").update({
                "verification_status": "verified",
                "verified_at": "now()"
            }).eq("domain", domain).execute()
        
        return verified
    
    async def get_custom_domains(self, org_id: str) -> list[CustomDomain]:
        """Get all custom domains for organization"""
        response = self.client.table("domain_verifications").select("*").eq("org_id", org_id).execute()
        
        if not response.data:
            return []
        
        return [
            CustomDomain(
                org_id=d["org_id"],
                domain=d["domain"],
                verification_status=d["verification_status"],
                verification_token=d["verification_token"],
                verification_method=d["verification_method"],
                ssl_status=d["ssl_status"]
            )
            for d in response.data
        ]
    
    # ========================================
    # HELPER METHODS
    # ========================================
    
    def _generate_default_theme(self) -> str:
        """Generate default theme CSS"""
        return """
:root {
  --color-primary: #3B82F6;
  --color-secondary: #10B981;
  --color-accent: #8B5CF6;
  --logo-url: url('/default-logo.png');
  --favicon-url: url('/default-favicon.png');
}
"""
    
    def _darken_color(self, hex_color: str, percent: int) -> str:
        """Darken a hex color by percentage"""
        # Simple implementation - in production, use proper color library
        return hex_color
    
    def _lighten_color(self, hex_color: str, percent: int) -> str:
        """Lighten a hex color by percentage"""
        # Simple implementation - in production, use proper color library
        return hex_color


# Example usage
"""
from services.branding.brand_manager import BrandManager

brand_manager = BrandManager(
    supabase_client,
    cdn_base_url="https://[project].supabase.co/storage/v1/object/public/brand-assets"
)

# Update branding
await brand_manager.create_or_update_brand_config(
    org_id="org-123",
    primary_color="#FF6B6B",
    secondary_color="#4ECDC4",
    logo_url="https://cdn.company.com/logo.png",
    show_powered_by=False
)

# Get theme CSS for frontend
theme_css = await brand_manager.get_theme_css("org-123")

# Add custom domain
domain = await brand_manager.add_custom_domain(
    org_id="org-123",
    domain="integrations.company.com"
)

# Get verification instructions
instructions = await brand_manager.get_domain_verification_instructions(domain.domain)
"""
