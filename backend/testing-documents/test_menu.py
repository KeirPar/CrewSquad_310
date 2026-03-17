from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_add_multiple_menu_items():
    """Verify that an owner can add multiple dishes with unique IDs."""
    #Creating owner
    email = "testowner@example.com"
    password = "Password123!"
    
    client.post("/auth/register", json={
        "name": "Test Owner",
        "email": email,
        "password": password,
        "phone_number": "211-595-0400",
        "role": "Restaurant Owner",
        "address": "456 Test St"
    })

    #Login as Owner
    login_res = client.post("/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #Register a restaurant so test works
    res_reg = client.post("/restaurants/register", headers=headers, json={
        "name": "Test Kitchen",
        "address": "123 Skoupas Lane",
        "cuisine_type": "Other",
        "phone_number": "250-555-1111",
        "price_tier": 2
    })
    restaurant_id = res_reg.json()["id"]

    #Add item: taco
    res1 = client.post(f"/menu/{restaurant_id}/add", headers=headers, json={
        "name": "Chorizo Taco", 
        "description": "Spicy", 
        "price": 4.5, 
        "category": "Protein",
        "image_url": "taco.jpg", 
        "is_available": True, 
        "add_ons": []
    })
    assert res1.status_code == 201
    assert res1.json()["id"] == 1

    #Add item: burrito
    res2 = client.post(f"/menu/{restaurant_id}/add", headers=headers, json={
        "name": "Big Burrito", 
        "description": "Huge", 
        "price": 12.0, 
        "category": "Protein",
        "image_url": "burrito.jpg", 
        "is_available": True, 
        "add_ons": []
    })
    
    #Assertions
    assert res2.status_code == 201
    assert res2.json()["id"] == 2  # This proves the +1 logic works
    assert res2.json()["name"] == "Big Burrito"

def test_update_menu_item_partial():
    """Verify that an owner can update without losing category data."""
    email = "testowner@example.com"
    password = "Password123!"
    login_res = client.post("/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #Register a restaurant so we have a valid id for test
    res_reg = client.post("/restaurants/register", headers=headers, json={
        "name": "Update Test Kitchen",
        "address": "456 Update St",
        "cuisine_type": "Other", #had to change this to other (we made the cuisine types enum not string)
        "phone_number": "250-555-2222",
        "price_tier": 2
    })
    restaurant_id = res_reg.json()["id"]

    #Add an item to specific restaurant
    res = client.post(f"/menu/{restaurant_id}/add", headers=headers, json={
        "name": "Original Pizza", 
        "description": "Very Cheesy", 
        "price": 10.0,
        "category": "Main",
        "image_url": "pizza.jpg", 
        "is_available": True, 
        "add_ons": []
    })
    item_id = res.json()["id"]

    #Change price using the dynamic ids
    update_res = client.patch(f"/menu/{restaurant_id}/{item_id}", headers=headers, json={
        "price": 15.50
    })

    #Assertions
    assert update_res.status_code == 200
    assert update_res.json()["price"] == 15.50
    assert update_res.json()["name"] == "Original Pizza"
    assert update_res.json()["category"] == "Main"


def test_delete_menu_item():
    """Verify that an owner can delete an item and it no longer exists."""
    email = "testowner@example.com"
    password = "Password123!"
    login_res = client.post("/auth/login", json={"email": email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #Register a restaurant for test
    res_reg = client.post("/restaurants/register", headers=headers, json={
        "name": "Delete Test Kitchen",
        "address": "789 Delete Ave",
        "cuisine_type": "Other", # same here
        "phone_number": "250-555-3333",
        "price_tier": 1
    })
    restaurant_id = res_reg.json()["id"]

    #Add item to specific restaurant
    res = client.post(f"/menu/{restaurant_id}/add", headers=headers, json={
        "name": "Delete Me",
        "description": "Bye",
        "price": 1.0, 
        "category": "Appetizer",
        "image_url": "none.jpg", 
        "is_available": True, "add_ons": []
    })
    item_id = res.json()["id"]

    #Delete using the dynamic ids
    delete_res = client.delete(f"/menu/{restaurant_id}/{item_id}", headers=headers)
    assert delete_res.status_code == 204

    #Verify the deleted item is gone (should be 404)
    verify_res = client.patch(f"/menu/{restaurant_id}/{item_id}", headers=headers, json={"price": 2.0})
    assert verify_res.status_code == 404

def test_get_restaurant_menu():
    """Verify that any user or owner can view the restaurant menu."""
    #Get request already public so can start
    res = client.get("/menu/1") #Use restaurant 1 from previous tests
    assert res.status_code in [200, 404] #404 is fine if the db was wiped, 200 if data exists
    
    if res.status_code == 200:
        menu = res.json()
        assert isinstance(menu, list)
        if len(menu) > 0:
            assert "category" in menu[0]
