from fastapi.testclient import TestClient
from app.main import app
from app.repositories.notification_repo import notification_db
from fastapi import status
import random

successful_status = status.HTTP_200_OK
failed_status = status.HTTP_400_BAD_REQUEST

client = TestClient(app)


def make_cart(restaurant_id=5):

    random_num = random.randint(1, 1000) #random number for random email
    res = client.post("/auth/register", json={ #make fake user
        "name": "Notification User",
        "email": f"notif_user_{random_num}@example.com",
        "password": "Password123!",
        "phone_number": "676-676-7676",
        "role": "Customer",
        "address": "123 Test St"
    })

    real_id = res.json().get("id", None) #get id from fake user

    return {
        "user_id": real_id,
        "cart": {
        "id": 1, #had to add some fields (userID, cart, id inside of menu list), tests were not running without them.
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


def test_notification_created_on_order():
    """Verify that placing an order creates a notification in the repository."""
    before = len(notification_db.get_all())
    response = client.post("/orders", json=make_cart())
    after = len(notification_db.get_all())
    assert after == before + 1


def test_notification_type_is_new_order():
    """Verify the notification type is NEW_ORDER."""
    client.post("/orders", json=make_cart())
    notification = client.get("/notifications").json()["notifications"][-1]
    assert notification["notification_type"] == "NEW_ORDER"


def test_notification_order_id_matches():
    """Verify the notification stores the correct order ID."""
    response = client.post("/orders", json=make_cart())
    order_id = response.json()["id"]
    notification = client.get("/notifications").json()["notifications"][-1]
    assert notification["order_id"] == order_id


def test_notification_restaurant_id_matches():
    """Verify the notification stores the correct restaurant ID."""
    response = client.post("/orders", json=make_cart(restaurant_id=5))
    notification = client.get("/notifications").json()["notifications"][-1]
    assert notification["restaurant_id"] == 5


def test_notification_has_timestamp():
    """Verify the notification has a timestamp."""
    client.post("/orders", json=make_cart())
    notification = client.get("/notifications").json()["notifications"][-1]
    assert notification["timestamp"] is not None


def test_notification_is_unread_on_creation():
    """Verify the notification starts as unread."""
    client.post("/orders", json=make_cart())
    notification = client.get("/notifications").json()["notifications"][-1]
    assert notification["is_read"] == False


def test_notification_has_content():
    """Verify the notification has a non-empty content message."""
    client.post("/orders", json=make_cart())
    notification = client.get("/notifications").json()["notifications"][-1]
    assert notification["content"] is not None
    assert len(notification["content"]) > 0


def test_notification_has_valid_id():
    """Verify the notification has a positive integer ID."""
    client.post("/orders", json=make_cart())
    notification = client.get("/notifications").json()["notifications"][-1]
    assert isinstance(notification["id"], int)
    assert notification["id"] > 0


def test_no_notification_on_empty_cart():
    """Verify that a failed order does not create a notification."""
    before = len(client.get("/notifications").json()["notifications"])
    client.post("/orders", json={"menu_items": []})
    after = len(client.get("/notifications").json()["notifications"])
    assert after == before


def test_no_notification_on_mixed_restaurant_cart():
    """Verify that a failed order (mixed restaurants) does not create a notification."""
    before = len(client.get("/notifications").json()["notifications"])
    mixed_cart = make_cart()
    mixed_cart["cart"]["menu_items"][1]["restaurant_id"] = 99
    client.post("/orders", json=mixed_cart)
    after = len(client.get("/notifications").json()["notifications"])
    assert after == before


def test_multiple_orders_create_multiple_notifications():
    """Verify that each order creates its own separate notification."""
    before = len(client.get("/notifications").json()["notifications"])
    client.post("/orders", json=make_cart())
    client.post("/orders", json=make_cart())
    after = len(client.get("/notifications").json()["notifications"])
    assert after == before + 2


def test_find_notification_by_order_id():
    """Verify that notifications can be retrieved by order ID."""
    response = client.post("/orders", json=make_cart())
    order_id = response.json()["id"]
    notifications = notification_db.find_by_order_id(order_id)
    assert len(notifications) == 1
    assert notifications[0].order_id == order_id