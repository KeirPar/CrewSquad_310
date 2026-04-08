from fastapi.testclient import TestClient
from app.main import app
from app.helpers.testing_data import TestingData
from app.helpers.user_test_helper import UserTestHelper
from app.packages.geo.coordinate import Coordinate
from app.schemas.user import UserCreate
from datetime import datetime, timezone, timedelta
import pytest

successful_status = 200
created_status = 201
failed_status = 400
missing_status = 404

client = TestClient(app)
testing_data = TestingData()
user_helper = UserTestHelper(client=client)


def get_auth_headers():
    from app.schemas.user import UserCreate
    from app.packages.geo.coordinate import Coordinate
    email = "scheduled_test@example.com"
    password = "Password123!"
    # Register — ignore if already exists
    client.post("/auth/register", json={
        "name": "Scheduled Tester",
        "email": email,
        "phone_number": "604-111-2222",
        "password": password,
        "role": "Customer",
        "address": "123 Near St",
        "coordinate": {"latitude": 49.8820, "longitude": -119.4950}
    })
    # Login using form data — matches OAuth2PasswordRequestForm
    login_response = client.post(
        "/auth/login",
        data={"username": email, "password": password}
    )
    token = login_response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture(autouse=True)
def auth_headers_fixture():
    global headers
    headers = get_auth_headers()


def get_current_user_id() -> int:
    response = client.get("/auth/me", headers=headers)
    return response.json()["id"]


def future_time(hours_ahead: float = 5) -> str:
    """Returns a timezone-aware datetime string hours_ahead from now."""
    return (datetime.now(timezone.utc) + timedelta(hours=hours_ahead)).isoformat()


def past_time() -> str:
    """Returns a datetime string in the past."""
    return (datetime.now(timezone.utc) - timedelta(hours=1)).isoformat()


def make_scheduled_order_body(hours_ahead: float = 5):
    """Builds a valid scheduled order request body."""
    safe_cart = testing_data.cart.model_dump()
    
    for item in safe_cart.get("menu_items", []): #had to change this, this pr was merged before my changes to the order repository went up
        item["restaurant_id"] = 1               #again just rewriting the restaurant_id and id of the menu item to match the new order repository and orders.json
        item["id"] = 1

    return {
        "cart": safe_cart,
        "scheduled_time": future_time(hours_ahead)
    }


def place_scheduled_order(hours_ahead: float = 5):
    """Places a valid scheduled order and returns the response."""
    return client.post(
        "/scheduled-orders",
        json=make_scheduled_order_body(hours_ahead),
        headers=headers
    )


# =====================================================================
# FR1: Customer can place a scheduled order for a future time
# =====================================================================

def test_place_scheduled_order_returns_201():
    """Verify that placing a valid scheduled order returns 201."""
    response = place_scheduled_order()

    assert response.status_code == created_status, f"API rejected the order! Reason: {response.text}"

    assert response.status_code == created_status


def test_place_scheduled_order_has_required_fields():
    """Verify the response contains all required fields."""
    response = place_scheduled_order()
    assert response.status_code == created_status
    data = response.json()
    assert "id" in data
    assert "user_id" in data
    assert "order" in data
    assert "scheduled_time" in data
    assert "estimated_delivery_time" in data
    assert "estimated_delivery_minutes" in data
    assert "created_at" in data
    assert "is_cancelled" in data


def test_place_scheduled_order_status_is_scheduled():
    """Verify the underlying order status is SCHEDULED."""
    response = place_scheduled_order()
    assert response.status_code == created_status
    assert response.json()["order"]["status"] == "SCHEDULED"


def test_place_scheduled_order_is_not_cancelled():
    """Verify a newly placed scheduled order is not cancelled."""
    response = place_scheduled_order()
    assert response.status_code == created_status
    assert response.json()["is_cancelled"] == False


def test_place_scheduled_order_user_id_matches_logged_in_user():
    """Verify the user_id on the scheduled order matches the authenticated user."""
    user_id = get_current_user_id()
    response = place_scheduled_order()
    assert response.status_code == created_status
    assert response.json()["user_id"] == user_id


def test_place_scheduled_order_requires_auth():
    """Verify that placing a scheduled order without auth returns 401."""
    fresh_client = TestClient(app)
    response = fresh_client.post("/scheduled-orders", json=make_scheduled_order_body())
    assert response.status_code == 401


