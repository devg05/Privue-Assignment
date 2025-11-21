from __future__ import annotations

from fastapi import HTTPException
from typing import Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.models import VendorModel, VendorScoreModel
from src.schema import VendorCreate, VendorUpdate


def create_vendor(session: Session, payload: VendorCreate) -> VendorModel:
    """Create an entry for a new vendor and return it."""
    try:
        vendor = VendorModel(name=payload.name, category=payload.category.value)
        session.add(vendor)
        session.commit()
        session.refresh(vendor)
        return vendor
    
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Vendor already exists.") from exc
    
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to create vendor.") from exc


def update_vendor(session: Session, vendor: VendorModel, payload: VendorUpdate) -> VendorModel:
    """Apply updates to an existing vendor."""
    if payload.name is not None:
        vendor.name = payload.name
    if payload.category is not None:
        vendor.category = payload.category.value

    try:
        session.add(vendor)
        session.commit()
        session.refresh(vendor)
        return vendor
    
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to update vendor.") from exc


def get_vendor_latest_score(session: Session, vendor_id: UUID) -> Optional[VendorScoreModel]:
    """Return the most recent score for a vendor."""
    stmt = (
        select(VendorScoreModel)
        .where(VendorScoreModel.vendor_id == vendor_id)
        .order_by(VendorScoreModel.calculated_at.desc())
        .limit(1)
    )
    try:
        return session.execute(stmt).scalars().first()
    
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch latest vendor score.") from exc


def list_vendor_scores(session: Session, vendor_id: UUID, *, limit: int = 10, offset: int = 0) -> list[VendorScoreModel]:
    """Return list of vendor score history."""
    stmt = (
        select(VendorScoreModel)
        .where(VendorScoreModel.vendor_id == vendor_id)
        .order_by(VendorScoreModel.calculated_at.desc())
        .offset(offset)
        .limit(limit)
    )
    try:
        return list(session.execute(stmt).scalars().all())
    
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch vendor score history.") from exc