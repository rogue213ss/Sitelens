import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.db.session import Base


class ScanStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


def _new_scan_id() -> str:
    return uuid.uuid4().hex


class Scan(Base):
    """A single request to analyze a website.

    Part 1 only ever creates scans in the QUEUED state - no analysis
    pipeline exists yet. The columns for status, timestamps, and error
    are here so later parts can update this same record in place.
    """

    __tablename__ = "scans"

    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_scan_id)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    normalized_url: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ScanStatus] = mapped_column(
        Enum(ScanStatus, native_enum=False, length=16),
        default=ScanStatus.QUEUED,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
