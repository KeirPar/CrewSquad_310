from pydantic import BaseModel
from datetime import datetime
from app.schemas.menu_item import MenuItem

class Order(BaseModel):
    id: int
    created_at: datetime
    status: str
    restaurant_id: int
    items: list[MenuItem]
    total_amount: float