# =====================================================================
# FR2: scheduled_time must be in the future and within 24 hours
# =====================================================================

def test_scheduled_time_in_past_rejected():
    """Verify that a scheduled_time in the past returns 400."""
    body = make_scheduled_order_body()
    body["scheduled_time"] = past_time()
    response = client.post("/scheduled-orders", json=body, headers=headers)
    assert response.status_code == failed_status
    assert "future" in response.json()["detail"].lower()


def test_scheduled_time_more_than_24h_ahead_rejected():
    """Verify that a scheduled_time more than 24 hours ahead returns 400."""
    body = make_scheduled_order_body(hours_ahead=25)
    response = client.post("/scheduled-orders", json=body, headers=headers)
    assert response.status_code == failed_status
    assert "24" in response.json()["detail"]


def test_scheduled_time_within_24h_accepted():
    """Verify that a scheduled_time within 24 hours is accepted."""
    response = place_scheduled_order(hours_ahead=12)
    assert response.status_code == created_status


# =====================================================================
# FR3: scheduled_time must allow enough time for delivery
# =====================================================================

def test_estimated_delivery_minutes_is_positive():
    """Verify the estimated delivery minutes is a positive number."""
    response = place_scheduled_order()
    assert response.status_code == created_status
    assert response.json()["estimated_delivery_minutes"] > 0


def test_estimated_delivery_time_is_after_creation():
    """Verify the estimated delivery time is after the order creation time."""
    response = place_scheduled_order()
    assert response.status_code == created_status
    data = response.json()
    created_at = datetime.fromisoformat(data["created_at"])
    estimated = datetime.fromisoformat(data["estimated_delivery_time"])
    assert estimated > created_at


def test_scheduled_time_too_soon_rejected():
    """Verify that a scheduled_time that doesn't allow enough delivery time is rejected."""
    body = make_scheduled_order_body()
    body["scheduled_time"] = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    response = client.post("/scheduled-orders", json=body, headers=headers)
    assert response.status_code == failed_status
    assert "enough time" in response.json()["detail"].lower()


def test_scheduled_time_error_includes_earliest_valid_time():
    """Verify the error message tells the customer the earliest valid scheduled time."""
    body = make_scheduled_order_body()
    body["scheduled_time"] = (datetime.now(timezone.utc) + timedelta(minutes=1)).isoformat()
    response = client.post("/scheduled-orders", json=body, headers=headers)
    assert response.status_code == failed_status
    assert "UTC" in response.json()["detail"]


def test_empty_cart_rejected():
    """Verify that an empty cart returns 400."""
    body = {
        "cart": {"id": 1, "menu_items": []},
        "scheduled_time": future_time(5)
    }
    response = client.post("/scheduled-orders", json=body, headers=headers)
    assert response.status_code == failed_status


def test_mixed_restaurant_cart_rejected():
    """Verify that a cart with items from different restaurants returns 400."""
    body = {
        "cart": {
            "id": 1,
            "menu_items": [
                {
                    "id": 1,
                    "name": "Burger",
                    "description": "Juicy",
                    "price": 10,
                    "image_url": "url",
                    "add_ons": [],
                    "is_available": True,
                    "restaurant_id": 5
                },
                {
                    "id": 2,
                    "name": "Pizza",
                    "description": "Cheesy",
                    "price": 12,
                    "image_url": "url",
                    "add_ons": [],
                    "is_available": True,
                    "restaurant_id": 6
                }
            ]
        },
        "scheduled_time": future_time(5)
    }
    response = client.post("/scheduled-orders", json=body, headers=headers)
    assert response.status_code == failed_status


# =====================================================================
# FR4: Customer can cancel their own scheduled order
# =====================================================================

def test_cancel_scheduled_order_returns_200():
    """Verify that cancelling a scheduled order returns 200."""
    order_id = place_scheduled_order().json()["id"]
    response = client.patch(f"/scheduled-orders/{order_id}/cancel", headers=headers)
    assert response.status_code == successful_status


def test_cancel_scheduled_order_sets_is_cancelled():
    """Verify that cancelling sets is_cancelled to True."""
    order_id = place_scheduled_order().json()["id"]
    response = client.patch(f"/scheduled-orders/{order_id}/cancel", headers=headers)
    assert response.status_code == successful_status
    assert response.json()["is_cancelled"] == True


