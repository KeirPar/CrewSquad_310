from urllib import response
from fastapi.testclient import TestClient
from app.main import app

successful_status = 200
failed_status = 400
invalid_status = 422
missing_status = 404

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

def test_get_order_status():
    """Verify that retrieving an order returns a 200 response."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status

def test_get_order_status_has_order_and_payment():
    """Verify the response contains both the order and payment."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert "order" in response.json()
    assert "payment" in response.json()

def test_get_order_status_reflects_payment_decision():
    """Verify the order status updates correctly after a payment decision."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    client.post(f"/payments/{order_id}", json={"decision": "ACCEPTED"})
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert response.json()["order"]["status"] == "PREPARING"
    assert response.json()["payment"]["status"] == "ACCEPTED"

def test_get_order_status_reflects_rejection():
    """Verify the order status updates correctly after a rejection."""
    order_id = client.post("/orders", json=make_cart()).json()["id"]
    client.post(f"/payments/{order_id}", json={"decision": "REJECTED", "reason": "Too busy"})
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert response.json()["order"]["status"] == "CANCELLED"
    assert response.json()["payment"]["status"] == "REJECTED"

def test_get_order_nonexistent():
    """Verify that retrieving a non-existent order returns 404."""
    response = client.get("/orders/99999")
    assert response.status_code == missing_status