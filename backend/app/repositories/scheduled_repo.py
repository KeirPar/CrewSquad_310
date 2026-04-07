from typing import List, Optional
from app.schemas.scheduled_order import ScheduledOrder


class ScheduledOrderRepository:
    """
    In-memory repository for scheduled orders.
    Consistent with the pattern used by other repositories in the project.
    """

    def __init__(self):
        self._scheduled_orders: List[ScheduledOrder] = []
        self._counter: int = 0

    def next_id(self) -> int:
        """Returns the next unique ID for a scheduled order."""
        self._counter += 1
        return self._counter

    def save(self, scheduled_order: ScheduledOrder) -> ScheduledOrder:
        """Persists a new scheduled order."""
        self._scheduled_orders.append(scheduled_order)
        return scheduled_order

    def find_by_id(self, scheduled_order_id: int) -> Optional[ScheduledOrder]:
        """Returns a scheduled order by its ID, or None if not found."""
        return next(
            (so for so in self._scheduled_orders if so.id == scheduled_order_id),
            None
        )

    def find_by_user_id(self, user_id: int) -> List[ScheduledOrder]:
        """Returns all scheduled orders for a specific user."""
        return [so for so in self._scheduled_orders if so.user_id == user_id]

    def get_all(self) -> List[ScheduledOrder]:
        """Returns all scheduled orders in the system."""
        return self._scheduled_orders


scheduled_order_db = ScheduledOrderRepository()