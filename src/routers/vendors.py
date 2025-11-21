from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from src.database.databases import get_db

from src.schema import (
    VendorCreate,
    VendorMetricCreate,
    VendorMetricResponse,
    VendorResponse,
    VendorScoreResponse,
)
from src.services import (
    create_metric,
    create_vendor,
    get_vendor_latest_score,
    list_vendor_scores,
    recompute_latest_score,
)

from utils.validate_vendor import load_vendor, vendor_to_response


router = APIRouter(prefix="/vendors", tags=["vendors"])


@router.post("", response_model=VendorResponse, status_code=201)
def register_vendor(payload: VendorCreate, session: Session = Depends(get_db)) -> VendorResponse:
    try:
        vendor = create_vendor(session, payload)
        latest_score = get_vendor_latest_score(session, vendor.id)
        return vendor_to_response(vendor, latest_score)
    
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=409, detail="Vendor already exists") from exc
    
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to register vendor") from exc


@router.post("/{vendor_id}/metrics", response_model=VendorMetricResponse, status_code=201)
def submit_vendor_metrics(
    vendor_id: UUID,
    payload: VendorMetricCreate,
    session: Session = Depends(get_db),
) -> VendorMetricResponse:
    
    vendor = load_vendor(session, vendor_id)

    raw_payload = payload.raw_payload
    if raw_payload is None:
        raw_payload = payload.model_dump(mode="json", exclude={"raw_payload"})

    try:
        metric = create_metric(session, vendor, payload, raw_payload=raw_payload)
        recompute_latest_score(session, vendor)

        return VendorMetricResponse.model_validate(metric, from_attributes=True)
    
    except IntegrityError as exc:
        session.rollback()
        raise HTTPException(status_code=400, detail="Invalid metric submission") from exc
    
    except SQLAlchemyError as exc:
        session.rollback()
        raise HTTPException(status_code=500, detail="Failed to submit vendor metrics") from exc


@router.get("/{vendor_id}", response_model=VendorResponse)
def get_vendor_detail(vendor_id: UUID, session: Session = Depends(get_db)) -> VendorResponse:
    vendor = load_vendor(session, vendor_id)
    try:
        latest_score = get_vendor_latest_score(session, vendor_id)
        return vendor_to_response(vendor, latest_score)
    
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch vendor details") from exc


@router.get("/{vendor_id}/scores", response_model=List[VendorScoreResponse])
def get_vendor_scores(
    vendor_id: UUID,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
    session: Session = Depends(get_db),
) -> List[VendorScoreResponse]:
    
    vendor = load_vendor(session, vendor_id)

    try:
        scores = list_vendor_scores(session, vendor_id, limit=limit, offset=offset)
        
    except SQLAlchemyError as exc:
        raise HTTPException(status_code=500, detail="Failed to fetch vendor scores") from exc
    
    return [
            VendorScoreResponse.model_validate(score, from_attributes=True) 
            for score in scores
        ]
