from fastapi.testclient import TestClient
from app.main import app
from app.helpers.user_test_helper import UserTestHelper
from app.packages.geo.coordinate import Coordinate
from fastapi import status

successful_status = status.HTTP_200_OK
failed_status = status.HTTP_400_BAD_REQUEST

client = TestClient(app)

user_test_helper = UserTestHelper(client)
user_test_helper.register_and_login_user(user=user_test_helper.test_user_create)


def make_cart(restaurant_id=5):
    return {
        "user_id": 1,
        "cart": {
            "id": 1,
            "menu_items": [
                {
                    "id": 1,
                    "name": "Burger",
                    "description": "A juicy burger",
                    "price": 10,
                    "image_url": "http://example.com/burger.jpg",
                    "add_ons": [],
                    "is_available": True,
                    "restaurant_id": restaurant_id
                },
                {
                    "id": 2,
                    "name": "Fries",
                    "description": "Crispy fries",
                    "price": 5,
                    "image_url": "http://example.com/fries.jpg",
                    "add_ons": [],
                    "is_available": True,
                    "restaurant_id": restaurant_id
                }
            ]
        }
    }


def place_order(restaurant_id=5):
    """Places a valid order and returns the full response dict."""
    return client.post("/orders", json=make_cart(restaurant_id)).json()


def build_order_body(order: dict) -> dict:
    """Reconstructs an Order request body from a place_order response."""
    return {
        "id": order["id"],
        "created_at": order["created_at"],
        "status": order["status"],
        "restaurant_id": order["restaurant_id"],
        "items": order["items"],
        "delivery_address": order.get("delivery_address", "123 Test St"),
        "coordinate": order["coordinate"],
        "bill": order["bill"]
    }


def get_notifications():
    return client.get("/notifications").json()["notifications"]


def get_notifications_for_order(order_id):
    return client.get(f"/notifications/order/{order_id}").json()["notifications"]


def get_notifications_for_recipient(recipient_id):
    return client.get(f"/notifications/recipient/{recipient_id}").json()["notifications"]


def change_status(order, new_status):
    """Helper to trigger a status change on an order."""
    return client.patch(
        f"/orders/{order['id']}/status",
        params={"new_status": new_status},
        json=build_order_body(order)
    )


def test_status_change_creates_notifications():
    """Verify that changing order status creates at least one notification."""
    order = place_order()
    before = len(get_notifications_for_order(order["id"]))
    change_status(order, "PREPARING")
    after = len(get_notifications_for_order(order["id"]))
    assert after > before


def test_status_change_notification_type_is_correct():
    """Verify the notification type is ORDER_STATUS_CHANGED."""
    order = place_order()
    change_status(order, "PREPARING")
    notifications = get_notifications_for_order(order["id"])
    status_notifications = [
        n for n in notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
    ]
    assert len(status_notifications) > 0


def test_status_change_notification_has_correct_order_id():
    """Verify the notification stores the correct order ID."""
    order = place_order()
    change_status(order, "PREPARING")
    notifications = get_notifications_for_order(order["id"])
    status_notifications = [
        n for n in notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
    ]
    assert all(n["order_id"] == order["id"] for n in status_notifications)


def test_status_change_notification_has_correct_restaurant_id():
    """Verify the notification stores the correct restaurant ID."""
    order = place_order(restaurant_id=5)
    change_status(order, "PREPARING")
    notifications = get_notifications_for_order(order["id"])
    status_notifications = [
        n for n in notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
    ]
    assert all(n["restaurant_id"] == 5 for n in status_notifications)


def test_status_change_notification_has_timestamp():
    """Verify the notification has a timestamp."""
    order = place_order()
    change_status(order, "PREPARING")
    notifications = get_notifications_for_order(order["id"])
    status_notifications = [
        n for n in notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
    ]
    assert all(n["timestamp"] is not None for n in status_notifications)


def test_status_change_notification_is_unread():
    """Verify the notification starts as unread."""
    order = place_order()
    change_status(order, "PREPARING")
    notifications = get_notifications_for_order(order["id"])
    status_notifications = [
        n for n in notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
    ]
    assert all(n["is_read"] == False for n in status_notifications)


def test_status_change_notifies_restaurant():
    """Verify a notification reaches the restaurant (recipient_id = restaurant_id)."""
    order = place_order(restaurant_id=5)
    change_status(order, "PREPARING")
    restaurant_notifications = get_notifications_for_recipient(5)
    matching = [
        n for n in restaurant_notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
        and n["order_id"] == order["id"]
    ]
    assert len(matching) > 0


def test_status_change_notifies_current_user():
    """Verify a notification reaches the user who triggered the change (recipient_id = user_id)."""
    order = place_order()
    change_status(order, "PREPARING")
    user_notifications = get_notifications_for_recipient(2)
    matching = [
        n for n in user_notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
        and n["order_id"] == order["id"]
    ]
    assert len(matching) > 0


def test_two_notifications_created_for_different_user_and_restaurant():
    """Verify two notifications are created when user and restaurant are different recipients."""
    order = place_order(restaurant_id=5)  
    before = len(get_notifications_for_order(order["id"]))
    change_status(order, "PREPARING")
    after = len(get_notifications_for_order(order["id"]))
    assert after == before + 2


def test_no_status_change_notification_on_invalid_transition():
    """Verify no notification is created when an invalid status transition is rejected."""
    order = place_order()
    before = len(get_notifications_for_order(order["id"]))
    change_status(order, "DELIVERED")  # invalid — cannot go PENDING -> DELIVERED
    after = len(get_notifications_for_order(order["id"]))
    assert after == before


def test_status_change_content_mentions_new_status():
    """Verify the notification content references the new status."""
    order = place_order()
    change_status(order, "PREPARING")
    notifications = get_notifications_for_order(order["id"])
    status_notifications = [
        n for n in notifications
        if n["notification_type"] == "ORDER_STATUS_CHANGED"
    ]
    assert all("PREPARING" in n["content"] for n in status_notifications)