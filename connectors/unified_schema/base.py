"""
Base Unified Schema Model

Provides common fields and behaviors for all unified models.
"""

from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime
from enum import Enum


class SchemaVersion(str, Enum):
    """Semantic versioning for schemas"""
    V1_0_0 = "1.0.0"
    V1_1_0 = "1.1.0"
    V2_0_0 = "2.0.0"


class UnifiedBase(BaseModel):
    """
    Base class for all unified models.
    
    Provides common metadata fields that every unified model inherits.
    """
    
    # Schema version (class attribute, not instance field)
    __schema_version__: str = "1.0.0"
    
    # Source system tracking
    source_system: str = Field(
        ...,
        description="Origin system (e.g., 'stripe', 'hubspot')",
        min_length=1
    )
    source_id: str = Field(
        ...,
        description="ID in source system",
        min_length=1
    )
    unified_id: Optional[str] = Field(
        None,
        description="Platform-generated unified ID"
    )
    
    # Timestamps
    created_at: Optional[datetime] = Field(
        None,
        description="When created in source system"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Last updated in source system"
    )
    synced_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="When synced to our platform"
    )
    
    # Raw data preservation (not serialized by default)
    raw_data: Optional[dict[str, Any]] = Field(
        None,
        description="Original API response",
        exclude=True
    )
    
    class Config:
        """Pydantic configuration"""
        extra = "allow"  # Allow additional fields
        ser_json_timedelta = 'iso8601'
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }


class TransformationMixin:
    """Mixin providing transformation helpers"""
    
    def to_dict(self, exclude_none: bool = True) -> dict:
        """Convert to dictionary with options"""
        return self.model_dump(exclude_none=exclude_none)
    
    def to_json(self) -> str:
        """Convert to JSON string"""
        return self.model_dump_json()
    
    @classmethod
    def from_source(
        cls,
        source_system: str,
        source_data: dict
    ) -> "UnifiedBase":
        """
        Create unified model from source data.
        Override in subclasses for custom transformation.
        """
        raise NotImplementedError(
            "Subclasses must implement from_source"
        )
