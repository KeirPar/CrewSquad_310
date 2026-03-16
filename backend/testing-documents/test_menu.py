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
        "cuisine_type": "Testing",
        "phone_number": "250-555-1111",
        "price_tier": 2
    })
    restaurant_id = res_reg.json()["id"]

    #Add item: taco
    res1 = client.post(f"/menu/{restaurant_id}/add", headers=headers, json={
        "name": "Chorizo Taco", "description": "Spicy", "price": 4.5,
        "image_url": "taco.jpg", "is_available": True, "add_ons": []
    })
    assert res1.status_code == 201
    assert res1.json()["id"] == 1

    #Add item: burrito
    res2 = client.post(f"/menu/{restaurant_id}/add", headers=headers, json={
        "name": "Big Burrito", "description": "Huge", "price": 12.0,
        "image_url": "burrito.jpg", "is_available": True, "add_ons": []
    })
    
    #Assertions
    assert res2.status_code == 201
    assert res2.json()["id"] == 2  # This proves the +1 logic works
    assert res2.json()["name"] == "Big Burrito"