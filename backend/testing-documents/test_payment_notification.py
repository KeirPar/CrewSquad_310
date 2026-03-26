from fastapi.testclient import TestClient
from app.main import app
from app.helpers.testing_data import TestingData
from app.helpers.user_test_helper import UserTestHelper
from app.schemas.order import OrderCreate
from app.packages.geo.coordinate import Coordinate
from fastapi import status

successful_status = status.HTTP_200_OK
missing_status = 404

client = TestClient(app)
testing_data = TestingData()

user_helper = UserTestHelper(client=client)


def get_auth_headers():
    user_create = user_helper.test_user_create.model_copy()
    user_helper.register_and_login_user(user=user_create)
    return {"Authorization": f"Bearer {user_helper.login_token}"}


headers = get_auth_headers()


def get_current_user_id() -> int:
    """Gets the current logged in user ID fresh each call."""
    response = client.get("/auth/me", headers=headers)
    return response.json()["id"]


def make_order_create():
    user_id = get_current_user_id()
    return OrderCreate(
        user_id=user_id,
        cart=testing_data.cart
    ).model_dump()


def get_notifications_for_recipient(recipient_id):
    return client.get(f"/notifications/recipient/{recipient_id}").json()["notifications"]


def place_order():
    return client.post("/orders", json=make_order_create()).json()


def test_payment_accepted_creates_notification():
    """Verify that accepting a payment creates a PAYMENT_ACCEPTED notification."""
    user_id = get_current_user_id()
    order = place_order()
    before = len(get_notifications_for_recipient(user_id))
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    after = len(get_notifications_for_recipient(user_id))
    assert after > before


def test_payment_accepted_notification_type():
    """Verify the notification type is PAYMENT_ACCEPTED."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    payment_notifications = [
        n for n in notifications
        if n["notification_type"] == "PAYMENT_ACCEPTED"
        and n["order_id"] == order["id"]
    ]
    assert len(payment_notifications) > 0


def test_payment_rejected_creates_notification():
    """Verify that rejecting a payment creates a PAYMENT_REJECTED notification."""
    user_id = get_current_user_id()
    order = place_order()
    before = len(get_notifications_for_recipient(user_id))
    client.post(f"/payments/{order['id']}", json={
        "decision": "REJECTED",
        "reason": "Out of stock"
    }, headers=headers)
    after = len(get_notifications_for_recipient(user_id))
    assert after > before


def test_payment_rejected_notification_type():
    """Verify the notification type is PAYMENT_REJECTED."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={
        "decision": "REJECTED",
        "reason": "Too busy"
    }, headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    payment_notifications = [
        n for n in notifications
        if n["notification_type"] == "PAYMENT_REJECTED"
        and n["order_id"] == order["id"]
    ]
    assert len(payment_notifications) > 0


def test_payment_notification_directed_at_user():
    """Verify the payment notification recipient is the user who placed the order."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    matching = [
        n for n in notifications
        if n["notification_type"] == "PAYMENT_ACCEPTED"
        and n["order_id"] == order["id"]
    ]
    assert all(n["recipient_id"] == user_id for n in matching)


def test_payment_notification_has_timestamp():
    """Verify the payment notification has a timestamp."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    matching = [
        n for n in notifications
        if n["notification_type"] == "PAYMENT_ACCEPTED"
        and n["order_id"] == order["id"]
    ]
    assert all(n["timestamp"] is not None for n in matching)


def test_payment_notification_is_unread():
    """Verify the payment notification starts as unread."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    matching = [
        n for n in notifications
        if n["notification_type"] == "PAYMENT_ACCEPTED"
        and n["order_id"] == order["id"]
    ]
    assert all(n["is_read"] == False for n in matching)


def test_payment_notification_has_content():
    """Verify the payment notification has a non-empty content message."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    matching = [
        n for n in notifications
        if n["notification_type"] == "PAYMENT_ACCEPTED"
        and n["order_id"] == order["id"]
    ]
    assert all(len(n["content"]) > 0 for n in matching)


def test_payment_notification_has_correct_order_id():
    """Verify the payment notification stores the correct order ID."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    matching = [
        n for n in notifications
        if n["notification_type"] == "PAYMENT_ACCEPTED"
        and n["order_id"] == order["id"]
    ]
    assert len(matching) > 0
    assert all(n["order_id"] == order["id"] for n in matching)


def test_simulate_payment_creates_notification():
    """Verify that simulating a payment creates a payment notification."""
    user_id = get_current_user_id()
    order = place_order()
    before = len(get_notifications_for_recipient(user_id))
    client.post(f"/payments/{order['id']}/simulate", headers=headers)
    after = len(get_notifications_for_recipient(user_id))
    assert after > before


def test_simulate_payment_notification_type_is_accepted_or_rejected():
    """Verify the simulated payment notification type is PAYMENT_ACCEPTED or PAYMENT_REJECTED."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}/simulate", headers=headers)
    notifications = get_notifications_for_recipient(user_id)
    matching = [
        n for n in notifications
        if n["notification_type"] in ["PAYMENT_ACCEPTED", "PAYMENT_REJECTED"]
        and n["order_id"] == order["id"]
    ]
    assert len(matching) > 0


def test_payment_notification_appears_in_order_timeline():
    """Verify the payment notification appears in the order timeline for the user."""
    user_id = get_current_user_id()
    order = place_order()
    client.post(f"/payments/{order['id']}", json={"decision": "ACCEPTED"}, headers=headers)
    response = client.get(f"/notifications/order/{order['id']}/recipient/{user_id}")
    assert response.status_code == successful_status
    timeline = response.json()["timeline"]
    payment_notifications = [
        n for n in timeline if n["notification_type"] == "PAYMENT_ACCEPTED"
    ]
    assert len(payment_notifications) > 0