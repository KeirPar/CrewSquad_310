from fastapi.testclient import TestClient
from app.main import app
from fastapi import status

successful_status = status.HTTP_200_OK
missing_status = 404

client = TestClient(app)


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
    return client.post("/orders", json=make_cart(restaurant_id)).json()


def build_order_body(order: dict) -> dict:
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


def change_status(order, new_status):
    return client.patch(
        f"/orders/{order['id']}/status",
        params={"new_status": new_status},
        json=build_order_body(order)
    )


def get_timeline(order_id, recipient_id):
    return client.get(f"/notifications/order/{order_id}/recipient/{recipient_id}")


def test_timeline_endpoint():
    """Verify the timeline endpoint returns a successful response for a valid order and recipient."""
    order = place_order()
    response = get_timeline(order["id"], 5)
    assert response.status_code == successful_status


def test_timeline_contains_timeline_key():
    """Verify the response contains a timeline list."""
    order = place_order()
    response = get_timeline(order["id"], 5)
    assert response.status_code == successful_status
    assert "timeline" in response.json()


def test_timeline_contains_order_id():
    """Verify the response includes the order_id."""
    order = place_order()
    response = get_timeline(order["id"], 5)
    assert response.json()["order_id"] == order["id"]


def test_timeline_contains_recipient_id():
    """Verify the response includes the recipient_id."""
    order = place_order()
    response = get_timeline(order["id"], 5)
    assert response.json()["recipient_id"] == 5


def test_timeline_starts_with_new_order_notification():
    """Verify the first event in the timeline is a NEW_ORDER notification."""
    order = place_order()
    response = get_timeline(order["id"], 5)
    timeline = response.json()["timeline"]
    assert len(timeline) >= 1
    assert timeline[0]["notification_type"] == "NEW_ORDER"


def test_timeline_grows_after_status_change():
    """Verify the timeline grows when an order status changes."""
    order = place_order(restaurant_id=5)
    before = len(get_timeline(order["id"], 5).json()["timeline"])
    change_status(order, "PREPARING")
    after = len(get_timeline(order["id"], 5).json()["timeline"])
    assert after > before


def test_timeline_is_chronologically_ordered():
    """Verify the timeline events are sorted oldest to newest."""
    order = place_order(restaurant_id=5)
    change_status(order, "PREPARING")
    timeline = get_timeline(order["id"], 5).json()["timeline"]
    timestamps = [n["timestamp"] for n in timeline]
    assert timestamps == sorted(timestamps)


def test_timeline_only_shows_notifications_for_recipient():
    """Verify the timeline only contains notifications for the specified recipient."""
    order = place_order(restaurant_id=5)
    change_status(order, "PREPARING")
    # Get timeline for restaurant (id=5)
    timeline = get_timeline(order["id"], 5).json()["timeline"]
    assert all(n["recipient_id"] == 5 for n in timeline)


def test_timeline_only_shows_notifications_for_order():
    """Verify the timeline only contains notifications for the specified order."""
    order = place_order(restaurant_id=5)
    timeline = get_timeline(order["id"], 5).json()["timeline"]
    assert all(n["order_id"] == order["id"] for n in timeline)


def test_timeline_for_manager_after_status_change():
    """Verify the manager (id=2) gets a status change notification in their timeline."""
    order = place_order(restaurant_id=5)
    change_status(order, "PREPARING")
    # Manager has id=2 from the stub
    response = get_timeline(order["id"], 2)
    assert response.status_code == successful_status
    timeline = response.json()["timeline"]
    assert any(n["notification_type"] == "ORDER_STATUS_CHANGED" for n in timeline)


def test_timeline_shows_multiple_status_changes():
    """Verify the timeline records every status change in order."""
    order = place_order(restaurant_id=5)
    change_status(order, "PREPARING")

    # Update order body to reflect new status for second change
    updated_body = build_order_body(order)
    updated_body["status"] = "PREPARING"
    client.patch(
        f"/orders/{order['id']}/status",
        params={"new_status": "DELIVERED"},
        json=updated_body
    )

    timeline = get_timeline(order["id"], 5).json()["timeline"]
    status_change_notifications = [
        n for n in timeline if n["notification_type"] == "ORDER_STATUS_CHANGED"
    ]
    assert len(status_change_notifications) >= 2


def test_timeline_returns_404_for_nonexistent_order():
    """Verify the timeline returns 404 when no notifications exist for the order."""
    response = get_timeline(99999, 1)
    assert response.status_code == missing_status


def test_timeline_returns_404_for_wrong_recipient():
    """Verify the timeline returns 404 when the recipient has no notifications for this order."""
    order = place_order(restaurant_id=5)
    # recipient_id=99 has no notifications for this order
    response = get_timeline(order["id"], 99)
    assert response.status_code == missing_status


def test_different_orders_have_separate_timelines():
    """Verify two different orders have independent timelines."""
    order1 = place_order(restaurant_id=5)
    order2 = place_order(restaurant_id=5)
    timeline1 = get_timeline(order1["id"], 5).json()["timeline"]
    timeline2 = get_timeline(order2["id"], 5).json()["timeline"]
    # Each timeline should only contain its own order's notifications
    assert all(n["order_id"] == order1["id"] for n in timeline1)
    assert all(n["order_id"] == order2["id"] for n in timeline2)