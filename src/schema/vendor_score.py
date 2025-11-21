from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field, ConfigDict


class VendorScoreResponse(BaseModel):
    """Represents a computed vendor score snapshot."""

    id: UUID
    vendor_id: UUID
    calculated_at: datetime
    score: float = Field(..., ge=0, le=100)

    model_config = ConfigDict(from_attributes=True)
