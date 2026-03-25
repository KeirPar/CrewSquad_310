from fastapi.testclient import TestClient
from app.main import app
from app.helpers.testing_data import TestingData
from app.helpers.user_test_helper import UserTestHelper
from app.schemas.user import User, UserCreate
from app.schemas.order import Order, OrderCreate
from app.schemas.cart import Cart
from app.schemas.menu_item import MenuItem
from app.packages.geo.coordinate import Coordinate

client = TestClient(app)
testing_data = TestingData()
user_test_helper = UserTestHelper(client)

successful_status = 200
failed_status = 400
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
        address="NEWADDRESS"
    )
    
    user_update_response = client.post("/user/update", json=updated_user_data.model_dump(), headers={"Authorization": f"Bearer {user_test_helper.login_token}"})

    #   Test if the user address field is updaed
    current_user: User = user_test_helper.get_current_user()
    assert current_user.address == updated_user_data.address

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