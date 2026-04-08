from pydantic import BaseModel
from enum import Enum

class ReportTargetType(str, Enum):
    RESTAURANT = "Restaurant"
    DRIVER = "Driver"

class ReportStatus(str, Enum):
    OPEN = "OPEN"
    VALIDATED = "VALIDATED"
    DISMISSED = "DISMISSED"

class ReportCreate(BaseModel):
    order_id: int
    target_type: ReportTargetType
    target_id: int
    reason: str

class Report(ReportCreate):
    id: int
    status: ReportStatus = ReportStatus.OPEN
    admin_notes: str = ""