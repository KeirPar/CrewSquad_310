from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    id: int
    sender_id: int
    receiver_id: int
    content: str
    sent_at: datetime