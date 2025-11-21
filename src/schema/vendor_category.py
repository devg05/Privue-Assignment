from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class VendorCategory(str, Enum):
    """Allowed vendor categories."""

    supplier = "supplier"
    distributor = "distributor"
    dealer = "dealer"
    manufacturer = "manufacturer"


class VendorBase(BaseModel):
    """Common (or Shared) vendor attributes used by multiple operations."""

    name: str = Field(..., min_length=1, max_length=200)
    category: VendorCategory


class VendorCreate(VendorBase):
    """Input Schema for creating a vendor."""
    pass


class VendorUpdate(BaseModel):
    """Input Schema for updating vendor fields."""

    name: Optional[str] = Field(None, min_length=1, max_length=200)
    category: Optional[VendorCategory] = None


class VendorResponse(VendorBase):
    """Output Schema response including metadata and latest score returned to Client."""

    id: UUID
    created_at: datetime
    updated_at: datetime
    latest_score: Optional[float] = Field(None, ge=0, le=100)

    model_config = ConfigDict(from_attributes=True)


class VendorListResponse(BaseModel):
    """Paginated vendor list payload."""

    items: list[VendorResponse]
    count: int
