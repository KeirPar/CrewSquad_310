from pydantic import BaseModel
from datetime import datetime

class Order(BaseModel):
    id: int
    created_at: datetime
    status: str
    total_amount: float