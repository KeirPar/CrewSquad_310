from fastapi.testclient import TestClient
from app.main import app
from app.helpers.testing_data import TestingData

client = TestClient(app)

successful_status = 200
failed_status = 400
invalid_status = 422

testing_data = TestingData()
# reusable valid cart
def make_cart():
    return testing_data.cart.model_dump()

def test_create_order_success():
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    data = response.json()
    assert data["restaurant_id"] == 5
    assert len(data["items"]) == 2
    assert data["bill"]["items_subtotal"] == 15


def test_create_order_status_is_pending():
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    assert response.json()["status"] == "PENDING"


def test_create_order_correct_total():
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    assert response.json()["bill"]["items_subtotal"] == 15


def test_create_order_correct_item_count():
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    assert len(response.json()["items"]) == 2


def test_create_order_empty_cart():
    empty_cart = {"id": 0,"menu_items": []}
    response = client.post("/orders", json=empty_cart)
    assert response.status_code == failed_status  # ValueError: No items in Cart


def test_create_order_mixed_restaurants():
    mixed_cart = make_cart()
    mixed_cart["menu_items"][1]["restaurant_id"] = 99  # different restaurant
    response = client.post("/orders", json=mixed_cart)
    assert response.status_code == failed_status  # ValueError: Pick Items from one restaurant only


def test_create_order_has_required_fields():
    response = client.post("/orders", json=make_cart())
    assert response.status_code == successful_status
    data = response.json()
    assert "id" in data
    assert "created_at" in data
    assert "status" in data
    assert "restaurant_id" in data
    assert "items" in data
    assert "bill" in data

def test_create_order_invalid_menu_items():
    response = client.post("/orders", json={"menu_items": "not a list"})
    assert response.status_code == invalid_status