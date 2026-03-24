from datetime import datetime
from app.schemas.order import Order
from app.schemas.notification import Notification, NotificationType
from app.repositories.notification_repo import notification_db


def create_order_notification(order: Order) -> Notification:
    """Creates a notification for a new order."""
    notification = Notification(
        id = len(notification_db.get_all()) + 1,
        content = f"New order #{order.id} received from {order.restaurant_id}.",
        timestamp = datetime.now(),
        is_read = False,
        notification_type = NotificationType.NEW_ORDER,
        order_id = order.id,
        restaurant_id = order.restaurant_id
    )
    return notification_db.save(notification)