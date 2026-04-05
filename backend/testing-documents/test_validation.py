from fastapi import status
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

#made so dont need to restart this each time a function runs
def get_auth_headers():
    """Helper to ensure a user exists and returns valid auth headers."""
    email = "testowner@example.com"
    password = "Password123!"
    
    #Register the user
    client.post("/auth/register", json={
        "name": "Test Owner",
        "email": email,
        "password": password,
        "phone_number": "250-555-0100",
        "role": "Restaurant Owner",
        "address": "123 Test Ave"
    })
    
    #Login to get the token
    login_res = client.post("/auth/login", data={"username": email, "password": password})
    token = login_res.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

#For negative price (price<0)
def test_negative_price_validation():
    """Verify the system rejects menu items with negative prices."""
    headers = get_auth_headers()

    #Try to add an item with a negative price
    response = client.post("/menu/1/add", headers=headers, json={
        "name": "Free Pizza",
        "description": "Too good to be true",
        "price": -10.50, #Make sure this fails
        "category": "Main",
        "image_url": "pizza.jpg",
        "is_available": True,
        "add_ons": []
    })

    #Check that the system blocked it with validation error
    assert response.status_code == 422
    assert "price" in response.json()["detail"][0]["loc"]

#For invalid price (Price >4 or price<1, just choosing to test 4 to make easier)
def test_invalid_price_tier_validation():
    """Verify the system rejects restaurants with price_tier > 4."""
    headers = get_auth_headers()

    #Try to register a restaurant with price_tier 5
    response = client.post("/restaurants/register", headers=headers, json={
        "name": "Gold Leaf Kitchen",
        "address": "123 Rich St",
        "cuisine_type": "Italian",
        "phone_number": "555-0000",
        "price_tier": 5 #This should fail (max is 4)
    })

    assert response.status_code == 422

#For invalid cuisine item trying to be added (Not one in enum list on restaurant.py )
def test_invalid_cuisine_enum_validation():
    """Verify the system rejects cuisines not in the Enum list."""
    headers = get_auth_headers()

    response = client.post("/restaurants/register", headers=headers, json={
        "name": "Evil Eater",
        "address": "1234 Fake Address",
        "cuisine_type": "Humans", #This should fail (not in Enum)
        "phone_number": "000-0000",
        "price_tier": 2
    })

    assert response.status_code == 422

def test_referential_integrity_cascade():
    """Verify that deleting a restaurant also wipes its menu items."""
    headers = get_auth_headers()

    #Register a new restaurant
    reg_res = client.post("/restaurants/register", headers=headers, json={
        "name": "Cool Eatery",
        "address": "789 asdfasdf Way",
        "cuisine_type": "Italian",
        "phone_number": "250-555-4444",
        "price_tier": 2
    })
    restaurant_id = reg_res.json()["id"]

    #Add an item to that restaurant's menu
    client.post(f"/menu/{restaurant_id}/add", headers=headers, json={
        "name": "Fettucini Alfredo",
        "description": "Will disappear soon",
        "price": 15.00,
        "category": "Main",
        "image_url": "pasta.jpg",
        "is_available": True,
        "add_ons": []
    })

    #Try deleting the restaurant
    del_res = client.delete(f"/restaurants/{restaurant_id}", headers=headers)
    assert del_res.status_code == status.HTTP_204_NO_CONTENT

    #Verify the menu is gone should get a 404
    menu_res = client.get(f"/menu/{restaurant_id}")
    assert menu_res.status_code == status.HTTP_404_NOT_FOUND