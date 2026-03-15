from pydantic import BaseModel
from datetime import datetime
from app.schemas.menu_item import MenuItem
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"


class Order(BaseModel):
    id: int
    created_at: datetime
    status: OrderStatus
    restaurant_id: int
    items: list[MenuItem]
    total_amount: float