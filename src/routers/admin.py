from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from src.database.databases import get_db
from src.schema import VendorResponse, VendorScoreRecomputeSummary
from src.services import recompute_all_vendor_scores, recompute_latest_score
from src.utils.validate_vendor import load_vendor, vendor_to_response


router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/vendors/{vendor_id}/scores/recompute", response_model=VendorResponse)
def admin_recompute_vendor_score(
    vendor_id: UUID,
    session: Session = Depends(get_db),
) -> VendorResponse:
    """Force recomputation of a specific vendor's score."""

    try:
        vendor = load_vendor(session, vendor_id)
        snapshot = recompute_latest_score(session, vendor)

    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to recompute vendor score") from exc

    if snapshot is None:
        raise HTTPException(status_code=400, detail="Vendor has no metrics to recompute")

    return vendor_to_response(vendor, snapshot)


@router.get("/vendors/scores/recompute", response_model=VendorScoreRecomputeSummary)
def admin_recompute_all_vendor_scores(
    session: Session = Depends(get_db),
) -> VendorScoreRecomputeSummary:
    """Recompute scores for every vendor and return a summary."""

    try:
        processed = recompute_all_vendor_scores(session)

    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to recompute vendor scores") from exc

    return VendorScoreRecomputeSummary(processed_vendors=processed)
