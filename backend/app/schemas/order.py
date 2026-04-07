from pydantic import BaseModel
from datetime import datetime
from app.schemas.menu_item import MenuItem
from .bill import Bill
from enum import Enum
from app.packages.geo.coordinate import Coordinate
from .cart import Cart

class OrderStatus(str, Enum):
    PENDING = "PENDING"
    PREPARING = "PREPARING"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    SCHEDULED = "SCHEDULED"

class OrderCreate(BaseModel):
    user_id: int
    cart: Cart

class Order(BaseModel):
    id: int
    created_at: datetime
    status: OrderStatus
    restaurant_id: int
    items: list[MenuItem]
    delivery_address: str
    coordinate: Coordinate
    delivery_note: str = ""
    bill: Bill