from typing import List, Optional
from app.schemas.payment import PaymentAttempt, PaymentStatus


class PaymentRepository:

    def __init__(self):
        self._payments: List[PaymentAttempt] = []

    def save(self, payment: PaymentAttempt) -> PaymentAttempt:
        """Persists a payment attempt to storage."""
        self._payments.append(payment)
        return payment

    def find_by_order_id(self, order_id: int) -> Optional[PaymentAttempt]:
        """Returns the payment attempt for a given order, or None if not found."""
        return next((p for p in self._payments if p.order_id == order_id), None)

    def get_all(self) -> List[PaymentAttempt]:
        """Returns all stored payment attempts."""
        return self._payments
    
    def update_status(self, order_id: int, status: PaymentStatus, reason=None):
        payment = self.find_by_order_id(order_id)
        if not payment:
            return None
        payment.status = status
        payment.reason = reason
        return payment


payment_db = PaymentRepository()