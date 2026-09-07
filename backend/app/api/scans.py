from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models import Scan
from app.schemas.scan import ScanCreateRequest, ScanResponse, ScanStatusResponse, ScanResultsResponse
from app.url_validation import InvalidUrlError, validate_and_normalize_url
from scanner.scanner import run_scan_task

router = APIRouter(prefix="/api/scans", tags=["scans"])


@router.post("", response_model=ScanResponse, status_code=201)
def create_scan(
    payload: ScanCreateRequest, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
) -> Scan:
    try:
        normalized_url = validate_and_normalize_url(payload.url)
    except InvalidUrlError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc

    scan = Scan(url=payload.url.strip(), normalized_url=normalized_url)
    db.add(scan)
    db.commit()
    db.refresh(scan)

    # Enqueue the actual background scan
    background_tasks.add_task(run_scan_task, scan.id)

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


@router.get("/{scan_id}/results", response_model=ScanResultsResponse)
def get_scan_results(scan_id: str, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    
    # We map the SQLAlchemy object to the Pydantic model
    return {
        "id": scan.id,
        "status": scan.status,
        "error": scan.error,
        "page": scan.page,
        "links": scan.links,
        "scripts": scan.scripts,
        "stylesheets": scan.stylesheets,
        "images": scan.images,
        "network_requests": scan.network_requests,
        "performance": scan.performance,
        "has_screenshot": scan.screenshot is not None
    }


@router.get("/{scan_id}/screenshot")
def get_scan_screenshot(scan_id: str, db: Session = Depends(get_db)):
    scan = db.get(Scan, scan_id)
    if scan is None:
        raise HTTPException(status_code=404, detail="Scan not found.")
    
    if scan.screenshot is None:
        raise HTTPException(status_code=404, detail="No screenshot available.")
    
    return Response(content=scan.screenshot.image_data, media_type="image/png")
