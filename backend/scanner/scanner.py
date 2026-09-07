import asyncio
import logging

from app.db.session import SessionLocal
from app.models import (
    Scan, ScanStatus, ScanPage, ScanLink, ScanScript,
    ScanStylesheet, ScanImage, ScanNetworkRequest, ScanPerformance, ScanScreenshot
)
from scanner.capture import capture_evidence
from scanner.security import SecurityBlockedError

logger = logging.getLogger(__name__)

def run_scan_task(scan_id: str):
    """
    Synchronous entry point for the FastAPI BackgroundTask.
    """
    db = SessionLocal()
    try:
        scan = db.get(Scan, scan_id)
        if not scan:
            logger.error(f"Scan {scan_id} not found.")
            return

        scan.status = ScanStatus.RUNNING
        db.commit()

        # Run async capture
        try:
            evidence = asyncio.run(capture_evidence(scan.normalized_url))
            
            # Persist evidence
            # 1. Page
            if "page" in evidence and evidence["page"]:
                page_data = evidence["page"]
                db.add(ScanPage(scan_id=scan_id, **page_data))

            # 2. Links
            for link in evidence.get("links", []):
                db.add(ScanLink(scan_id=scan_id, **link))

            # 3. Scripts
            for script in evidence.get("scripts", []):
                db.add(ScanScript(scan_id=scan_id, **script))

            # 4. Stylesheets
            for style in evidence.get("stylesheets", []):
                db.add(ScanStylesheet(scan_id=scan_id, **style))

            # 5. Images
            for img in evidence.get("images", []):
                db.add(ScanImage(scan_id=scan_id, **img))

            # 6. Network Requests
            for req in evidence.get("network_requests", []):
                db.add(ScanNetworkRequest(scan_id=scan_id, **req))

            # 7. Performance
            if "performance" in evidence and evidence["performance"]:
                perf_data = evidence["performance"]
                db.add(ScanPerformance(scan_id=scan_id, **perf_data))

            # 8. Screenshot
            if evidence.get("screenshot"):
                db.add(ScanScreenshot(scan_id=scan_id, image_data=evidence["screenshot"]))

            scan.status = ScanStatus.COMPLETE
            db.commit()

        except SecurityBlockedError as e:
            scan.status = ScanStatus.FAILED
            scan.error = "Scan blocked due to security policies (SSRF protection)."
            db.commit()
            logger.warning(f"Scan {scan_id} blocked: {e}")

        except Exception as e:
            scan.status = ScanStatus.FAILED
            scan.error = f"Failed to scan: {str(e)}"
            db.commit()
            logger.error(f"Scan {scan_id} failed: {e}", exc_info=True)

    finally:
        db.close()
