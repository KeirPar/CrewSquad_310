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

order_db = OrderRepository()