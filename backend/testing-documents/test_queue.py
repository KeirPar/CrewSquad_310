import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.schemas.order import Order, OrderStatus

client = TestClient(app)

#Integration tests to creat a register a new user, log them in
#and then check if they can access the pending orders queue, and if the queue only shows pending orders
#have to be a restaurant manager to access the queue


def test_queue_access_forbidden_for_customers():
    customer_email = "thingy@customer.com"
    password = "Password123!"
    client.post("/auth/register", json={ #register fake user
        "name": "Snoopy Customer", "email": customer_email, "phone_number": "604-676-6767",
        "password": password, "role": "Customer", "address": "111 Fake St"
    })
    login_res = client.post("/auth/login", json={"email": customer_email, "password": password}) #log them in
    customer_token = login_res.json()["access_token"]
    
    response = client.get(
        "/orders/queue",  #hit endpoint
        headers={"Authorization": f"Bearer {customer_token}"}
    )
    
    assert response.status_code == 403 #make sure we got kicked out bc we are a customer, not manager
    assert "Only restaurant managers" in response.json()["detail"]


def test_manager_can_view_pending_queue():

    manager_email = "boss@kitchen.com"
    password = "Password123!"
    client.post("/auth/register", json={ #fake manager
        "name": "The Kitchen Boss", "email": manager_email, "phone_number": "604-677-6767",
        "password": password, "role": "Restaurant Owner", "address": "456 Kitchen Ave"
    })
    login_res = client.post("/auth/login", json={"email": manager_email, "password": password}) #log them in
    manager_token = login_res.json()["access_token"]
    
    response = client.get(
        "/orders/queue",  #check endpoint
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    assert response.status_code == 200
    data = response.json() #should work
    assert data["message"] == "Kitchen queue retrieved successfully"
    assert type(data["pending_orders"]) == list

def test_queue_filters_out_completed_orders():

    manager_email = "boss@kitchen.com" 
    password = "Password123!"
    client.post("/auth/register", json={ #fake manager
        "name": "The Kitchen Boss", "email": manager_email, "phone_number": "604-677-6767",
        "password": password, "role": "Restaurant Owner", "address": "456 Kitchen Ave"
    })
    login_res = client.post("/auth/login", json={"email": manager_email, "password": password}) #log them in
    manager_token = login_res.json()["access_token"]
    
    response = client.get(
        "/orders/queue",  #check endpoint
        headers={"Authorization": f"Bearer {manager_token}"}
    )
    
    assert response.status_code == 200
    pending_orders = response.json()["pending_orders"]
    
    for order in pending_orders: #looping through the order to make sure all are pending
        assert order["status"] == OrderStatus.PENDING.value