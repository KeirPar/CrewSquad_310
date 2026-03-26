from fastapi.testclient import TestClient
from app.main import app
from fastapi import status

client = TestClient(app)

def test_restaurant_lifecycle_and_security():
    """Test registration, successful update, and unauthorized update block."""
    
    #Register and Login as Owner 1
    owner_email = "boss@spicytaco.com"
    password = "SecurePassword123!"
    client.post("/auth/register", json={
        "name": "The Boss", "email": owner_email, "phone_number": "250-000-0000",
        "password": password, "role": "Restaurant Owner", "address": "123 Boss St"
    })
    login_res = client.post("/auth/login", json={"email": owner_email, "password": password})
    token = login_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    #Testing registration, create new restaurant
    reg_res = client.post("/restaurants/register", headers=headers, json={
        "name": "Test Bistro",
        "address": "456 Test Ave",
        "cuisine_type": "Other", #same change
        "phone_number": "250-111-2222",
        "price_tier": 3
    })
    assert reg_res.status_code == status.HTTP_201_CREATED
    restaurant_id = reg_res.json()["id"]

    #Update the phone number
    patch_res = client.patch(
        f"/restaurants/{restaurant_id}",
        headers=headers,
        json={"phone_number": "250-999-9999"}
    )
    assert patch_res.status_code == status.HTTP_200_OK
    assert patch_res.json()["phone_number"] == "250-999-9999"

    #Try to update Restaurant #2 (not yours)
    forbidden_res = client.patch(
        "/restaurants/2",
        headers=headers,
        json={"name": "I don't own this"}
    )
    assert forbidden_res.status_code == status.HTTP_403_FORBIDDEN
    assert "You do not own this restaurant" in forbidden_res.json()["detail"]