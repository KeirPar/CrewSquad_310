from fastapi.testclient import TestClient
from app.main import app
from app.helpers.testing_data import TestingData
from app.schemas.user import User
from app.schemas.order import Order, OrderCreate
from app.schemas.cart import Cart
from app.schemas.menu_item import MenuItem
from fastapi import status


client = TestClient(app)

successful_status = status.HTTP_200_OK
failed_status = status.HTTP_400_BAD_REQUEST
invalid_status = 422

testing_data = TestingData()
# reusable valid cart
def make_order_create():
    return OrderCreate(
        user_id=testing_data.customer.id,
        cart=testing_data.cart
    ).model_dump()

def test_create_order_success():
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    data = response.json()
    assert data["restaurant_id"] == 5
    assert len(data["items"]) == 2
    assert data["bill"]["items_subtotal"] == 15
    assert data["delivery_note"] == testing_data.customer.delivery_note


def test_create_order_status_is_pending():
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    assert response.json()["status"] == "PENDING"


def test_create_order_correct_total():
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    assert response.json()["bill"]["items_subtotal"] == 15


def test_create_order_correct_item_count():
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    assert len(response.json()["items"]) == 2


def test_create_order_empty_cart():
    empty_order_create = OrderCreate(
        user_id=testing_data.customer.id,
        cart=Cart(
            id=10,
            menu_items=[]
        )
    )
    response = client.post("/orders", json=empty_order_create.model_dump())
    assert response.status_code == failed_status  # ValueError: No items in Cart


def test_create_order_mixed_restaurants():
    order_create = OrderCreate(
        user_id=testing_data.customer.id,
        cart=Cart(
            id=10,
            menu_items=[menu_item.model_copy() for menu_item in testing_data.cart.menu_items]
        )
    )
    order_create.cart.menu_items[0].restaurant_id = 99  # different restaurant
    response = client.post("/orders", json=order_create.model_dump())
    assert response.status_code == failed_status  # ValueError: Pick Items from one restaurant only


def test_create_order_has_required_fields():
    response = client.post("/orders", json=make_order_create())
    assert response.status_code == successful_status
    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert "status" in data
    assert "restaurant_id" in data
    assert "items" in data
    assert "bill" in data
    assert "delivery_note" in data
    assert "delivery_address" in data
    assert "coordinate" in data

def test_create_order_invalid_menu_items():
    response = client.post("/orders", json={"menu_items": "not a list"})
    assert response.status_code == invalid_status

def test_get_orders():
    #   Example with new user
    email = "login_test@example.com"
    password = "Password123!"
    
    client.post(
        "/auth/register",
        json={
            "name": "Login Tester",
            "email": email,
            "phone_number": "604-9722",
            "password": password,
            "role": "Customer",
            "address": "789 Test Ave"
        }
    )

    #   Trying login
    login_response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )

    assert login_response.status_code == status.HTTP_200_OK
    login_token = login_response.json()["access_token"]

    #   Get Current User
    get_user_response = client.get("/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    current_user: User = User(**get_user_response.json())

    #   Get all orders
    get_orders_response = client.get("/orders", headers={"Authorization": f"Bearer {login_token}"})
    assert get_orders_response.status_code == status.HTTP_200_OK
    assert get_orders_response.json() == []
    
    #   Order something
    create_order_response = client.post("/orders", json={ "user_id": current_user.id, "cart": testing_data.cart.model_dump() })

    #   Get all orders
    get_orders_response = client.get("/orders", headers={"Authorization": f"Bearer {login_token}"})
    assert get_orders_response.status_code == status.HTTP_200_OK
    retrieved_orders: list[Order] = [Order(**order) for order in get_orders_response.json()]
    assert retrieved_orders[0].items == testing_data.cart.menu_items