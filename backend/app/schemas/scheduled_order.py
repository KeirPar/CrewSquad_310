from pydantic import BaseModel
from datetime import datetime
from app.schemas.order import Order
from app.schemas.cart import Cart


class ScheduledOrderCreate(BaseModel):
    """
    Request body for placing a scheduled order.
    user_id is NOT included here — it comes from the authenticated user via the router.
    """
    cart: Cart
    scheduled_time: datetime  # must be in the future and allow enough time for delivery


class ScheduledOrder(BaseModel):
    """A scheduled order stored in the system."""
    id: int
    user_id: int
    order: Order
    scheduled_time: datetime
    estimated_delivery_time: datetime   # calculated at creation based on distance
    estimated_delivery_minutes: float   # raw number for easy display on frontend
    created_at: datetime
    is_cancelled: bool = False
    cancellation_reason: str = ""       # optional reason when cancelled