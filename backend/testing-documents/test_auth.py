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
            "role": "Customer"
        }
    )
    
    #We should get a HTTP 201 Created status code
    assert response.status_code == 201
    #We should have the database returning our email
    assert response.json()["email"] == "new_user@example.com"
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
            "role": "Restaurant Owner"
        }
    )
    
    #We should get the HTTP 400 Bad Request status code
    assert response.status_code == 400
    #We should get the exact error detail message in auth_router
    assert response.json()["detail"] == "Email has already been registered"