import uuid
from datetime import datetime

from sqlalchemy import Integer, Float, Boolean, DateTime, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


from src.models.base import Base


class VendorMetricModel(Base):
    """Stores every metric submission made for each vendor."""

    __tablename__ = "vendor_metrics"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False, index=True
    )
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    on_time_delivery_rate: Mapped[float] = mapped_column(Float, nullable=False)
    complaint_count: Mapped[int] = mapped_column(Integer, nullable=False)
    missing_documents: Mapped[bool] = mapped_column(Boolean, nullable=False)
    compliance_score: Mapped[float] = mapped_column(Float, nullable=False)
    raw_payload: Mapped[dict] = mapped_column(JSON, nullable=True)


    def __repr__(self) -> str:
        return f"<VendorMetric(id={self.id}, vendor_id={self.vendor_id}, timestamp={self.timestamp})>"
