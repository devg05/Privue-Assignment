"""Pydantic schemas for vendor metrics."""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field, field_validator, ConfigDict


class VendorMetricBase(BaseModel):
    """Shared metric fields."""

    timestamp: datetime
    on_time_delivery_rate: float = Field(..., ge=0, le=100)
    complaint_count: int = Field(..., ge=0)
    missing_documents: bool
    compliance_score: float = Field(..., ge=0, le=100)
    raw_payload: Optional[dict] = None


class VendorMetricCreate(VendorMetricBase):
    """Data the client sends when submitting a new metric entry. (Input Schema)"""

    @field_validator("timestamp")
    @classmethod
    def ensure_timezone(cls, value: datetime) -> datetime:
        if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
            raise ValueError("timestamp must be timezone-aware (UTC recommended)")
        return value


class VendorMetricResponse(VendorMetricBase):
    """Data returned back to the client after a metric is stored. (Output Schema)"""

    id: UUID
    vendor_id: UUID
    model_config = ConfigDict(from_attributes=True)
