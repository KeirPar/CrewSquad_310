from urllib import response

from fastapi.testclient import TestClient
from app.main import app
from app.schemas.payment import PaymentStatus
from app.schemas.order import OrderCreate
from app.helpers.testing_data import TestingData
from app.schemas.bill import Bill
from app.schemas.cart import Cart
from fastapi import status

successful_status = status.HTTP_200_OK
failed_status = status.HTTP_400_BAD_REQUEST
invalid_status = 422
missing_status = 404

client = TestClient(app)
testing_data = TestingData()

# reusable valid cart (same pattern as test_order.py)
def make_order_create():
    return OrderCreate(
        user_id=testing_data.customer.id,
        cart=testing_data.cart
    ).model_dump()


def test_payment_attempt_exists_in_response():
    """Verify that placing an order returns a payment attempt in the response."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    assert "payment" in response.json()

def test_payment_attempt_status_is_pending():
    """Verify the payment attempt always starts with PENDING status."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert payment["status"] == PaymentStatus.PENDING

def test_payment_attempt_amount_matches_order_total():
    """Verify the payment amount matches the order's total_amount."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    data = response.json()
    assert data["payment"]["amount"] == Bill(**data["bill"]).total

def test_payment_attempt_order_id_matches_order():
    """Verify the payment attempt is linked to the correct order via order_id."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    data = response.json()
    assert data["payment"]["order_id"] == data["id"]

def test_payment_attempt_has_required_fields():
    """Verify the payment attempt contains all required fields."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert "id" in payment
    assert "order_id" in payment
    assert "amount" in payment
    assert "status" in payment
    assert "created_at" in payment

def test_payment_attempt_has_valid_id():
    """Verify the payment attempt has a positive integer ID."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert isinstance(payment["id"], int)
    assert payment["id"] > 0

def test_payment_attempt_has_timestamp():
    """Verify the payment attempt has a created_at timestamp."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    payment = response.json()["payment"]
    assert payment["created_at"] is not None

def test_payment_attempt_correct_amount_single_item():
    """Verify the payment amount is correct for a single item cart."""
    cart_id = 1
    testing_data.customer.cart.append(cart_id)
    single_item_cart = {
        "user_id": testing_data.customer.id,
        "cart": {
            "id": cart_id,
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
    }
    response = client.post("/orders", json=single_item_cart)
    assert response.status_code == successful_status
    data = response.json()
    assert round(data["payment"]["amount"], 2) == 24.39

def test_no_payment_attempt_on_empty_cart():
    """Verify that a failed order (empty cart) does not create a payment attempt."""
    
    empty_order_create = OrderCreate(
        user_id=testing_data.customer.id,
        cart=Cart(
            id=10,
            menu_items=[]
        )
    )
    response = client.post("/orders", json=empty_order_create.model_dump())
    assert response.status_code == failed_status
    assert "payment" not in response.json()

def test_no_payment_attempt_on_mixed_restaurant_cart():
    """Verify that a failed order (mixed restaurants) does not create a payment attempt."""
    order_create = OrderCreate(
        user_id=testing_data.customer.id,
        cart=Cart(
            id=10,
            menu_items=[menu_item.model_copy() for menu_item in testing_data.cart.menu_items]
        )
    )
    order_create.cart.menu_items[0].restaurant_id = 99  # different restaurant
    response = client.post("/orders", json=order_create.model_dump())
    assert response.status_code == failed_status
    assert "payment" not in response.json()

def test_order_fields_still_intact_after_payment_added():
    """Verify that adding payment to response does not break any existing order fields."""
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert "status" in data
    assert "restaurant_id" in data
    assert "items" in data
    assert "bill" in data
    assert data["status"] == "PENDING"
    assert data["bill"]["items_subtotal"] == 15
    assert data["restaurant_id"] == 5