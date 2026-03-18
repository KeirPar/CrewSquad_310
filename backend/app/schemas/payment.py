from typing import Optional
from pydantic import BaseModel
from datetime import datetime, timezone
from enum import Enum


class PaymentStatus(str, Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class PaymentAttempt(BaseModel):
    id: int
    order_id: int
    amount: float
    status: PaymentStatus
    created_at: datetime
    resolved_at: Optional[datetime] = None
    reason: Optional[str] = None

class PaymentDecision(BaseModel):
    decision: PaymentStatus
    reason: Optional[str] = None