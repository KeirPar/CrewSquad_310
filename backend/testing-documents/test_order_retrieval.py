from urllib import response
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.order import OrderCreate
from app.helpers.testing_data import TestingData
from app.helpers.user_test_helper import UserTestHelper
from fastapi import status


successful_status = status.HTTP_200_OK
failed_status = status.HTTP_400_BAD_REQUEST
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
    """Verify that retrieving an order returns a status.HTTP_200_OK response."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status

def test_get_order_status_has_correct_status():
    """Verify the response contains the correct order status."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert "order status" in response.json()

def test_get_order_status_reflects_payment_decision():
    """Verify the order status updates correctly after a payment decision."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    client.post(f"/payments/{order_id}", json={"decision": "ACCEPTED"}, headers=headers)
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert response.json()["order status"] == "PREPARING"

def test_get_order_status_reflects_rejection():
    """Verify the order status updates correctly after a rejection."""
    order_id = client.post("/orders", json=make_order_create()).json()["id"]
    client.post(f"/payments/{order_id}", json={"decision": "REJECTED", "reason": "Too busy"}, headers=headers)
    response = client.get(f"/orders/{order_id}")
    assert response.status_code == successful_status
    assert response.json()["order status"] == "CANCELLED"

def test_get_order_nonexistent():
    """Verify that retrieving a non-existent order returns 404."""
    response = client.get("/orders/99999", headers=headers)
    assert response.status_code == missing_status