from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from src.models import VendorMetricModel, VendorModel, VendorScoreModel

CATEGORY_WEIGHTS = {
    "supplier": 1.0,
    "distributor": 0.95,
    "dealer": 0.9,
    "manufacturer": 1.05,
}


def clamp_score(value: float) -> float:
    """Clamp a score to the inclusive range [0, 100]."""

    return max(0.0, min(100.0, value))


def _complaint_penalty(complaints: int) -> float:
    """Penalty curve for complaint counts."""

    # 1 complaint = 1.25 penalty, maxing out at 20 complaints = 25 penalty
    return min(complaints * 1.25, 25.0)


def _missing_docs_penalty(missing: bool) -> float:
    return 10.0 if missing else 0.0


def compute_score(metric: VendorMetricModel, vendor: VendorModel) -> float:
    """Compute a deterministic score for a given metric."""

    delivery_component = metric.on_time_delivery_rate * 0.45
    compliance_component = metric.compliance_score * 0.4
    reliability_component = max(0, 15 - _complaint_penalty(metric.complaint_count))
    penalty_component = _missing_docs_penalty(metric.missing_documents)

    raw_score = delivery_component + compliance_component + reliability_component - penalty_component
    weight = CATEGORY_WEIGHTS.get(vendor.category, 1.0)

    return clamp_score(raw_score * weight)


def record_score_snapshot(session: Session, vendor: VendorModel, score_value: float) -> VendorScoreModel:
    """Record a recent score calculated for a vendor."""

    snapshot = VendorScoreModel(
        vendor_id=vendor.id,
        calculated_at=datetime.now(timezone.utc),
        score=score_value,
    )

    try:
        session.add(snapshot)
        session.commit()
        session.refresh(snapshot)
        return snapshot

    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to record vendor score snapshot.") from exc


def recompute_latest_score(session: Session, vendor: VendorModel) -> VendorScoreModel | None:
    """Recompute the score using the most recent vendor metric."""

    metric_stmt = (
        select(VendorMetricModel)
        .where(VendorMetricModel.vendor_id == vendor.id)
        .order_by(VendorMetricModel.timestamp.desc())
        .limit(1)
    )

    try:
        metric = session.execute(metric_stmt).scalars().first()

    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch vendor metrics for scoring.") from exc

    if metric is None:      # Handle case where no metrics exist for the vendor
        return None

    score_value = compute_score(metric, vendor)
    return record_score_snapshot(session, vendor, score_value)


def recompute_all_vendor_scores(session: Session) -> int:
    """Recalculate scores for all vendors; returns number of processed vendors."""

    try:
        vendors = session.execute(select(VendorModel)).scalars().all()

    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to load vendors for score recomputation.") from exc

    processed = 0
    for vendor in vendors:
        if recompute_latest_score(session, vendor):
            processed += 1
    return processed