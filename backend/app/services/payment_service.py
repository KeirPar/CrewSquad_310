from datetime import datetime, timezone
import random
from app.schemas.order import Order, OrderStatus
from app.schemas.payment import PaymentAttempt, PaymentStatus
from app.repositories.payment_repo import payment_db
from app.repositories.order_repo import order_db
from app.services.notification_service import create_payment_notification

REJECTION_REASONS = [
    "Insufficient funds",
    "Card declined by issuer",
    "Invalid card details",
    "Suspected fraud activity",
    "Payment gateway error"
]

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
        amount=order.bill.total,
        status=PaymentStatus.PENDING,
        created_at=datetime.now(timezone.utc)
    )
    return payment_db.save(payment)

def process_payment(order_id: int, decision: PaymentStatus, user_id: int, reason: str = None) -> dict:
    """
    Updates the payment attempt for a given order with the provided decision and reason.

    Args:
        order_id (int): The ID of the order whose payment attempt is to be updated.
        decision (PaymentStatus): The new status for the payment attempt (ACCEPTED or REJECTED).
        user_id (int): The ID of the user initiating the payment update.
        reason (str, optional): An optional reason for the decision.

    Returns:
        PaymentAttempt: The updated payment attempt, or None if no attempt was found for the order.
    """
    if decision == PaymentStatus.PENDING:
        raise ValueError("Payment decision cannot be PENDING.")
    
    payment = payment_db.find_by_order_id(order_id)
    if not payment:
        raise ValueError(f"No payment attempt found for order ID {order_id}.")

    order = order_db.find_by_id(order_id)
    if not order:
        raise ValueError(f"No order found with ID {order_id}.")
    
    updated_payment = payment_db.update_status(order_id, decision, reason)
    
    
    if decision == PaymentStatus.ACCEPTED:
        order.status = OrderStatus.PREPARING
    else:
        order.status = OrderStatus.CANCELLED
    order_db.save(order)

    create_payment_notification(order_id, order.restaurant_id, user_id, decision)

    return {
        "payment": updated_payment,
        "order": order
    }

def simulate_payment(order_id: int, user_id: int) -> dict:
    payment = payment_db.find_by_order_id(order_id)
    if not payment:
        raise ValueError(f"No payment attempt found for order ID {order_id}.")  
        
    if payment.status != PaymentStatus.PENDING:
        raise ValueError(f"Payment attempt for order ID {order_id} is not in PENDING status.")
        
    order = order_db.find_by_id(order_id)
    if not order:
        raise ValueError(f"No order found with ID {order_id}.")
        
    # Simulate a random payment decision
    decision = random.choices([PaymentStatus.ACCEPTED, PaymentStatus.REJECTED], 
                                 weights=[70, 30]) [0] 
    reason = random.choice(REJECTION_REASONS) if decision == PaymentStatus.REJECTED else None
    resolved_at = datetime.now(timezone.utc)

    updated_payment = payment_db.update_status(order_id, decision, reason, resolved_at)  

    if decision == PaymentStatus.ACCEPTED:
        order.status = OrderStatus.PREPARING
    else:
        order.status = OrderStatus.CANCELLED  

    create_payment_notification(order_id, order.restaurant_id, user_id, decision)  
        
    return {
        "simulated": True,
        "payment": updated_payment,
        "order": order
    }