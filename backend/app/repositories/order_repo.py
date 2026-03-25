from app.schemas.order import Order
from .user_repository import user_db

#   TODO: add types
class OrderRepository:
    """
    A simple in-memory repository for storing orders.
    """
    def __init__(self):
        self._counter = 0
        self._orders = []

    def next_id(self) -> int:
        self._counter += 1
        return self._counter

    def save(self, order) -> None:
        self._orders.append(order)

    def find_by_id(self, order_id):
        return next((o for o in self._orders if o.id == order_id), None)
    
    def find_all_by_user_id(self, user_id) -> list[Order]:
        all_orders_by_user_id: list[Order] = []

        user = user_db.find_by_user_id(user_id)
        order_ids = user.order_history

        for order in self._orders:
            if order.id in order_ids:
                all_orders_by_user_id.append(order)
        return all_orders_by_user_id



order_db = OrderRepository()