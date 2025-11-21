from __future__ import annotations

from typing import Any
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.models import VendorMetricModel, VendorModel
from src.schema import VendorMetricCreate


def create_metric(
	session: Session,
	vendor: VendorModel,
	payload: VendorMetricCreate,
	*,
	raw_payload: dict[str, Any] | None = None,      # Can be passed only as Keyword Argument
) -> VendorMetricModel:
	"""Insert a vendor metric submission."""

	metric = VendorMetricModel(
		vendor_id=vendor.id,
		timestamp=payload.timestamp,
		on_time_delivery_rate=payload.on_time_delivery_rate,
		complaint_count=payload.complaint_count,
		missing_documents=payload.missing_documents,
		compliance_score=payload.compliance_score,
		raw_payload=raw_payload,
	)

	try:
		session.add(metric)
		session.commit()
		session.refresh(metric)
		return metric

	except IntegrityError as exc:
		session.rollback()
		raise HTTPException(status_code=400, detail="Invalid vendor metric submission.") from exc

	except SQLAlchemyError as exc:
		session.rollback()
		raise HTTPException(status_code=500, detail="Failed to record vendor metric.") from exc


def get_latest_metric(session: Session, vendor_id: UUID) -> VendorMetricModel | None:
	"""Return the newest metric for a vendor by timestamp."""

	stmt = (
		select(VendorMetricModel)
		.where(VendorMetricModel.vendor_id == vendor_id)
		.order_by(VendorMetricModel.timestamp.desc())
		.limit(1)
	)

	try:
		return session.execute(stmt).scalars().first()

	except SQLAlchemyError as exc:
		raise HTTPException(status_code=500, detail="Failed to fetch latest vendor metric.") from exc