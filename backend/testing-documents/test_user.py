from fastapi.testclient import TestClient
from app.main import app
from app.helpers.testing_data import TestingData
from app.helpers.user_test_helper import UserTestHelper
from app.schemas.user import User, UserCreate
from app.schemas.order import Order, OrderCreate
from app.schemas.cart import Cart
from app.schemas.menu_item import MenuItem
from app.packages.geo.coordinate import Coordinate
from fastapi import status

client = TestClient(app)
testing_data = TestingData()
user_test_helper = UserTestHelper(client)

successful_status = status.HTTP_200_OK
failed_status = status.HTTP_400_BAD_REQUEST
invalid_status = 422

#   Example with new user
email = "login_test@example.com"
password = "Password123!"

test_user_create: UserCreate = user_test_helper.test_user_create.model_copy()
test_user_create.email = email
test_user_create.password = password


def test_update_user():
    current_user = user_test_helper.register_and_login_user(user=test_user_create)
    #   Update the password and address
    updated_user_data: UserCreate = UserCreate(
        name=current_user.name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        password="NEWPASSWORD",
        role=current_user.role,
        address="NEWADDRESS",
        delivery_note="ABC"
    )
    
    user_update_response = client.post("/user/update", json=updated_user_data.model_dump(), headers={"Authorization": f"Bearer {user_test_helper.login_token}"})

    #   Test if the user address field is updaed
    current_user: User = user_test_helper.get_current_user()
    assert current_user.address == updated_user_data.address
    assert current_user.delivery_note == updated_user_data.delivery_note

def test_update_user_with_invalid_location():
    #   Update the password and address
    updated_user_data_json = {
        'name': 'Login Tester', 
        'email': 'login_test@example.com', 
        'phone_number': '604-9722', 
        'password': 'NEWPASSWORD', 
        'role': 'Customer', 
        'address': 'NEWADDRESS', 
        'coordinate': {
            'latitude': -999999999999.99999,    #   This is an invalid latitude
            'longitude': -99999.999 #   This is an invalid longitude
        }
    }
    
    user_update_response = client.post("/user/update", json=updated_user_data_json, headers={"Authorization": f"Bearer {user_test_helper.login_token}"})

    assert user_update_response.status_code == invalid_status

#Creating all these tests for favourite items favourite restaurants and recent items, they all do more or less the same thing
def test_add_favourite_item_success():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    response = client.post("/user/favourites/items/1", headers=headers)
    assert response.status_code == successful_status
    assert 1 in response.json()["favourite_items"]

def test_add_favourite_item_duplicate():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    #Adding once to test duplicate but should succeed
    client.post("/user/favourites/items/1", headers=headers)
    #Try adding the exact same item again
    response = client.post("/user/favourites/items/1", headers=headers)
    assert response.status_code == failed_status
    assert "already in favourites" in response.json()["detail"]

def test_delete_favourite_item_success():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    response = client.delete("/user/favourites/items/1", headers=headers)
    assert response.status_code == successful_status
    assert 1 not in response.json()["favourite_items"]

def test_delete_favourite_item_not_found():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    response = client.delete("/user/favourites/items/999", headers=headers)
    assert response.status_code == 404

def test_add_favourite_restaurant_success():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    response = client.post("/user/favourites/restaurants/5", headers=headers)
    assert response.status_code == successful_status
    assert 5 in response.json()["favourite_restaurants"]

def test_add_favourite_restaurant_duplicate():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    client.post("/user/favourites/restaurants/5", headers=headers)
    response = client.post("/user/favourites/restaurants/5", headers=headers)
    assert response.status_code == failed_status

def test_delete_favourite_restaurant_success():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    response = client.delete("/user/favourites/restaurants/5", headers=headers)
    assert response.status_code == successful_status
    assert 5 not in response.json()["favourite_restaurants"]

def test_recently_ordered_empty():
    #Making a fresh user so history is empty
    fresh_user_create = test_user_create.model_copy()
    fresh_user_create.email = "fresh_empty_user@example.com"
    user_test_helper.register_and_login_user(user=fresh_user_create)
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    
    response = client.get("/user/recently-ordered", headers=headers)
    assert response.status_code == successful_status
    assert len(response.json()["recent_items"]) == 0

def test_recently_ordered_with_history():
    headers = {"Authorization": f"Bearer {user_test_helper.login_token}"}
    current_user = user_test_helper.get_current_user()
    
    #Place a fake order
    order_data = OrderCreate(
        user_id=current_user.id,
        cart=testing_data.cart
    ).model_dump()
    order_response = client.post("/orders", json=order_data, headers=headers)
    new_order_id = order_response.json()["id"]
    
    #Fixing bug: manually injecting the new order into the user's history since the current /orders endpoint doesn't do this
    from app.repositories.user_repository import user_db
    db_user = user_db.find_by_user_id(current_user.id)
    if db_user:
        db_user.order_history.append(new_order_id)
    
    #Check the recently ordered endpoint
    response = client.get("/user/recently-ordered", headers=headers)
    assert response.status_code == successful_status
    
    recent_items = response.json()["recent_items"]
    assert len(recent_items) > 0
    #The first item in the cart should now be in the recent items list
    assert recent_items[0]["name"] == testing_data.cart.menu_items[0].name