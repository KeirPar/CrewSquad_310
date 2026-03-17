from datetime import datetime, timezone
from app.schemas.order import Order
from app.schemas.payment import PaymentAttempt, PaymentStatus
from app.repositories.payment_repo import payment_db


def create_payment_attempt(order: Order) -> PaymentAttempt:
    """
    Creates and stores a payment attempt for a given order.
    The attempt is always initialised with a PENDING status.

    Args:
        order (Order): The Order object returned after successful order creation.

    Returns:
        PaymentAttempt: The stored payment attempt.
    """
    payment = PaymentAttempt(
        id=len(payment_db.get_all()) + 1,
        order_id=order.id,
        amount=order.total_amount,
        status=PaymentStatus.PENDING,
        created_at=datetime.now(timezone.utc)
    )
    return payment_db.save(payment)