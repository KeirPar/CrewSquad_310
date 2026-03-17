class OrderIdCounter:
    def __init__(self):
        self._counter = 0

    def next_id(self) -> int:
        self._counter += 1
        return self._counter

order_db = OrderIdCounter()