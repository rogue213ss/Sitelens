import enum
import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, String, Text, Boolean, Integer, ForeignKey, Float, LargeBinary
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base


class ScanStatus(str, enum.Enum):
    QUEUED = "QUEUED"
    RUNNING = "RUNNING"
    COMPLETE = "COMPLETE"
    FAILED = "FAILED"


def _new_scan_id() -> str:
    return uuid.uuid4().hex


class Scan(Base):
    """A single request to analyze a website."""
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

    page: Mapped["ScanPage"] = relationship(back_populates="scan", uselist=False, cascade="all, delete-orphan")
    links: Mapped[list["ScanLink"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    scripts: Mapped[list["ScanScript"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    stylesheets: Mapped[list["ScanStylesheet"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    images: Mapped[list["ScanImage"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    network_requests: Mapped[list["ScanNetworkRequest"]] = relationship(back_populates="scan", cascade="all, delete-orphan")
    performance: Mapped["ScanPerformance"] = relationship(back_populates="scan", uselist=False, cascade="all, delete-orphan")
    screenshot: Mapped["ScanScreenshot"] = relationship(back_populates="scan", uselist=False, cascade="all, delete-orphan")


def _new_uuid() -> str:
    return uuid.uuid4().hex


class ScanPage(Base):
    __tablename__ = "scan_pages"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True)
    requested_url: Mapped[str] = mapped_column(Text, nullable=False)
    final_url: Mapped[str] = mapped_column(Text, nullable=False)
    page_title: Mapped[str] = mapped_column(Text, nullable=False)
    status_code: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    viewport: Mapped[str | None] = mapped_column(Text, nullable=True)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    html: Mapped[str | None] = mapped_column(Text, nullable=True)
    scan: Mapped["Scan"] = relationship(back_populates="page")


class ScanLink(Base):
    __tablename__ = "scan_links"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    is_external: Mapped[bool] = mapped_column(Boolean, nullable=False)
    scan: Mapped["Scan"] = relationship(back_populates="links")


class ScanScript(Base):
    __tablename__ = "scan_scripts"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_inline: Mapped[bool] = mapped_column(Boolean, nullable=False)
    script_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    scan: Mapped["Scan"] = relationship(back_populates="scripts")


class ScanStylesheet(Base):
    __tablename__ = "scan_stylesheets"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_inline: Mapped[bool] = mapped_column(Boolean, nullable=False)
    scan: Mapped["Scan"] = relationship(back_populates="stylesheets")


class ScanImage(Base):
    __tablename__ = "scan_images"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    alt_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    width: Mapped[int | None] = mapped_column(Integer, nullable=True)
    height: Mapped[int | None] = mapped_column(Integer, nullable=True)
    scan: Mapped["Scan"] = relationship(back_populates="images")


class ScanNetworkRequest(Base):
    __tablename__ = "scan_requests"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False)
    url: Mapped[str] = mapped_column(Text, nullable=False)
    method: Mapped[str] = mapped_column(String(16), nullable=False)
    resource_type: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[int] = mapped_column(Integer, nullable=False)
    content_type: Mapped[str | None] = mapped_column(Text, nullable=True)
    scan: Mapped["Scan"] = relationship(back_populates="network_requests")


class ScanPerformance(Base):
    __tablename__ = "scan_performance"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True)
    navigation_start: Mapped[float | None] = mapped_column(Float, nullable=True)
    dom_content_loaded: Mapped[float | None] = mapped_column(Float, nullable=True)
    load_event: Mapped[float | None] = mapped_column(Float, nullable=True)
    request_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    scan: Mapped["Scan"] = relationship(back_populates="performance")


class ScanScreenshot(Base):
    __tablename__ = "scan_screenshots"
    id: Mapped[str] = mapped_column(String(32), primary_key=True, default=_new_uuid)
    scan_id: Mapped[str] = mapped_column(String(32), ForeignKey("scans.id", ondelete="CASCADE"), nullable=False, unique=True)
    image_data: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    scan: Mapped["Scan"] = relationship(back_populates="screenshot")
