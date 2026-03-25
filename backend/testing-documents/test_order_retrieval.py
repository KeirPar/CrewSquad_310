from urllib import response
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.order import OrderCreate
from app.helpers.testing_data import TestingData
from app.helpers.user_test_helper import UserTestHelper



successful_status = 200
failed_status = 400
invalid_status = 422
missing_status = 404

client = TestClient(app)
testing_data = TestingData()
user_helper = UserTestHelper(client=client)

def get_auth_headers():
    user_create = user_helper.test_user_create.model_copy()
    user_helper.register_and_login_user(user=user_create)
    return {"Authorization": f"Bearer {user_helper.login_token}"}

headers = get_auth_headers()
# reusable valid cart (same pattern as test_order.py)
def make_order_create():
    return OrderCreate(
        user_id=testing_data.customer.id,
        cart=testing_data.cart
    ).model_dump()

def test_get_order_status():
    """Verify that retrieving an order returns a 200 response."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status

def test_get_order_status_has_order_and_payment():
    """Verify the response contains both the order and payment."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert "order" in response.json()
    assert "payment" in response.json()

def test_get_order_status_reflects_payment_decision():
    """Verify the order status updates correctly after a payment decision."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    client.post(f"/payments/{order_id}", json={"decision": "ACCEPTED"}, headers=headers)
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert response.json()["order"]["status"] == "PREPARING"
    assert response.json()["payment"]["status"] == "ACCEPTED"

def test_get_order_status_reflects_rejection():
    """Verify the order status updates correctly after a rejection."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    client.post(f"/payments/{order_id}", json={"decision": "REJECTED", "reason": "Too busy"}, headers=headers)
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert response.json()["order"]["status"] == "CANCELLED"
    assert response.json()["payment"]["status"] == "REJECTED"

def test_get_order_nonexistent():
    """Verify that retrieving a non-existent order returns 404."""
    response = client.get("/orders/99999", headers=headers)
    assert response.status_code == missing_status