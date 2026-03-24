from enum import Enum
from pydantic import BaseModel
from datetime import datetime

class NotificationType(str, Enum):
    NEW_ORDER = "NEW_ORDER"
    ORDER_STATUS_CHANGED = "ORDER_STATUS_CHANGED"  
    PAYMENT_ACCEPTED = "PAYMENT_ACCEPTED"
    PAYMENT_REJECTED = "PAYMENT_REJECTED"

class Notification(BaseModel):
    id: int
    content: str
    timestamp: datetime
    is_read: bool
    notification_type: NotificationType
    order_id: int
    restaurant_id: int
