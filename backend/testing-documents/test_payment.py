from fastapi.testclient import TestClient
from app.main import app
from app.schemas.payment import PaymentStatus

successful_status = 200
failed_status = 400
invalid_status = 422

client = TestClient(app)

# reusable valid cart (same pattern as test_order.py)
def make_cart(restaurant_id=5):
    return {
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


def test_payment_attempt_exists_in_response():
    """Verify that placing an order returns a payment attempt in the response."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    assert "payment" in response.json()

def test_payment_attempt_status_is_pending():
    """Verify the payment attempt always starts with PENDING status."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert payment["status"] == PaymentStatus.PENDING

def test_payment_attempt_amount_matches_order_total():
    """Verify the payment amount matches the order's total_amount."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    data = response.json()
    assert data["payment"]["amount"] == data["total_amount"]

def test_payment_attempt_order_id_matches_order():
    """Verify the payment attempt is linked to the correct order via order_id."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    data = response.json()
    assert data["payment"]["order_id"] == data["id"]

def test_payment_attempt_has_required_fields():
    """Verify the payment attempt contains all required fields."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert "id" in payment
    assert "order_id" in payment
    assert "amount" in payment
    assert "status" in payment
    assert "created_at" in payment

def test_payment_attempt_has_valid_id():
    """Verify the payment attempt has a positive integer ID."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert isinstance(payment["id"], int)
    assert payment["id"] > 0

def test_payment_attempt_has_timestamp():
    """Verify the payment attempt has a created_at timestamp."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert payment["created_at"] is not None

def test_payment_attempt_correct_amount_single_item():
    """Verify the payment amount is correct for a single item cart."""
    single_item_cart = {
        "menu_items": [
            {
                "id": 1,
                "name": "Pizza",
                "description": "Cheesy",
                "price": 20.0,
                "image_url": "pizza.jpg",
                "add_ons": [],
                "is_available": True,
                "restaurant_id": 5
            }
        ]
    }
    response = client.post("/orders", json=single_item_cart)
    assert response.status_code == successful_status
    data = response.json()
    assert data["payment"]["amount"] == 20.0

def test_no_payment_attempt_on_empty_cart():
    """Verify that a failed order (empty cart) does not create a payment attempt."""
    response = client.post("/orders", json={"menu_items": []})
    assert response.status_code == failed_status
    assert "payment" not in response.json()

def test_no_payment_attempt_on_mixed_restaurant_cart():
    """Verify that a failed order (mixed restaurants) does not create a payment attempt."""
    mixed_cart = make_cart()
    mixed_cart["menu_items"][1]["restaurant_id"] = 99
    response = client.post("/orders", json=mixed_cart)
    assert response.status_code == failed_status
    assert "payment" not in response.json()

def test_order_fields_still_intact_after_payment_added():
    """Verify that adding payment to response does not break any existing order fields."""
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert "status" in data
    assert "restaurant_id" in data
    assert "items" in data
    assert "total_amount" in data
    assert data["status"] == "PENDING"
    assert data["total_amount"] == 15.0
    assert data["restaurant_id"] == 5