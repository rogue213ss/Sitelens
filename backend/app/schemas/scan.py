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

# Evidence schemas
class ScanPageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    requested_url: str
    final_url: str
    page_title: str
    status_code: int
    content_type: str | None
    viewport: str | None
    user_agent: str | None
    html: str | None

class ScanLinkSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    text: str
    is_external: bool

class ScanScriptSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str | None
    is_inline: bool
    script_type: str | None

class ScanStylesheetSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str | None
    is_inline: bool

class ScanImageSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    alt_text: str | None
    width: int | None
    height: int | None

class ScanNetworkRequestSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    url: str
    method: str
    resource_type: str
    status: int
    content_type: str | None

class ScanPerformanceSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    navigation_start: float | None
    dom_content_loaded: float | None
    load_event: float | None
    request_count: int

class ScanResultsResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: str
    status: ScanStatus
    error: str | None
    page: ScanPageSchema | None
    links: list[ScanLinkSchema]
    scripts: list[ScanScriptSchema]
    stylesheets: list[ScanStylesheetSchema]
    images: list[ScanImageSchema]
    network_requests: list[ScanNetworkRequestSchema]
    performance: ScanPerformanceSchema | None
    has_screenshot: bool
