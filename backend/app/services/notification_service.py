from typing import List
from datetime import datetime
from app.schemas.user import User
from app.schemas.order import Order, OrderStatus
from app.schemas.notification import Notification, NotificationType
from app.repositories.notification_repo import notification_db
from app.schemas.payment import PaymentStatus

def create_order_notification(order: Order) -> Notification:
    """Creates a notification for a new order."""
    notification = Notification(
        id = len(notification_db.get_all()) + 1,
        content = f"New order #{order.id} received from {order.restaurant_id}.",
        timestamp = datetime.now(),
        is_read = False,
        notification_type = NotificationType.NEW_ORDER,
        order_id = order.id,
        restaurant_id = order.restaurant_id,
        recipient_id = order.restaurant_id
    )
    return notification_db.save(notification)

def create_status_change_notifications(order: Order, new_status: OrderStatus, current_user: User) -> List[Notification]:
    """
    Creates and stores two notifications when an order status changes (Feat 8-FR2).
 
    One notification is sent to the customer, one to the restaurant owner.
    Both contain the notification type, order ID, restaurant ID, and timestamp.
 
    Args:
        order (Order): The Order object whose status changed.
        new_status (OrderStatus): The new status the order moved to.
        current_user (User): The user who triggered the status change.
 
    Returns:
        List[Notification]: The two stored notifications.
    """
    timestamp = datetime.now()
    content = f"Order #{order.id} status changed to {new_status}."
    created = []
 
    # Notification for the customer who triggered the change
    customer_notification = Notification(
        id=len(notification_db.get_all()) + 1,
        content=content,
        timestamp=timestamp,
        is_read=False,
        notification_type=NotificationType.ORDER_STATUS_CHANGED,
        order_id=order.id,
        restaurant_id=order.restaurant_id,
        recipient_id=current_user.id
    )
    notification_db.save(customer_notification)
    created.append(customer_notification)
 
    # Notification for the restaurant owner
    # Only create a second notification if the restaurant is a different recipient
    if current_user.id != order.restaurant_id:
        restaurant_notification = Notification(
            id=len(notification_db.get_all()) + 1,
            content=content,
            timestamp=timestamp,
            is_read=False,
            notification_type=NotificationType.ORDER_STATUS_CHANGED,
            order_id=order.id,
            restaurant_id=order.restaurant_id,
            recipient_id=order.restaurant_id
        )
        notification_db.save(restaurant_notification)
        created.append(restaurant_notification)
 
    return created

def create_payment_notification(order_id: int, restaurant_id: int, user_id: int, payment_status: PaymentStatus) -> Notification:
    
    notification_type = (
        NotificationType.PAYMENT_ACCEPTED
        if payment_status == PaymentStatus.ACCEPTED
        else NotificationType.PAYMENT_REJECTED
    )
    content = (
        f"Payment for order #{order_id} has been accepted."
        if payment_status == PaymentStatus.ACCEPTED
        else f"Payment for order #{order_id} has been rejected."
    )
    notification = Notification(
        id=len(notification_db.get_all()) + 1,
        content=content,
        timestamp=datetime.now(),
        is_read=False,
        notification_type=notification_type,
        order_id=order_id,
        restaurant_id=restaurant_id,
        recipient_id=user_id
    )
    return notification_db.save(notification)