def test_cancel_scheduled_order_sets_order_status_cancelled():
    """Verify that cancelling updates the underlying order status to CANCELLED."""
    order_id = place_scheduled_order().json()["id"]
    response = client.patch(f"/scheduled-orders/{order_id}/cancel", headers=headers)
    assert response.status_code == successful_status
    assert response.json()["order"]["status"] == "CANCELLED"


def test_cancel_with_reason_stores_reason():
    """Verify that a cancellation reason is stored."""
    order_id = place_scheduled_order().json()["id"]
    response = client.patch(
        f"/scheduled-orders/{order_id}/cancel",
        json={"reason": "Changed my mind"},
        headers=headers
    )
    assert response.status_code == successful_status
    assert response.json()["cancellation_reason"] == "Changed my mind"


def test_cancel_without_reason_succeeds():
    """Verify that cancelling without a reason still works."""
    order_id = place_scheduled_order().json()["id"]
    response = client.patch(f"/scheduled-orders/{order_id}/cancel", headers=headers)
    assert response.status_code == successful_status


def test_cancel_already_cancelled_order_returns_400():
    """Verify that cancelling an already cancelled order returns 400."""
    order_id = place_scheduled_order().json()["id"]
    client.patch(f"/scheduled-orders/{order_id}/cancel", headers=headers)
    response = client.patch(f"/scheduled-orders/{order_id}/cancel", headers=headers)
    assert response.status_code == failed_status
    assert "already been cancelled" in response.json()["detail"].lower()


def test_cancel_nonexistent_order_returns_404():
    """Verify that cancelling a nonexistent order returns 404."""
    response = client.patch("/scheduled-orders/99999/cancel", headers=headers)
    assert response.status_code == missing_status


def test_cancel_requires_auth():
    """Verify that cancelling without auth returns 401."""
    order_id = place_scheduled_order().json()["id"]
    fresh_client = TestClient(app)
    response = fresh_client.patch(f"/scheduled-orders/{order_id}/cancel")
    assert response.status_code == 401


# =====================================================================
# FR5: Customer can retrieve their scheduled orders
# =====================================================================

def test_get_my_scheduled_orders_returns_200():
    """Verify that retrieving all scheduled orders returns 200."""
    response = client.get("/scheduled-orders/my-orders/all", headers=headers)
    assert response.status_code == successful_status


def test_get_my_scheduled_orders_returns_list():
    """Verify that the response is a list."""
    response = client.get("/scheduled-orders/my-orders/all", headers=headers)
    assert response.status_code == successful_status
    assert isinstance(response.json(), list)


def test_get_my_scheduled_orders_includes_placed_order():
    """Verify that a placed scheduled order appears in the user's list."""
    placed = place_scheduled_order().json()
    response = client.get("/scheduled-orders/my-orders/all", headers=headers)
    assert response.status_code == successful_status
    ids = [o["id"] for o in response.json()]
    assert placed["id"] in ids


def test_get_my_scheduled_orders_sorted_by_scheduled_time():
    """Verify that results are sorted by scheduled_time ascending."""
    place_scheduled_order(hours_ahead=10)
    place_scheduled_order(hours_ahead=5)
    response = client.get("/scheduled-orders/my-orders/all", headers=headers)
    orders = response.json()
    if len(orders) > 1:
        times = [o["scheduled_time"] for o in orders]
        assert times == sorted(times)


def test_get_scheduled_order_by_id_returns_200():
    """Verify that retrieving a specific scheduled order returns 200."""
    order_id = place_scheduled_order().json()["id"]
    response = client.get(f"/scheduled-orders/{order_id}", headers=headers)
    assert response.status_code == successful_status


def test_get_scheduled_order_by_id_correct_data():
    """Verify that the retrieved order has the correct ID."""
    order_id = place_scheduled_order().json()["id"]
    response = client.get(f"/scheduled-orders/{order_id}", headers=headers)
    assert response.status_code == successful_status
    assert response.json()["id"] == order_id


def test_get_nonexistent_scheduled_order_returns_404():
    """Verify that retrieving a nonexistent scheduled order returns 404."""
    response = client.get("/scheduled-orders/99999", headers=headers)
    assert response.status_code == missing_status


def test_get_scheduled_order_requires_auth():
    """Verify that retrieving a scheduled order without auth returns 401."""
    order_id = place_scheduled_order().json()["id"]
    fresh_client = TestClient(app)
    response = fresh_client.get(f"/scheduled-orders/{order_id}")
    assert response.status_code == 401