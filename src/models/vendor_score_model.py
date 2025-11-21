import uuid
from datetime import datetime, timezone

from sqlalchemy import Float, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import ForeignKey


from src.models.base import Base


class VendorScoreModel(Base):
    """Stores history of computed vendor score."""

    __tablename__ = "vendor_scores"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False
    )
    vendor_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("vendors.id"), nullable=False, index=True
    )
    calculated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    score: Mapped[float] = mapped_column(Float, nullable=False)


    def __repr__(self) -> str:
        return f"<VendorScore(id={self.id}, vendor_id={self.vendor_id}, score={self.score})>"
