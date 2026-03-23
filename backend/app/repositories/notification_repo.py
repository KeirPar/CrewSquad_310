from typing import List
from app.schemas.notification import Notification


class NotificationRepository:

    def __init__(self):
        self.notifications: List[Notification] = [] 

    def save(self, notification: Notification):
        """Saves a notification to the repository."""
        self.notifications.append(notification)
        return notification
    
    def find_by_order_id(self, order_id: int) -> List[Notification]:
        """Finds all notifications associated with a specific order ID."""
        return [n for n in self.notifications if n.order_id == order_id]
    
    def get_all(self) -> List[Notification]:
        """Returns all notifications in the repository."""
        return self.notifications
    
notification_db = NotificationRepository()