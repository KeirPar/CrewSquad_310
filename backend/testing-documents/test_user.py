from fastapi.testclient import TestClient
from app.main import app
from app.helpers.testing_data import TestingData
from app.schemas.user import User, UserCreate
from app.schemas.order import Order, OrderCreate
from app.schemas.cart import Cart
from app.schemas.menu_item import MenuItem
from app.packages.geo.coordinate import Coordinate

client = TestClient(app)
testing_data = TestingData()

successful_status = 200
failed_status = 400
invalid_status = 422

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
        "address": "789 Test Ave",
        "coordinate": {
            "latitude": 23,
            "longitude": 3
        }
    }
)

#   Trying login
login_response = client.post(
    "/auth/login",
    json={"email": email, "password": password}
)

assert login_response.status_code == 200
login_token = login_response.json()["access_token"]


def test_update_user():
    #   Get Current User
    get_user_response = client.get("/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    current_user: User = User(**get_user_response.json())
    #   Update the password and address
    updated_user_data: UserCreate = UserCreate(
        name=current_user.name,
        email=current_user.email,
        phone_number=current_user.phone_number,
        password="NEWPASSWORD",
        role=current_user.role,
        address="NEWADDRESS"
    )
    
    user_update_response = client.post("/user/update", json=updated_user_data.model_dump(), headers={"Authorization": f"Bearer {login_token}"})

    #   Test if the user address field is updaed
    get_user_response = client.get("/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    current_user: User = User(**get_user_response.json())
    assert current_user.address == updated_user_data.address

def test_update_user_with_invalid_location():
    #   Get Current User
    get_user_response = client.get("/auth/me", headers={"Authorization": f"Bearer {login_token}"})
    current_user: User = User(**get_user_response.json())
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
    
    user_update_response = client.post("/user/update", json=updated_user_data_json, headers={"Authorization": f"Bearer {login_token}"})

    assert user_update_response.status_code == invalid_status