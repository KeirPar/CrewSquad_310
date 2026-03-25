from fastapi import APIRouter
from app.repositories.notification_repo import notification_db

router = APIRouter(prefix="/notifications", tags=["Notifications"])

@router.get("")
def get_all_notifications():
    return {"notifications": notification_db.get_all()}

@router.get("/order/{order_id}")
def get_notifications_for_order(order_id: int):
    return {"notifications": notification_db.find_by_order_id(order_id)}

@router.get("/recipient/{recipient_id}")
def get_notifications_for_recipient(recipient_id: int):
    return {"notifications": notification_db.find_by_recipient_id(recipient_id)}