from fastapi.testclient import TestClient
from app.main import app

#Creates a fake browser that can talk to the API
client = TestClient(app)

def test_register_user_success():
    """Test that a new user can register successfully."""
    response = client.post(
        "/auth/register",
        json={
            "name": "Test Customer",
            "email": "new_user@example.com",
            "phone_number": "604-9722",
            "password": "BrandenSkoupas123!",
            "role": "Customer",
            "address": "123 Kelowna Way"
        }
    )
    
    #We should get a HTTP 201 Created status code
    assert response.status_code == 201
    #We should have the database returning our email
    assert response.json()["email"] == "new_user@example.com"
    #We should get the database returning our address
    assert response.json()["address"] == "123 Kelowna Way"
    #We should get the database generating an id
    assert "id" in response.json()

def test_register_duplicate_email():
    """Test that the system stops someone trying to use an existing email."""
    #Because we just registered the email once it should now fail if try again 
    response = client.post(
        "/auth/register",
        json={
            "name": "Evil Customer",
            "email": "new_user@example.com", 
            "phone_number": "604-9722",
            "password": "BrandenSkoupas123!",
            "role": "Restaurant Owner",
            "address": "456 Fake Street"
        }
    )
    
    #We should get the HTTP 400 Bad Request status code
    assert response.status_code == 400
    #We should get the exact error detail message in auth_router
    assert response.json()["detail"] == "Email has already been registered"

def test_login_success():
    """Test that a registered user can log in and gets a JWT."""
    #Example with new user
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

    #Trying login
    response = client.post(
        "/auth/login",
        json={"email": email, "password": password}
    )
    #Assertions
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_get_me_success():
    """Test the profile endpoint"""
    email = "me_test@example.com"
    password = "Password123!"
    address = "123 Test Lane"
    
    #Register
    client.post("/auth/register", json={
        "name": "Me Tester", "email": email, "phone_number": "604-0000",
        "password": password, "role": "Customer", "address": address
    })
    #Login
    login_res = client.post("/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    
    #Get /me
    response = client.get("/auth/me", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 200
    assert response.json()["email"] == email
    assert response.json()["address"] == address



def test_menu_add_forbidden_for_customer():
    """Test that a Customer is blocked from adding menu items (403)."""
    #Register and Login as Customer
    email = "customer@test.com"
    password = "Password123!"
    client.post("/auth/register", json={
        "name": "Customer User", "email": email, "phone_number": "604-9722",
        "password": password, "role": "Customer", "address": "111 Brookside Way"
    })
    login_res = client.post("/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]

    #Try to access owner route
    response = client.post("/menu/1/add", headers={"Authorization": f"Bearer {token}"})
    
    assert response.status_code == 403
    assert "Access denied" in response.json()["detail"]

def test_menu_add_allowed_for_owner():
    """Test that a Restaurant Owner can successfully add menu items (200)."""
    #Register and Login as Restaurant Owner
    email = "owner@test.com"
    password = "Password123!"
    client.post("/auth/register", json={
        "name": "Owner User", "email": email, "phone_number": "604-9722",
        "password": password, "role": "Restaurant Owner", "address": "333 branden street"
    })
    login_res = client.post("/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]

    rest_response = client.post( #make a fake restaurant so we have a valid restaurant id to add menu items to
        "/restaurants/register", 
        headers={"Authorization": f"Bearer {token}"},
        json={
            "name": "Taco Stand", 
            "address": "123 Taco St", 
            "phone_number": "555-1234",
            "cuisine_type": "Mexican",
            "price_tier": 1
        }
    )

    assert rest_response.status_code == 201, rest_response.json() #Created status code means it worked and we created the item

    new_rest_id = rest_response.json()["id"] #get id of restaurant

    #Access owner only route
    response = client.post(f"/menu/{new_rest_id}/add", headers={"Authorization": f"Bearer {token}"},  #was causing error with test
                           json = {"name": "Test Item",
                                   "description": "A delicious test item",
                                   "price": 9.99,
                                   "category": "Test Category",
                                    "image_url": "http://example.com/test_item.jpg"
                                   }) 
    
    assert response.status_code == 201, rest_response.json() #Created status code means it worked and we created the item

    response_data = response.json()
    assert response_data["name"] == "Test Item" #make sure the item we added is the one we get back
    assert response_data["price"] == 9.99
    assert response_data["category"] == "Test Category"


def test_dashboard_and_cart_flow():
    """Verify that a user can add items to a cart and see them on their personal dashboard"""
    email = "us2_tester@example.com"
    password = "Password123!"
    
    #Register and Login
    client.post("/auth/register", json={
        "name": "US2 User", "email": email, "phone_number": "555-0000",
        "password": password, "role": "Customer", "address": "123 Dashboard St"
    })
    login_res = client.post("/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #Add an item to the cart (test id = 99)
    client.post("/cart/add/99", headers=headers)

    #Check the dashboard to see if item in cart
    dash_res = client.get("/auth/dashboard", headers=headers)
    assert dash_res.status_code == 200
    assert dash_res.json()["stats"]["items_in_cart"] == 1
    assert "Welcome back" in dash_res.json()["message"]

    #Check the Cart endpoint
    cart_res = client.get("/cart", headers=headers)
    assert 99 in cart_res.json()["cart_items"]