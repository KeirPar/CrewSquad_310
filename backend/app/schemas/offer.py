from pydantic import BaseModel
from datetime import datetime

class Offer(BaseModel):
    id: int
    description: str
    discount_percentage: float
    valid_until: datetime