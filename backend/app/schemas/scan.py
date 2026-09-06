from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models import ScanStatus


class ScanCreateRequest(BaseModel):
    url: str


class ScanResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    url: str
    normalized_url: str
    status: ScanStatus
    created_at: datetime
    completed_at: datetime | None
    error: str | None


class ScanStatusResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    status: ScanStatus
    error: str | None
