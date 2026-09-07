import pytest
from sqlalchemy.orm import Session
from app.db.session import engine, Base
from app.models import Scan, ScanStatus
from scanner.scanner import run_scan_task

# Pytest fixture to handle DB
@pytest.fixture(scope="module", autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

def test_run_scan_task_success():
    from app.db.session import SessionLocal
    db = SessionLocal()
    scan = Scan(url="http://example.com", normalized_url="http://example.com/")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    scan_id = scan.id
    db.close()

    # Run the background task directly
    run_scan_task(scan_id)

    db = SessionLocal()
    scan_result = db.get(Scan, scan_id)
    assert scan_result is not None
    assert scan_result.status == ScanStatus.COMPLETE
    assert scan_result.page is not None
    assert scan_result.page.status_code == 200
    assert scan_result.screenshot is not None
    assert scan_result.performance is not None
    db.close()

def test_run_scan_task_blocked():
    from app.db.session import SessionLocal
    db = SessionLocal()
    scan = Scan(url="http://127.0.0.1:8000", normalized_url="http://127.0.0.1:8000/")
    db.add(scan)
    db.commit()
    db.refresh(scan)
    scan_id = scan.id
    db.close()

    # Run the background task directly
    run_scan_task(scan_id)

    db = SessionLocal()
    scan_result = db.get(Scan, scan_id)
    assert scan_result is not None
    assert scan_result.status == ScanStatus.FAILED
    assert "SSRF" in scan_result.error or "blocked" in scan_result.error.lower()
    db.close()
