from fastapi import APIRouter, HTTPException
from app.repositories.notification_repo import notification_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def get_all_notifications():
    """Returns all notifications in the system (for testing purposes)."""
    return {"notifications": notification_db.get_all()}

@router.get("/order/{order_id}")
def get_notifications_for_order(order_id: int):
    """Returns all notifications associated with a specific order ID."""
    return {"notifications": notification_db.find_by_order_id(order_id)}

@router.get("/recipient/{recipient_id}")
def get_notifications_for_recipient(recipient_id: int):
    """Returns all notifications for a specific recipient (e.g. user or restaurant)."""
    return {"notifications": notification_db.find_by_recipient_id(recipient_id)}

@router.get("/order/{order_id}/recipient/{recipient_id}")
def get_order_timeline_for_recipient(order_id: int, recipient_id: int):
    """Returns a chronological timeline of notifications for a specific order and recipient."""

    timeline = notification_db.find_by_order_and_recipient(order_id, recipient_id)

    if not timeline:
        raise HTTPException(status_code=404, detail="No notifications found for this order and recipient")
    
    return {
        "order_id": order_id,
        "recipient_id": recipient_id,
        "timeline": timeline
    }