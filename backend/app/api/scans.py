from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Scan
from app.schemas.scan import ScanCreateRequest, ScanResponse, ScanStatusResponse
from app.url_validation import InvalidUrlError, validate_and_normalize_url

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("", response_model=ScanResponse, status_code=201)
def create_scan(payload: ScanCreateRequest, db: Session = Depends(get_db)) -> Scan:
    try:
        normalized_url = validate_and_normalize_url(payload.url)
    except InvalidUrlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    scan = Scan(url=payload.url.strip(), normalized_url=normalized_url)
    db.add(scan)
    db.commit()
    db.refresh(scan)
    return scan


@router.get("/{scan_id}", response_model=ScanResponse)
def get_scan(scan_id: str, db: Session = Depends(get_db)) -> Scan:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan


@router.get("/{scan_id}/status", response_model=ScanStatusResponse)
def get_scan_status(scan_id: str, db: Session = Depends(get_db)) -> Scan:
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    return scan
