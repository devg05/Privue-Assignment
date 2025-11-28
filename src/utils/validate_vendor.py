from uuid import UUID
from sqlalchemy.orm import Session
from fastapi import HTTPException

from src.models import VendorModel, VendorScoreModel
from src.schema import VendorResponse


def load_vendor(session: Session, vendor_id: UUID) -> VendorModel:
    vendor = session.get(VendorModel, vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=404,
            detail="Vendor not found"
        )
    return vendor


def vendor_to_response(vendor: VendorModel, latest_score: VendorScoreModel | None) -> VendorResponse:
    return VendorResponse(
        id=vendor.id,
        name=vendor.name,
        category=vendor.category,
        created_at=vendor.created_at,
        updated_at=vendor.updated_at,
        latest_score=latest_score.score if latest_score else None,
    )