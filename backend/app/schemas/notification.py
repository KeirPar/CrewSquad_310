from pydantic import BaseModel
from datetime import datetime

class Notification(BaseModel):
    id: int
    content: str
    timestamp: datetime
    is_read: bool